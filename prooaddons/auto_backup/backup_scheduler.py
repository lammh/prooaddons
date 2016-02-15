# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import xmlrpclib
import socket
import os
import time
import base64

from openerp.osv import fields,osv
from openerp import tools
from openerp import netsvc
from openerp import service
import ftplib
from openerp.tools.translate import _
import datetime

#logger = netsvc._Logger()

def execute(connector, method, *args):
    res = False
    try:        
        res = getattr(connector,method)(*args)
    except socket.error,e:        
            raise e
    return res

addons_path = tools.config['addons_path'] + '/auto_backup/DBbackups'

class db_backup(osv.osv):
    _name = 'db.backup'
    
    def get_db_list(self, cr, user, ids, host='localhost', port='8069', context={}):
        uri = 'http://' + host + ':' + port
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = execute(conn, 'list')
        return db_list
        
    _columns = {
        'host' : fields.char('Host', size=100, required='True'),
        'port' : fields.char('Port', size=10, required='True'),
        'name' : fields.char('Database', size=100, required='True',help='Database you want to schedule backups for'),
        'bkp_dir' : fields.char('Backup Directory', size=100, help='Absolute path for storing the backups', required='True'),
        'autoremove': fields.boolean('Auto. Remove Backups', help="If you check this option you can choose to automaticly remove the backup after xx days"),
        'daystokeep': fields.integer('Remove after x days',
                                     help="Choose after how many days the backup should be deleted. For example:\nIf you fill in 5 the backups will be removed after 5 days.",required=True),
        'ftp_enable' : fields.boolean('FTP Enable ?'),
        'ftp_host': fields.char('FTP Host/Server', size=255),
        'ftp_username': fields.char('FTP Username', size=255),
        'ftp_password': fields.char('FTP Password', size=255),
        'ftp_location': fields.char('To Directory',size=255,help="The location must contain a trailing `/`"),
        'daystokeepsftp': fields.integer('Remove SFTP after x days', help="Choose after how many days the backup should be deleted from the FTP server. For example:\nIf you fill in 5 the backups will be removed after 5 days from the FTP server."),
        'sendmailsftpfail': fields.boolean('Auto. E-mail on backup fail', help="If you check this option you can choose to automaticly get e-mailed when the backup to the external server failed."),
        'emailtonotify': fields.char('E-mail to notify', help="Fill in the e-mail where you want to be notified that the backup failed on the FTP."),
                }
    
    _defaults = {
        'bkp_dir' : lambda *a : addons_path,
        'host' : lambda *a : 'localhost',
        'port' : lambda *a : '8069',
        'autoremove': True,
        'daystokeep': 30,
        'daystokeepsftp': 30,
    }
    
    def _check_db_exist(self, cr, user, ids):
        for rec in self.browse(cr,user,ids):
            db_list = self.get_db_list(cr, user, ids, rec.host, rec.port)
            if rec.name in db_list:
                return True
        return False
    
    _constraints = [
                    (_check_db_exist, _('Error ! No such database exists!'), [])
                    ]

    def test_ftplib_connection(self, cr, uid, ids, context=None):
        conf_ids= self.search(cr, uid, [])
        confs = self.browse(cr,uid,conf_ids)
        #Check if there is a success or fail and write messages
        messageTitle = ""
        messageContent = ""
        for rec in confs:
            db_list = self.get_db_list(cr, uid, [], rec.host, rec.port)
            try:
                #Connect with external server over SFTP, so we know sure that everything works.
                srv = ftplib.FTP(rec.ftp_host,rec.ftp_username,rec.ftp_password)
                srv.close()
                #We have a success.
                messageTitle = "Connection Test Succeeded!"
                messageContent = "Everything seems properly set up for FTP back-ups!"
            except Exception, e:
                messageTitle = "Connection Test Failed!"
                if len(rec.ftp_host) < 8:
                    messageContent += "\nYour IP address seems to be too short.\n"
                messageContent += "Here is what we got instead:\n"
        if "Failed" in messageTitle:
            raise osv.except_osv(_(messageTitle), _(messageContent + "%s") % tools.ustr(e))
        else:
            raise osv.except_osv(_(messageTitle), _(messageContent))

    def schedule_backup(self, cr, user, context={}):
        conf_ids= self.search(cr, user, [])
        confs = self.browse(cr,user,conf_ids)
        for rec in confs:
            db_list = self.get_db_list(cr, user, [], rec.host, rec.port)
            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.bkp_dir):
                        os.makedirs(rec.bkp_dir)
                except:
                    raise
                bkp_file='%s_%s.dump' % (rec.name, time.strftime('%Y%m%d_%H_%M_%S'))
                file_path = os.path.join(rec.bkp_dir,bkp_file)

                uri = 'http://' + rec.host + ':' + rec.port
                conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
                bkp=''
                try:
                    bkp = execute(conn, 'dump', tools.config['admin_passwd'], rec.name)
                except:
