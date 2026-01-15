from odoo import models, fields, api
from odoo.exceptions import UserError

class EmployeePressure(models.Model):
    _name ='employee.pressure'
    _description = 'Registro de presión arterial'
    _rec_name = 'employee_id'
    _order = 'record_date desc'

    # Campos del formulario
    employee_id = fields.Many2one('hr.employee',
                                  string='Nombre de empleado',
                                  ondelete='cascade',
                                  required=True)

    department_id = fields.Many2one(comodel_name='hr.department',
                                    related='employee_id.department_id',
                                    string="Departamento",
                                    store=True,
                                    readonly=True)

    record_date = fields.Datetime(string='Fecha y Hora', required=True, default=fields.Datetime.now)
    ta_systolic = fields.Integer(string='Sistólica (mmHg)', required=True)
    ta_diastolic = fields.Integer(string='Diastólica (mmHg)', required=True)
    fc = fields.Integer(string='Frecuencia Cardiaca', required=True)
    observations = fields.Text(string='Observaciones')

    # Validación de valores de presión
    @api.constrains('ta_systolic', 'ta_diastolic')
    def _check_pressure_values(self):
        for record in self:
            if record.ta_systolic <= 70 or record.ta_diastolic <= 45 or record.ta_systolic > 250 or record.ta_diastolic > 160:
                raise UserError("Valores de presión inválidos")

    # Validación de fecha futura
    # @api.constrains('record_date')
    # def _check_record_date(self):
    #     for record in self:
    #         if record.record_date > fields.Date.today():
    #             raise UserError("No puedes registrar una toma de presión con fecha futura.")

class EmployeePressureLine(models.Model):
    _name = 'employee.pressure.line'
    _description = 'New Model Description'
    _order = 'id desc'

