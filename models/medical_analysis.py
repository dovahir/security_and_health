import base64

from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError

class MedicalAnalysis(models.Model):
    _name ='medical.analysis'
    _description = 'Resultados de análisis médicos'
    _rec_name = 'type_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Campos del formulario
    name = fields.Char(string='Referencia', required=True, default='Nuevo análisis')
    type_id = fields.Many2one('medical.analysis.type',
                              string="Tipo de Análisis",
                              required=True,
                              tracking=True)
    employee_id = fields.Many2one('hr.employee',
                                  string='Empleado',
                                  ondelete='cascade',
                                  required=True,
                                  tracking=True)
    analysis_date = fields.Date(string='Fecha de analisis', required=True, default=fields.Date.today, tracking=True)
    laboratory = fields.Char(string='Laboratorio', tracking=True)
    laboratory_phone = fields.Char(string='Contacto', tracking=True)

    # Notebook de Resultados del analisis
    analysis_line_ids = fields.One2many(
        'medical.analysis.line',
        'analysis_id',
        string='Resultados del Análisis',
        tracking=True
    )

    # Notebook de Anexo para cargar el pdf (como anexo opcional)
    analysis_file = fields.Binary(string='Archivo PDF (Max: 5MB)', attachment=True)
    file_name = fields.Char(string='Nombre del archivo', tracking=True)
    password = fields.Char(string='Contraseña', tracking=True)

    state = fields.Selection([
        ('draft', 'En proceso'),
        ('ready', 'Concluido'),
    ], string='Estado', default='draft', required=True, tracking=True)

    # Metodo de cambio de estado
    def action_draft(self):
        """ Vuelve el estrado a Borrador """
        self.ensure_one()
        self.state = 'draft'

    def action_ready(self):
        """ Marca como Listo """
        self.ensure_one()
        self.state = 'ready'

    # Plantilla de parámetros del análisis
    @api.onchange('type_id')
    def _onchange_type_id(self):
        """
        Al cambiar el tipo de análisis:
        Limpia la tabla anterior
        Trae los parámetros de ese tipo
        Crea renglones vacíos listos para llenar.
        """
        if not self.type_id:
            return
        # Lista de lineas
        lines = [Command.clear()] #Eliminar las anteriores para no mezclar

        for param in self.type_id.parameter_ids:
            lines.append(Command.create({
                'parameter_id': param.id,
                'result_value': '', # Para que el usuario escriba
                'unit_of_measure': param.unit_of_measure,
                'reference_range': param.reference_range,
            }))
        self.analysis_line_ids = lines

    #Funcion que hace validaciones al archivo
    @api.constrains('analysis_file')
    def _check_pdf(self):
        for record in self:
            #Si no hay archivo, termina
            if not record.analysis_file:
                continue

            #Verifica si tiene extensión .pdf
            # filename = (record.file_name or "").lower()
            # if not filename.endswith(".pdf"):
            #     raise UserError(_("Solo PDF's"))

            #Verifica si no excede tamaño
            file_bytes = base64.b64decode(record.analysis_file)
            file_size = len(file_bytes)
            max_size = 5 * 1024 * 1024 #5MB
            if file_size > max_size:
                raise UserError(_("El archivo pdf excede el tamaño máximo (5MB)"))

            #Verifica que, aunque termine en .pdf, sea un pdf real
            if not file_bytes.startswith(b"%PDF"):
                raise UserError(_("PDF no valido"))

    # Restriccion de fecha futura
    @api.constrains('analysis_date')
    def _check_analysis_date(self):
        for record in self:
            if record.analysis_date > fields.Date.today():
                raise UserError("No puedes registrar un analisis con fecha futura.")

    # Restriccion para el numero telefonico
    @api.constrains('laboratory_phone')
    def _check_digits(self):
        for num in self:
            if not num.laboratory_phone:
                continue

            if not num.laboratory_phone.isdigit():
                raise UserError (_("Solo se admiten números en el campo Contacto"))
            total = len(num.laboratory_phone)
            if total != 10:
                raise UserError(_("No es un número de contacto valido"))
