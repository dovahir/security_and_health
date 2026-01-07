from odoo import models, fields, _, api
from odoo.exceptions import UserError
import datetime
from datetime import date, timedelta

class FinalReport(models.Model):
    _name = 'final.report'
    _description = 'Reporte final'
    _rec_name = 'security_situation_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Conectar con situación de seguridad
    security_situation_id = fields.Many2one('security.situation',
                                            string="Situación de Seguridad",
                                            ondelete="cascade",
                                            required=True)

    final_report_employee_id = fields.Many2one(
        related='security_situation_id.employee_id',
        string='Empleado de la Situación',
        readonly=True,
        store=True  # Recomendado para que sea buscable y filtrable en la lista
    )

    # Campos a mostrar en el formulario
    corrective_actions = fields.Text(string="Acciones Correctivas", tracking=True)
    lessons_learned = fields.Text(string="Lecciones Aprendidas", tracking=True)
    final_summary = fields.Text(string="Comentarios Finales", tracking=True)

    return_date_warning = fields.Char(
        string="Aviso de Regreso",
        compute="_compute_return_date_warning"
    )