#                    logger.notifyChannel('backup', netsvc.LOG_INFO, "Could'nt backup database %s. Bad database administrator password for server running at http://%s:%s" %(rec.name, rec.host, rec.port))
                    continue
                bkp = base64.decodestring(bkp)
                fp = open(file_path,'wb')
                fp.write(bkp)
                fp.close()
##############################################################################
                if rec.autoremove is True:
                    dir = rec.bkp_dir
                    #Loop over all files in the directory.
                    for f in os.listdir(dir):
                        fullpath = os.path.join(dir, f)
                        timestamp = os.stat(fullpath).st_ctime
                        createtime = datetime.datetime.fromtimestamp(timestamp)
                        now = datetime.datetime.now()
                        delta  = now - createtime
                        if delta.days >= rec.daystokeep:
                        #Only delete files (which are .dump), no directories.
                            if os.path.isfile(fullpath) and ".dump" in f:
                                print("Delete: " + fullpath)
                                os.remove(fullpath)
##############################################################################
                if rec.ftp_enable :
                    tar_file_name = '%s_%s.dump' %(rec.name, time.strftime('%Y%m%d_%H_%M_%S'))
                    tar_file_path = file_path
                    try:
                        s = ftplib.FTP(rec.ftp_host,rec.ftp_username,rec.ftp_password) # Connect
                        f = open(tar_file_path,'rb')                # file to send
                        remote_file_path = os.path.join(rec.ftp_location,tar_file_name)
                        s.storbinary('STOR ' + remote_file_path , f)         # Send the file
                        f.close()                                # Close file and FTP
                        s.quit()
                    except Exception, e:
                        continue
                    for file in s.listdir(rec.ftp_location):
                        #Get the full path
                        fullpath = os.path.join(rec.ftp_location,file)
                        #Get the timestamp from the file on the external server
                        timestamp = s.stat(fullpath).st_atime
                        createtime = datetime.datetime.fromtimestamp(timestamp)
                        now = datetime.datetime.now()
                        delta = now - createtime
                        #If the file is older than the daystokeepsftp (the days to keep that the user filled in on the Odoo form it will be removed.
                        if delta.days >= rec.daystokeepsftp:
                            #Only delete files, no directories!
                            if s.isfile(fullpath) and ".dump" in file:
                                print("Delete: " + file)
                                s.unlink(file)

                    if rec.sendmailsftpfail:
                        try:
                            ir_mail_server = self.pool.get('ir.mail_server')
                            message = "Dear,\n\nThe backup for the server " + rec.host + " (IP: " + rec.sftpip + ") failed.Please check the following details:\n\nIP address SFTP server: " + rec.sftpip + "\nUsername: " + rec.sftpusername + "\nPassword: " + rec.sftppassword + "\n\nError details: " + tools.ustr(e) + "\n\nWith kind regards"
                            msg = ir_mail_server.build_email("auto_backup@" + rec.name + ".com", [rec.emailtonotify], "Backup from " + rec.host + "(" + rec.sftpip + ") failed", message)
                            ir_mail_server.send_email(cr, user, msg)
                        except Exception:
                            pass
##############################################################################
#            else:
#                logger.notifyChannel('backup', netsvc.LOG_INFO, "database %s doesn't exist on http://%s:%s" %(rec.name, rec.host, rec.port))

db_backup()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
