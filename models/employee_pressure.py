from odoo import models, fields, api
from odoo.exceptions import UserError

class EmployeePressure(models.Model):
    _name ='employee.pressure'
    _description = 'Registro de Presión Arterial'
    _rec_name = 'employee_id'
    _order = 'record_date desc'

    # Campos del formulario
    employee_id = fields.Many2one('hr.employee',
                                  string='Nombre de empleado',
                                  ondelete='cascade',
                                  required=True)
    record_date = fields.Date(string='Fecha', required=True, default=fields.Date.today)
    blood_pressure_systolic = fields.Integer(string='Sistólica (mmHg)', required=True)
    blood_pressure_diastolic = fields.Integer(string='Diastólica (mmHg)', required=True)

    # Validación de valores de presión
    @api.constrains('blood_pressure_systolic', 'blood_pressure_diastolic')
    def _check_pressure_values(self):
        for record in self:
            if record.blood_pressure_systolic <= 75 or record.blood_pressure_diastolic <= 50 or record.blood_pressure_systolic > 200 or record.blood_pressure_diastolic > 140:
                raise UserError("Valores de presión fuera del rango")

    # Validación de fecha futura
    @api.constrains('record_date')
    def _check_record_date(self):
        for record in self:
            if record.record_date > fields.Date.today():
                raise UserError("No puedes registrar una toma de presión con fecha futura.")