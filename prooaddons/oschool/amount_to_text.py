# -*- coding: utf-8 -*-


to_19_fr = ( u'Zéro',  'Un',    'Deux',   'Trois',    'Quatre', 'Cinq',  'Six',      'Sept',     'Huit',    'Neuf', 'Dix',
            'Onze',   'Douze', 'Treize', 'Quatorze', 'Quinze', 'Seize', 'Dix-Sept', 'Dix-Huit', 'Dix-Neuf' )
tens_fr  = ( 'Vingt', 'Trente', 'Quarante', 'Cinquante', 'Soixante', 'Soixante', 'Quatre-Vingt', 'Quatre-Vingt')
denom_fr = ( '',
          'Mille',        'Millions',        'Milliards',     'Billions',       'Quadrillions',
          'Quintillion',  'Sextillion',      'Septillion',    'Octillion',      'Nonillion',
          'Décillion',    'Undecillion',     'Duodecillion',  'Tredecillion',   'Quattuordecillion',
          'Sexdecillion', 'Septendecillion', 'Octodecillion', 'Icosillion',     'Vigintillion' )


def _convert_nn_fr(val):
    """ convert a value < 100 to French
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if val > 60:
                if val % 20 >= 10:
                    return dcap + '-' + to_19_fr[val % 20]
                return dcap + '-' + to_19_fr[val % 10]
            if val % 10:
                return dcap + '-' + to_19_fr[val % 10]
            return dcap


def _convert_nnn_fr(val):
    """ convert a value < 1000 to french

        special cased because it is the level that kicks
        off the < 100 special case.  The rest are more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if rem == 1:
            word = 'Cent'
        word = to_19_fr[rem] + ' Cents'
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_fr(mod)
    return word


def french_number(val):
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
         return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            ret = _convert_nnn_fr(l) + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ' ' + french_number(r)
            return ret


def amount_to_text_tn(number, currency_id):

     units_name = currency_id[0].name
     if currency_id[0].name.upper() == 'EUR':
         units_name = 'Euro'
     elif currency_id[0].name.upper() == 'USD':
         units_name = 'Dollars'
     elif currency_id[0].name.upper() == 'BRL':
         units_name = 'reais'
     elif currency_id[0].name.upper() == 'TND':
         units_name = 'Dinars'
     else:
         units_name = currency_id[0].name

     number = '%.2f' % number

     list = str(number).split('.')
     start_word = french_number(abs(int(list[0])))
     end_word = french_number(int(list[1]))
     cents_number = int(list[1])
     cents_name = (cents_number > 1) and 'Millimes' or 'Millime'
     final_result = start_word + ' ' + units_name + ' ' + end_word + ' ' + cents_name
     return final_result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: