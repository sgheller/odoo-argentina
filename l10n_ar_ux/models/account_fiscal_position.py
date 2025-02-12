# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, api
from odoo.addons.l10n_ar.models.account_fiscal_position import AccountFiscalPosition


@api.model
def _get_fiscal_position(self, partner, delivery=None):
    company = self.env.company
    if company.country_id.code == "AR":
        self = self.with_context(
            company_code='AR',
            l10n_ar_afip_responsibility_type_id=partner.l10n_ar_afip_responsibility_type_id.id)
    return super(AccountFiscalPosition, self)._get_fiscal_position(partner, delivery=delivery)


AccountFiscalPosition._get_fiscal_position = _get_fiscal_position


class AccountFiscalPositionMp(models.Model):

    _inherit = 'account.fiscal.position'

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
        """ Take into account the partner afip responsibility in order to auto-detect the fiscal position """
        if self._context.get('company_code') == 'AR':
            domain += [('l10n_ar_afip_responsibility_type_ids', '=', self._context.get('l10n_ar_afip_responsibility_type_id'))]
        return super()._search(domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)

    def _onchange_afip_responsibility(self):
        return {}

    @api.model
    def _get_fpos_by_region(self, country_id=False, state_id=False, zipcode=False, vat_required=False):
        if country_id and 'website_id' in self._context and 'l10n_ar_afip_responsibility_type_id' not in self._context:
            company = self.env['res.company'].browse(self._context.get('force_company', self.env.company.id))
            if company.country_id.code == 'AR':
                self = self.with_context(company_code='AR')
        # odoo only match fiscal positions if partner has a country, we've many customers with partners with country_id = False
        # so, for ARG, if no country is configured we use Argentina for the fiscal autodetection
        if not country_id and 'l10n_ar_afip_responsibility_type_id' in self._context:
            country_id = self.env.ref('base.ar').id
        return super()._get_fpos_by_region(country_id=country_id, state_id=state_id, zipcode=zipcode, vat_required=vat_required)
