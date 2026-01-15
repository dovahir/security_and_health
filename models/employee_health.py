from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EmployeeHealth(models.Model):
    _name ='employee.health'
    _description = 'Registro de salud general del empleado'
    _order = 'record_date desc'
    _rec_name = 'employee_id'

    record_date = fields.Datetime(string='Fecha y Hora de Registro', required=True, default=fields.Datetime.now)
    employee_id = fields.Many2one('hr.employee', string='Nombre de empleado', ondelete='cascade', required=True)
    department_id = fields.Many2one(comodel_name='hr.department',
                                    related='employee_id.department_id',
                                    string="Departamento",
                                    store=True,
                                    readonly=True)
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ], string='Tipo de sangre')
    height = fields.Float(string='Estatura (cm)', digits=(3, 0))
    weight = fields.Float(string='Peso (kg)', digits=(5, 2))
    imc = fields.Float(string='IMC', compute='_compute_imc', store=True, digits=(4, 2))
    notes = fields.Text(string='Notas médicas')

    #Validar si la altura o peso es valida
    @api.constrains('height', 'weight')
    def _check_values(self):
        for record in self:
            if record.height < 130 or record.height > 240:
                raise UserError(_("Revisar altura"))

            if record.weight < 30 or record.weight > 300:
                raise UserError(_("Revisar peso"))

    @api.depends('height', 'weight')
    def _compute_imc(self):
        for record in self:
            if record.height > 0 and record.weight > 0:
                height_in_meters = record.height / 100.0
                record.imc = record.weight / (height_in_meters ** 2)
            else:
                record.imc = 0.0

    # # Validación de fecha pasada
    # @api.constrains('record_date')
    # def _check_record_date(self):
    #     for record in self:
    #         if record.record_date < fields.Date.today():
    #             raise UserError("No puedes hacer un registro con fechas pasadas")