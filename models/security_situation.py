from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import datetime
from datetime import date, timedelta


class SecuritySituation(models.Model):
    _name = 'security.situation'
    _description = 'Situación de Seguridad'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Referencia', required=True, copy=False, index=True,
                       default=lambda self: _('Nueva Situación'),
                       tracking=True, readonly=True)

    # Campos del formulario-----------------------------------------------------------

    # Info de la situación--------

    event_date = fields.Datetime(string="Fecha y Hora",
                                 default=fields.Datetime.now, required=True, tracking=True)

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

    rwc_days = fields.Integer(string="Días de Trabajo Restringido", tracking=True)

    activities_type_id = fields.Many2one(comodel_name='activities.type',
                                         string="Tipo de Actividad",
                                         tracking=True,
                                         required=True)

    event_severity = fields.Selection([
        ('minor', 'Menor'),
        ('moderate', 'Moderado'),
        ('high', 'Alta'),
        ('critic', 'Crítica')
    ], string="Severidad del Evento", required=True, tracking=True)

    cause = fields.Selection([
        ('unsafe act', 'Acto Inseguro'),
        ('insecure condition', 'Condición Insegura')
    ], string='Causa', required=True, tracking=True)

    immediate_actions = fields.Selection([
        ('first_aid', 'Primeros Auxilios'),
        ('emergency_actions', 'Acciones de Emergencia'),
        ('transfer_worker', 'Traslado del Trabajador'),
        ('area_isolation', 'Aislamiento del Area'),
        ('machine_lockout', 'Bloqueo de Máquina'),
        ('internal_report', 'Reporte Interno')
    ], string="Medidas Inmediatas", required=True, tracking=True)

    follow = fields.Many2one(
        comodel_name='hr.employee', string="Seguimiento",
        ondelete='set null', index=True,
        help="Empleado que atendió activamente la situación (Opcional)", tracking=True)

    witnesses = fields.Many2many(
        comodel_name='hr.employee',
        string="Testigos",
        help="Empleados que presenciaron el evento (Opcional)",
        tracking=True)

    # Ubicacion-----------

    location_situation = fields.Selection([
        ('inside', 'Dentro de la empresa'),
        ('outside', 'Fuera de la empresa'),
        ('commute', 'Trayecto al trabajo')
    ], string='¿Dónde sucedió?' , tracking=True, required=True)

    company_id = fields.Many2one(comodel_name='res.company',
                                 string="Empresa",
                                 help="Empresa donde ocurrió la situación", tracking=True)

    phone_company = fields.Char(string="Teléfono", related='company_id.phone')

    work_center_id = fields.Many2one(comodel_name='hr.work.location',
                                     string="Ubicación de Trabajo",
                                     help="Ubicación en la empresa donde ocurrió la situación", tracking=True)

    work_area_id = fields.Many2one(comodel_name='work.area',
                                   string="Área / Lugar exacto",
                                   help="Debe seleccionar ubicación de trabajo", tracking=True)

    # Responsables--------

    supervisor_ssma = fields.Many2one(comodel_name='hr.employee',
                                      string="Supervisor SSMA",
                                      ondelete='cascade',
                                      tracking=True,
                                      default=lambda self: self.env.user.employee_id,
                                      required=True)

    supervisor_ssma_phone = fields.Char(string="Teléfono de trabajo", related='supervisor_ssma.work_phone')

    supervisor_ssma_email = fields.Char(string="E-mail de trabajo", related='supervisor_ssma.work_email')

    is_constr_supervisor = fields.Selection([
        ('yes', 'Sí'),
        ('no', 'No')
    ], string='¿Existe responsable de obra?', default='no', tracking=True)

    constr_supervisor = fields.Char(string="Nombre del supervisor de obra", tracking=True)

    constr_supervisor_phone = fields.Char(string="Teléfono de contacto", tracking=True)

    # Info del empleado---------

    employee_id = fields.Many2one(  # Opcional
        comodel_name='hr.employee', string="Empleado",
        ondelete='set null', index=True,
        help="Empleado involucrado (opcional). Al seleccionar, se despliegan más campos", tracking=True)

    employee_picture = fields.Image(related='employee_id.image_1920', readonly=True)

    company_employee_id = fields.Many2one(comodel_name='res.company',
                                    related='employee_id.company_id',
                                    string="Empresa",
                                    help="Empresa donde labora el empleado",
                                    store=True,
                                    readonly=True)

    department_id = fields.Many2one(comodel_name='hr.department',
                                    related='employee_id.department_id',
                                    string="Departamento",
                                    help="Departamento al que pertenece empleado",
                                    store=True,
                                    readonly=True)

    job_id = fields.Many2one(comodel_name='hr.job',
                             related='employee_id.job_id',
                             string="Puesto de trabajo",
                             help="Puesto al que pertenece empleado",
                             store=True,
                             readonly=True)

    employee_type = fields.Selection(string="Tipo de empleado", related='employee_id.employee_type', help="")

    parent_id = fields.Many2one(comodel_name='hr.employee',
                                related='employee_id.parent_id',
                                string="Líder directo",
                                help="Líder directo a cargo del empleado",
                                store=True,
                                readonly=True)

    private_phone = fields.Char(string='Teléfono Personal', related='employee_id.private_phone')
    private_email = fields.Char(string='Correo Personal', related='employee_id.private_email')
    private_street = fields.Char(string="Dirección Particular", related='employee_id.private_street')
    private_street2 = fields.Char(string="", related='employee_id.private_street2')
    private_state_id = fields.Many2one(string="Estado", related='employee_id.private_state_id')
    private_city = fields.Char(string="Ciudad", related='employee_id.private_city')
    marital = fields.Selection(string="Estado Civil", related='employee_id.marital', tracking=False)
    birthday = fields.Date(string="Fecha de nacimiento", related='employee_id.birthday', tracking=False)

    actual_laboral_state = fields.Selection([
        ('normal', 'Actividades normales'),
        ('not_normal', 'Actividades parciales'),
        ('out', 'Actividades nulas'),
    ], string="Estado laboral actual", tracking=True)

    # Campos si resulta herido en 'Info del empleado'-----

    given_days = fields.Integer(string='Días de incapacidad', default='0', tracking=True)

    attention_type = fields.Selection([
        ('na', 'N/A'),
        ('private', 'Privada'),
        ('public', 'Pública'),
    ], string="Tipo de atención médica", tracking=True)

    currency_id = fields.Many2one(comodel_name='res.currency', string="Currency",
                                  related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    attention_cost = fields.Monetary(string="Costo de Atención Médica Privada", tracking=True,
                                     help="Costo total de la atención médica (En pesos MX)")

    # Info de lesiones---------------

    is_injuried = fields.Selection([
        ('yes', 'Sí'),
        ('no', 'No')
    ], string='¿Resultó Herido?', default='no', help='Al seleccionar "Sí", se abrirán otros campos', tracking=True)

    is_initial_attention = fields.Boolean(string="¿Hubo atención medica inicial?", tracking=True)

    injury_type_id = fields.Many2one(comodel_name='injury.type',
                                     string="Tipo de lesión",
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
    ], string="Factor Tipo", tracking=True, help="Tipo de Accidente")

    injury_severity = fields.Selection([
        ('first_aid', 'Solo Primeros Auxilios'),
        ('disabling', 'Incapacitante'),
        ('hospitalization', 'Hospitalización'),
        ('fatal', 'Fatal'),
    ], string="Severidad de la lesión", tracking=True)

    injury_description = fields.Text(string="Descripción detallada de la lesión", tracking=True)

    injured_body_part = fields.Many2many('body.parts',
                                         string='Partes del Cuerpo Lesionadas', tracking=True)

    # Notebook: Detalles y evidencias------------

    details_whats = fields.Text(string="Qué pasó", tracking=True)
    details_how = fields.Text(string="Cómo pasó", tracking=True)
    details_when = fields.Text(string="Cuándo pasó", help="Secuencia Cronológica del Suceso", tracking=True)

    details_materials = fields.Text(string="Materiales y Equipo", tracking=True)
    details_enviroment = fields.Text(string="Entorno", tracking=True)
    details_human_factors = fields.Text(string="Factores Humanos", tracking=True)

    evidence_photo_1 = fields.Image(string="Foto de evidencia 1", max_width=1280, max_height=720)
    evidence_photo_2 = fields.Image(string="Foto de evidencia 2", max_width=1280, max_height=720)
    evidence_photo_3 = fields.Image(string="Foto de evidencia 3", max_width=1280, max_height=720)

    state = fields.Selection([
        ('active', 'Activo'),
        ('concluded', 'Concluido'),
    ], string="Estado", tracking=True, default="active")

    # Notebook: Seguimiento/Atenciones

    attention_ids = fields.One2many(
        comodel_name='security.attention',
        inverse_name='situation_id',
        string='Línea de tiempo de atenciones')

    # Campo aún no en vista
    return_activities_date = fields.Date(string="Fecha de regreso a actividades normales",
                                         compute='_compute_return_activities_date',
                                         help="Basado en la fecha de creación de la situacion y los dias de incapacidad del empleado")

    # Funciones---------------------------------------------------------------------------------

    # Cambian el estado a 'Activo' (Volver a Borrador) o Concluido
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
            'target': 'current',
        }

    # No permite registrar una fecha y hora futura
    @api.constrains('event_date')
    def _check_event_date_not_future(self):
        for record in self:
            if record.event_date and record.event_date > fields.Datetime.now():
                raise UserError("No puedes registrar una fecha y hora futura para una Situación de Seguridad.")

    # Funciones que hacen validaciones a la imagen
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

    # Usado para mostrar mensaje del regreso de actividades
    # @api.depends('return_activities_date')
    # def _compute_return_date_warning(self):
    #     today = date.today()
    #     seven_days_later = today + timedelta(days=7)
    #
    #     for record in self:
    #         warning = False
    #         return_date = record.return_activities_date
    #
    #         if not return_date:
    #             record.return_date_warning = False
    #             continue
    #         if return_date == today:
    #             warning = "¡ATENCIÓN! El empleado debería estar actualmente en labores."
    #         elif today < return_date <= seven_days_later:
    #             remaining_days = (return_date - today).days
    #             warning = f"AVISO: El empleado regresa en {remaining_days} días ({return_date.strftime('%d-%m-%Y')})."
    #         elif return_date < today:
    #             warning = "NOTA: La fecha de regreso ya pasó. Verifique el estado laboral."
    #         else:  # Fecha lejana
    #             warning = f"La fecha de regreso está programada para {return_date.strftime('%d-%m-%Y')}."
    #
    #         record.return_date_warning = warning

    # Para calcular la fecha de regreso de actividades
    # @api.depends('return_activities_date', 'given_days', 'event_date')
    # def _compute_return_activities_date(self):
    #     for date in self:
    #         init_date = date.event_date
    #         incapacity_days = datetime.timedelta(days=date.given_days)
    #         newDate = init_date + incapacity_days
    #
    #         date.return_activities_date = newDate

    # Restriccion para los dias de incapacidad
    @api.constrains('given_days')
    def _check_given_days(self):
        for record in self:
            if record.given_days < 0:
                raise UserError(_("Revisar días de incapacidad (No puede ser negativo)"))

    # Metodos onchange para limpiar campos segun cierta condición
    @api.onchange('type')
    def _onchange_type(self):
        if self.type != 'restricted_work_case':
            self.rwc_days = 0

    @api.onchange('is_constr_supervisor')
    def _onchange_is_constr_supervisor(self):
        if self.is_constr_supervisor == 'no':
            self.constr_supervisor = ""
            self.constr_supervisor_phone = ""

    @api.onchange('attention_type')
    def _onchange_attention_type(self):
        if self.attention_type != 'private':
            self.attention_cost = 0

    @api.onchange('actual_laboral_state')
    def _onchange_actual_laboral_state(self):
        if self.actual_laboral_state == 'normal':
            self.given_days = 0
            self.attention_type = 'na'

    @api.onchange('is_injuried')
    def _onchange_is_injuried(self):
        if self.is_injuried == 'no':
            self.is_initial_attention = False
            self.injury_type_id = False
            self.factor_type = False
            self.injury_severity = False
            self.injury_description = ''
            self.injured_body_part = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.actual_laboral_state = 'normal'
            self.is_injuried = 'no'

    @api.onchange('location_situation')
    def _onchange_location_situation(self):
        if self.location_situation != 'inside':
            self.company_id = False
            self.work_center_id = False
            self.work_area_id = False