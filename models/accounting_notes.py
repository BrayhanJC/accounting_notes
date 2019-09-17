# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    Autor: Brayhan Andres Jaramillo Castaño
#    Correo: brayhanjaramillo@hotmail.com
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from odoo import api, fields, models, _
import time
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)
from odoo import modules
from odoo.addons import decimal_precision as dp

class AccountingNotes(models.TransientModel):

	_name = "accounting.notes"
	_description = 'Accounting Notes'

	date_begin = fields.Datetime(string= 'Start time')
	date_end = fields.Datetime(string= 'End time', required=True)	
	acount_origin_debit = fields.Many2one('account.account', string="Account Origin Debit")
	acount_origin_credit = fields.Many2one('account.account', string="Account Origin Credit")
	acount_destination_debit = fields.Many2one('account.account', string="Account Destination Debit")
	acount_destination_credit = fields.Many2one('account.account', string="Account Destination Credit")


	def return_accounting(self):
		domain= []

		if self.date_begin and self.date_end:

			domain.append( [('date', '>=', self.date_begin), ('date', '<=', self.date_end)] )

		elif self.date_end and not self.date_begin:

			domain = [('date', '<=', self.date_end)]

		account_move_line_ids = self.env['account.move.line'].search(domain)

		data = [x.account_id.id for x in account_move_line_ids]

		return data


	@api.onchange('date_begin', 'date_end')
	def onchange_date_end(self):

		data = self.return_accounting()
		
		self.acount_origin_debit = data

		res = {}

		res['domain'] = {'acount_origin_debit': [('id', 'in', data)], 'acount_origin_credit': [('id', 'in', data)]}
			
		return res


	def search_update_account(self, account_move_line_model, account_move_model, account_origin, account_destination):

		domain = [('account_id', '=', account_origin)]

		account_move_line_ids = account_move_line_model.search(domain)

		vals = {'account_id': account_destination}

		#Actualizando apuntes contables
		for x in account_move_line_ids:
			x.write(vals)


		#Actualizando asientos contables
		account_move_ids = account_move_model.search([])

		for x in account_move_ids:
			if x.state == 'draft':
				if x.line_ids:
					for account in x.line_ids:
						if account.account_id == account_origin:
							account.write(vals)


	@api.multi
	def update_accounting_notes(self):

		account_move_line_model = self.env['account.move.line']
		account_move_model = self.env['account.move']

		if self.acount_origin_debit and self.acount_destination_debit:

			self.search_update_account(account_move_line_model, account_move_model, self.acount_origin_debit.id, self.acount_destination_debit.id)

		if self.acount_origin_credit and self.acount_destination_credit:

			self.search_update_account(account_move_line_model, account_move_model, self.acount_origin_credit.id, self.acount_destination_credit.id)


AccountingNotes()