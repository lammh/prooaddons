# -*- coding: utf-8 -*-

from openerp.osv import osv, orm, fields
from openerp import models, api

# -------------------------------------------------------------------------
# Auteur: Bejaoui Souheil, Date:25-08-2015
# -------------------------------------------------------------------------

TYPE2FIELD = {
    'char': 'value_text',
    'float': 'value_float',
    'boolean': 'value_integer',
    'integer': 'value_integer',
    'text': 'value_text',
    'binary': 'value_binary',
    'many2one': 'value_reference',
    'date': 'value_datetime',
    'datetime': 'value_datetime',
    'selection': 'value_text',
}

class ir_property(osv.osv):
    _inherit = 'ir.property'

    #On intercepte le mise à jour ou la création
    #Le but est de mettre le champ company_id = null pour le modèle product.pricelict
    def _update_values(self, cr, uid, ids, values):
        value = values.pop('value', None)
        if not value:
            return values

        prop = None
        type_ = values.get('type')
        if not type_:
            if ids:
                prop = self.browse(cr, uid, ids[0])
                type_ = prop.type
            else:
                type_ = self._defaults['type']

        field = TYPE2FIELD.get(type_)
        if not field:
            raise osv.except_osv('Error', 'Invalid type')

        if field == 'value_reference':
            if isinstance(value, orm.BaseModel):
                value = '%s,%d' % (value._name, value.id)
            elif isinstance(value, (int, long)):
                field_id = values.get('fields_id')
                if not field_id:
                    if not prop:
                        raise ValueError()
                    field_id = prop.fields_id
                else:
                    field_id = self.pool.get('ir.model.fields').browse(cr, uid, field_id)

                value = '%s,%d' % (field_id.relation, value)
                #Ici on fait le test sur le modèle
                #on met le cmpany_id à false pour résoudre le problème de unknown catégorie de parent
                if field_id.relation == 'product.pricelist':
                    values['company_id'] = False
        values[field] = value

        return values
    @api.model
    def set_multi(self, name, model, values):
        """ Assign the property field `name` for the records of model `model`
            with `values` (dictionary mapping record ids to their value).
        """
        def clean(value):
            return value.id if isinstance(value, models.BaseModel) else value

        if not values:
            return

        domain = self._get_domain(name, model)
        if domain is None:
            raise Exception()

        # retrieve the default value for the field
        default_value = clean(self.get(name, model))

        # retrieve the properties corresponding to the given record ids
        self._cr.execute("SELECT id FROM ir_model_fields WHERE name=%s AND model=%s", (name, model))
        field_id = self._cr.fetchone()[0]
        company_id = self.env['res.company']._company_default_get(model, field_id)
        refs = {('%s,%s' % (model, id)): id for id in values}

        if name == 'property_product_pricelist':
            props = self.search([
                ('fields_id', '=', field_id),
                #('company_id', '=', company_id),
                ('res_id', 'in', list(refs)),
            ])
            # si la prop est défini plus q'une fois
            # on parcour le resultat et on laisse q'une seule prop
            #tous les autres seront supprimées
            if len(props) > 1:
                i = 0
                for prop in props:
                    i+=1
                    if i < len(props):
                        prop.unlink()
                    elif i == len(props):
                        props = prop

        else:
            props = self.search([
                ('fields_id', '=', field_id),
                ('company_id', '=', company_id),
                ('res_id', 'in', list(refs)),
            ])

        # modify existing properties
        for prop in props:
            id = refs.pop(prop.res_id)
            value = clean(values[id])
            if value == default_value:
                prop.unlink()
            elif value != clean(prop.get_by_record(prop)):
                prop.write({'value': value})

        # create new properties for records that do not have one yet
        for ref, id in refs.iteritems():
            value = clean(values[id])
            if value != default_value:
                self.create({
                    'fields_id': field_id,
                    'company_id': company_id,
                    'res_id': ref,
                    'name': name,
                    'value': value,
                    'type': self.env[model]._fields[name].type,
                })
