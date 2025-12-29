# from odoo import models, fields, api
# from odoo.api import ondelete
#
#
# class WorkArea(models.Model):
#     _name = "work.area"
#     _description = "Área de trabajo"
#
#     name = fields.Char(string="Nombre del area", required=True)
#     work_area_id = fields.Many2one(comodel_name='hr.work.location',
#                                      string="Centro de Trabajo",
#                                    ondelete='cascade')
#
#     # _sql_constraints = [
#     #     ('name_unique', 'unique (work_center_id, name)', 'Esta área de trabajo ya existe en este centro')
#     # ]