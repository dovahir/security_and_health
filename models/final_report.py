from odoo import models, fields, _, api
from odoo.exceptions import UserError
import datetime
from datetime import date, timedelta

class FinalReport(models.Model):
    _name = 'final.report'
    _description = 'Reporte final'
    _rec_name = 'security_situation_id'

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
    investigator = fields.Char(string="Investigador")
    medic_diagnostic = fields.Char(string='Diagnóstico')
    attention_type = fields.Selection([
        ('na', 'N/A'),
        ('private','Privada'),
        ('public','Pública'),
    ], string="Tipo de atención")
    given_days = fields.Integer(string='Días de incapacidad', default='0')
    work_risk = fields.Selection([
        ('no_risk','No de trabajo'),
        ('yes_risk','Sí de trabajo')
    ], string="Riesgo de trabajo")
    actual_laboral_state = fields.Selection([
        ('normal','Actividades normales'),
        ('not_normal','Actividades parciales'),
        ('out', 'Actividades nulas'),
    ], string="Estado laboral actual")
    return_activities_date = fields.Date(string="Fecha de regreso a actividades normales",
                                         compute='_compute_return_activities_date',
                                         help="Basado en la fecha de creación de la situacion y los dias de incapacidad del empleado")
    supervisor_ssma = fields.Many2one('hr.employee',
                                      string="Supervisor SSMA",
                                      ondelete='cascade',
                                      tracking=True,
                                      default=lambda self: self.env.user.employee_id,
                                      required=True )
    medical_treatment = fields.Char(string="Tratamiento médico")
    initial_attention = fields.Boolean(string="¿Hubo atención medica inicial?")
    corrective_actions = fields.Text(string="Acciones correctivas")
    lessons_learned = fields.Text(string="Lecciones aprendidas")
    final_summary = fields.Text(string="Comentarios finales")

    return_date_warning = fields.Char(
        string="Aviso de Regreso",
        compute="_compute_return_date_warning"
    )

    @api.depends('return_activities_date')
    def _compute_return_date_warning(self):
        today = date.today()
        seven_days_later = today + timedelta(days=7)

        for record in self:
            warning = False
            return_date = record.return_activities_date

            if not return_date:
                record.return_date_warning = False
                continue
            if return_date == today:
                warning = "¡ATENCIÓN! El empleado debe regresar hoy."
            elif today < return_date <= seven_days_later:
                remaining_days = (return_date - today).days
                warning = f"AVISO: El empleado regresa en {remaining_days} días ({return_date.strftime('%d-%m-%Y')})."
            elif return_date < today:
                warning = "NOTA: La fecha de regreso ya pasó. Verifique el estado laboral."
            else:  # Fecha lejana
                warning = f"La fecha de regreso está programada para {return_date.strftime('%d-%m-%Y')}."

            record.return_date_warning = warning

    # @api.constrains('given_days', 'return_activities_date')
    # def _checkr_return_activities_date(self):
    #     for record in self:
    #         if record.return_activities_date < fields.Date.today():
    #             raise UserError("No puedes registrar una fecha pasada.")
    #
    #         if record.given_days < 0:
    #             raise UserError(_("Revisar valor de días"))

    @api.depends('return_activities_date', 'given_days', 'security_situation_id.event_date')
    def _compute_return_activities_date(self):
        for date in self:
            init_date = date.security_situation_id.event_date
            incapacity_days = datetime.timedelta(days=date.given_days)
            newDate = init_date + incapacity_days

            date.return_activities_date = newDate

    @api.constrains('given_days')
    def _check_given_days(self):
        for record in self:
            if record.given_days < 0:
                raise UserError(_("Revisar días de incapacidad (No puede ser negativo)"))