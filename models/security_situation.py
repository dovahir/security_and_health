from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64

class SecuritySituation(models.Model):
    _name = 'security.situation'
    _description = 'Situación de Seguridad'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Campos del formulario
    event_date = fields.Datetime(string="Fecha y Hora", default=fields.Datetime.now, required=True, tracking=True)

    name = fields.Char(string='Referencia', required=True, copy=False, index=True,
                       default=lambda self: _('Nueva Situación'),
                       tracking=True, readonly=True)

    type = fields.Selection([
        ('incident', 'Incidente'),
        ('accident', 'Accidente'),
        ('quasi_accident', 'Quasi Accidente'),
        ('lost_time_injury', 'Incidente con Pérdida de Tiempo'),
        ('medical_treatment', 'Requiere tratamiento médico'),
        ('restricted_work_case', 'Caso de Trabajo Restringido'),
        ('non_work_related', 'No Relacionado con Act. Laborales'),
        ('near_misses_incident', 'Incidente "Near Misses"')
    ], string="Tipo de Situación", required=True, tracking=True)

    rwc_days = fields.Integer(string="Días de Trabajo Restringido")

    cause = fields.Selection([
           ('unsafe act', 'Acto Inseguro'),
           ('insecure condition', 'Condición Insegura')
      ], string='Causa', required=True, tracking=True)


    employee_id = fields.Many2one(  #Opcional
        'hr.employee', string="Empleado",
        ondelete='set null', index=True,
        help="Empleado involucrado (opcional).", tracking=True)

    job_id = fields.Many2one(comodel_name='hr.job',
                             related='employee_id.job_id',
                             string="Puesto de trabajo",
                             help="Puesto al que pertenece empleado",
                             store=True,
                             readonly=True)

    department_id = fields.Many2one(comodel_name='hr.department',
                                    related='employee_id.department_id',
                                    string="Departamento",
                                    help="Departamento al que pertenece empleado",
                                    store=True,
                                    readonly=True)

    parent_id = fields.Many2one(comodel_name='hr.employee',
                             related='employee_id.parent_id',
                             string="Líder directo",
                             help="Líder directo a cargo del empleado",
                             store=True,
                             readonly=True)


    follow = fields.Many2one(
        'hr.employee', string="Seguimiento",
        ondelete='set null', index=True,
        help="Empleado que atendió activamente la situación", tracking=True)

    company_id = fields.Many2one('res.company',
                                 string="Empresa",
                                 required=True,
                                 default=lambda self: self.env.company)

    work_center_id = fields.Many2one('hr.work.location',
                                     string="Ubicacion de Trabajo")

    work_area_id = fields.Many2one('work.area',
                                   string="Área / Lugar exacto",
                                   help="Debe seleccionar ubicacion de trabajo")

    event_severity = fields.Selection([
        ('minor', 'Menor'),
        ('moderate', 'Moderado'),
        ('high', 'Alta'),
        ('critic', 'Crítica')
    ], string="Severidad del Evento", required=True, tracking=True)

    immediate_actions = fields.Selection([
        ('first_aid', 'Primeros Auxilios'),
        ('emergency_actions', 'Acciones de Emergencia'),
        ('transfer_worker', 'Traslado del Trabajador'),
        ('area_isolation', 'Aislamiento del Area'),
        ('machine_lockout', 'Bloqueo de Máquina'),
        ('internal_report', 'Reporte Interno')
    ], string="Medidas Inmediatas", required=True, tracking=True)


    activities_type_id = fields.Many2one('activities.type',
                                       string="Tipo de Actividad",
                                       tracking=True)

    factor_type = fields.Selection([
        ('by_blow', 'Por golpe'),
        ('by_contact', 'Por contacto'),
        ('by_hitting against', 'Por pegar contra'),
        ('by_contact with', 'Por contacto con'),
        ('by_entrapment', 'Por atrapamiento'),
        ('by_catching', 'Por prendimiento'),
        ('by_imprisonment', 'Por aprisionamiento'),
        ('by_fall from height', 'Por caída a desnivel'),
        ('by_fall on level ground', 'Por caída a nivel'),
        ('by_overexertion', 'Por sobreesfuerzo'),
        ('by_exposure', 'Por exposición')
    ], string="Factor Tipo", required=True, tracking=True, help="Tipo de Accidente")

    injury_type_id = fields.Many2one('injury.type',
                                     string="Tipo de lesión",
                                     tracking=True
                                     )

    injury_severity = fields.Selection([
        ('first_aid','Solo Primeros Auxilios'),
        ('disabling', 'Incapacitante'),
        ('hospitalization', 'Hospitalización'),
        ('fatal', 'Fatal'),
    ], string ="Severidad de la lesión", tracking=True)

    injury_description = fields.Text(string="Descripción detallada de la lesión")

    body_part = fields.Selection([
        ('head', 'Cabeza'),
        ('eyes', 'Ojos'),
        ('nose', 'Naríz'),
        ('mouth', 'Boca'),
        ('ears', 'Orejas'),
        ('neck', 'Cuello'),
        ('shoulders', 'Hombros'),
        ('arms', 'Brazos'),
        ('hands', 'Manos'),
        ('back', 'Espalda'),
        ('hip', 'Cadera'),
        ('legs', 'Piernas'),
        ('knee', 'Rodilla'),
        ('ankle', 'Tobillo'),
        ('foot', 'Pies')
    ], string="Parte del Cuerpo Afectada", required=True, tracking=True, help="Parte del cuerpo que fue herida/lesionada")

    witnesses = fields.Many2many(
        comodel_name='hr.employee',
        string="Testigos",
        help="Empleados que presenciaron el evento",
        tracking=True
    )

    # Notebook Detalles y evidencias
    details_whats = fields.Text(string="Qué pasó")
    details_how = fields.Text(string="Cómo pasó")
    details_when = fields.Text(string="Cuándo pasó", help="Secuencia Cronológica del Suceso")

    details_materials = fields.Text(string="Materiales y Equipo", help="Describir si existió Herramientas, maquinaria implicada y su estado.")
    details_enviroment = fields.Text(string="Entorno", help="Describir las condiciones de iluminación, suelo, ruido, ventilación, entre otros.")
    details_human_factors = fields.Text(string="Factores Humanos", help="Ojos no en la tarea, mente no en la tarea, falta de señalización, entre otros.")

    evidence_photo_1 = fields.Image(string="Foto de evidencia 1", max_width=1024, max_height=1024)
    evidence_photo_2 = fields.Image(string="Foto de evidencia 2", max_width=1024, max_height=1024)
    evidence_photo_3 = fields.Image(string="Foto de evidencia 3", max_width=1024, max_height=1024)

    state = fields.Selection([
        ('active', 'Activo'),
        ('concluded', 'Concluido'),
    ], string="Estado", tracking=True, default="active")


    # Notebook Seguimiento/Atenciones
    attention_ids = fields.One2many(
        'security.attention',
        'situation_id',
        string='Línea de tiempo de atenciones'
    )

    # Cambia el estado a 'Activo' (Volver a Borrador) o Concluido
    def action_conclude(self):
        self.ensure_one()
        self.state = 'concluded'

    def action_draft(self):
        self.ensure_one()
        self.state = 'active'

    # Limpia el campo de Área de Trabajo cuando cambia el centro de Trabajo
    @api.onchange('work_center_id')
    def _onchange_work_center_id(self):
        # para forzar la selección centro del nuevo dominio.
        self.work_area_id = False

    # Abrir vista Reporte Final
    def action_open_final_report(self):
        self.ensure_one()
        # Buscar un reporte final existente
        report = self.env['final.report'].search([('security_situation_id', '=', self.id)])

        # Si no existe, creamos uno nuevo
        if not report:
            report = self.env['final.report'].create({
                'security_situation_id': self.id,
            })

        # Abrimos la vista del reporte final mediante return
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'final.report',
            'view_mode': 'form',
            'res_id': report.id,
            'target':'current',
        }

    # No permite registrar una fecha y hora futura
    @api.constrains('event_date')
    def _check_event_date_not_future(self):
        for record in self:
            if record.event_date and record.event_date > fields.Datetime.now():
                raise UserError("No puedes registrar una fecha y hora futura para una Situación de Seguridad.")

    # Funcion que hace validaciones a la imagen
    @api.constrains('evidence_photo_1')
    def _check_evidence_photo_1(self):
        for record in self:
            # Si no hay archivo, termina
            if not record.evidence_photo_1:
                continue

            # Verifica si no excede tamaño
            file_bytes1 = base64.b64decode(record.evidence_photo_1)
            file_size1 = len(file_bytes1)
            max_size1 = 5 * 1024 * 1024  # 5MB
            if file_size1 > max_size1:
                raise UserError(_("Evidencia 1 excede el tamaño permitido (5MB)"))

    @api.constrains('evidence_photo_2')
    def _check_evidence_photo_2(self):
        for record in self:
            # Si no hay archivo, termina
            if not record.evidence_photo_2:
                continue

            # Verifica si no excede tamaño
            file_bytes2 = base64.b64decode(record.evidence_photo_2)
            file_size2 = len(file_bytes2)
            max_size2 = 5 * 1024 * 1024  # 5MB
            if file_size2 > max_size2:
                raise UserError(_("Evidencia 2 excede el tamaño permitido (5MB)"))

    @api.constrains('evidence_photo_3')
    def _check_evidence_photo_3(self):
        for record in self:
            # Si no hay archivo, termina
            if not record.evidence_photo_3:
                continue

            # Verifica si no excede tamaño
            file_bytes3 = base64.b64decode(record.evidence_photo_3)
            file_size3 = len(file_bytes3)
            max_size3 = 5 * 1024 * 1024  # 5MB
            if file_size3 > max_size3:
                raise UserError(_("Evidencia 3 excede el tamaño permitido (5MB)"))

    # Metodo usado para la secuencia de name (referencia)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nueva Situación')) == _('Nueva Situación'):
                vals['name'] = (self.env['ir.sequence'].next_by_code('security.situation'))
        return super().create(vals_list)

