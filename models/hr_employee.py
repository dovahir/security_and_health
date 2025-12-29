from odoo import models, fields, api
from odoo.tools import float_round

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    # Declaro un campo que se usará para el contador y otro para que actue como string
    # que será el mostrado en el decoration(views)
    incident_count = fields.Integer(string="Incidentes", compute='_compute_security_counts', store=True)
    incident_count_string = fields.Char(string="Incidentes_String")

    accident_count = fields.Integer(string="Accidentes", compute='_compute_security_counts', store=True)
    accident_count_string = fields.Char(string="Accidentes_String")

    quasi_accident_count = fields.Integer(string="Cuasi Accidentes", compute='_compute_security_counts', store=True)
    quasi_accident_count_string = fields.Char(string="Cuasi Accidentes_String")

    # Estos campos son para resumen del último estado de salud general
    health_record_ids = fields.One2many('employee.health', 'employee_id', string='Registros de Salud')
    last_height = fields.Float(string='Estatura (cm)', compute='_compute_last_health_data', store=True, digits=(3, 0))
    last_weight = fields.Float(string='Peso (kg)', compute='_compute_last_health_data', store=True, digits=(5, 2))
    last_imc = fields.Float(string='IMC', compute='_compute_last_health_data', store=True, digits=(4, 2))
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ], string='Tipo de Sangre', compute='_compute_last_health_data', store=True)

    # Otros campos que se mostraran
    last_accident_date = fields.Datetime(string="Último accidente", compute='_compute_security_counts', store=True)
    pressure_daily_ids = fields.One2many('employee.pressure', 'employee_id', string='Registros de Presión')

    analysis_ids = fields.One2many('medical.analysis', 'employee_id', string='Análisis Médicos')
    security_situation_ids = fields.One2many('security.situation', 'employee_id', string="Situaciones de Seguridad")

    avg_systolic = fields.Integer(string='Promedio Sistólico', compute='_compute_average_pressure', store=True)
    avg_diastolic = fields.Integer(string='Promedio Diastólica', compute='_compute_average_pressure', store=True)

    # Metodo para contabilizar y dar valor a los contadores de situaciones
    @api.depends('security_situation_ids.type', 'security_situation_ids.event_date', 'incident_count_string', 'accident_count_string', 'quasi_accident_count_string')
    def _compute_security_counts(self):
        Situation = self.env['security.situation'].sudo() # Se usa compute_sudo() para que no falle el conteo por permisos
        for employee in self:
            # Conteos
            incidents = Situation.search([
                ('employee_id', '=', employee.id),
                ('type', '=', 'incident'),
            ])
            accidents = Situation.search([
                ('employee_id', '=', employee.id),
                ('type', '=', 'accident'),
            ])
            quasi_accidents = Situation.search([
                ('employee_id', '=', employee.id),
                ('type', '=', 'quasi_accident'),
            ])

            employee.incident_count = str(len(incidents))
            employee.accident_count = len(accidents)
            employee.quasi_accident_count = len(quasi_accidents)

            #Asigno valor al campo string correspondiente dependiendo del
            #valor al hacer el conteo
            if employee.incident_count == 0:
                employee.incident_count_string = "0"
            else:
                employee.incident_count_string = str(employee.incident_count)

            if employee.accident_count == 0:
                employee.accident_count_string = "0"
            else:
                employee.accident_count_string = str(employee.accident_count)

            if employee.quasi_accident_count == 0:
                employee.quasi_accident_count_string = "0"
            else:
                employee.quasi_accident_count_string = str(employee.quasi_accident_count)

            # Último accidente
            last_accident = Situation.search([
                ('employee_id', '=', employee.id),
                ('type', '=', 'accident'),
            ], order='event_date desc', limit=1)
            employee.last_accident_date = last_accident.event_date if last_accident else False

    # Metodo para obtener el promedio de presion
    @api.depends('pressure_daily_ids.blood_pressure_systolic', 'pressure_daily_ids.blood_pressure_diastolic')
    def _compute_average_pressure(self):
        for employee in self:
            if employee.pressure_daily_ids:
                total_systolic = sum(employee.pressure_daily_ids.mapped('blood_pressure_systolic'))
                total_diastolic = sum(employee.pressure_daily_ids.mapped('blood_pressure_diastolic'))
                count = len(employee.pressure_daily_ids)

                # Redondea y asigna el promedio
                employee.avg_systolic = float_round(total_systolic / count, precision_digits=0)
                employee.avg_diastolic = float_round(total_diastolic / count, precision_digits=0)
            else:
                employee.avg_systolic = 0
                employee.avg_diastolic = 0

    # Metodo para obtener los ultimos registros de salud de un empleado
    @api.depends('health_record_ids.record_date', 'health_record_ids.height', 'health_record_ids.imc', 'health_record_ids.blood_type')
    def _compute_last_health_data(self):
        for employee in self:
            #Usado solo para bloodType
            first_record = self.env['employee.health'].search([
                ('employee_id', '=', employee.id)
            ], order='record_date asc', limit=1)

            last_record = self.env['employee.health'].search([
                ('employee_id', '=', employee.id)
            ], order='record_date desc', limit=1)

            if last_record:
                employee.last_height = last_record.height
                employee.last_weight = last_record.weight
                employee.last_imc = last_record.imc
                employee.blood_type = first_record.blood_type

            else:
                employee.last_height == 0.0
                employee.last_weight == 0.0
                employee.last_imc == 0.0
                employee.blood_type == 0.0

    # Este metodo filtra todos los registros de situaciones de seguridad ligadas a un empleado
    def action_open_employee_situations(self):
        self.ensure_one()
        return {
            'name': ('Situaciones de seguridad de %s' % self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'security.situation',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'group_by': 'type',
                        },
        }