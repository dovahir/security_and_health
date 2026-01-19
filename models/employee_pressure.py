from odoo import models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup
from odoo.tools import format_date, format_datetime

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

        # === SEGUIMIENTO EN EL CHATTER DE LA SITUACIÓN ===

    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.employee_id:
                formatted_date = format_datetime(self.env, rec.record_date) if rec.record_date else "N/A"
                rec.employee_id.message_post(
                    body=Markup(
                        """
                        <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify;">
                            <b>📋 NUEVA TOMA DE PRESION</b><br/>
                            <span style="margin-left: 20px;">• FECHA DE CREACION: %s</span>
                        </div>
                        """) % (
                             formatted_date
                         ),
                )
        return records

    def write(self, vals):
        # Guardar valores antiguos solo de campos relevantes para el mensaje
        # Solo estos campos generan mensajes si cambian.
        TRACKED_FIELDS = {'record_date', 'ta_systolic', 'ta_diastolic', 'fc'}
        tracked_vals = {k: v for k, v in vals.items() if k in TRACKED_FIELDS}

        if not tracked_vals:
            return super().write(vals)

        # Guardar valores antiguos
        old_data = {}
        for rec in self:
            old_data[rec.id] = {
                f: rec[f] for f in tracked_vals
            }

        result = super().write(vals)

        # Publicar cambios en el chatter de la situación
        for rec in self:
            old = old_data.get(rec.id, {})
            new = {f: rec[f] for f in tracked_vals}
            changes = []

            # Compara cambios y escribe si cambiaron
            for field_name, old_val in old.items():
                new_val = new[field_name]
                if old_val != new_val:
                    formatted_date = format_datetime(self.env, rec.record_date) if rec.record_date else "N/A"
                    field_label = rec._fields[field_name].string or field_name
                    old_display = self._format_value_for_display(field_name, old_val)
                    new_display = self._format_value_for_display(field_name, new_val)
                    # Damos formato para que sea legible
                    changes.append(f"<li>{field_label}: {old_display} → {new_display}</li>")

            if changes and rec.employee_id:
                changes_html = Markup("".join(changes))
                rec.employee_id.message_post(
                    body=Markup(
                        """
                        <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify;">
                            <b>📋 TOMA DE PRESION ACTUALIZADO</b><br/>
                            <span style="margin-left: 20px;">• Cambios del registro de %s:</span>
                            <ul style="margin-left: 40px;">%s</ul>
                        </div>
                        """) % (
                        formatted_date,
                        changes_html,
                         ),
                )

        return result

    def unlink(self):
        # Guardar referencia antes de borrar
        messages = []
        for rec in self:
            if rec.employee_id:
                # Damos formato al campo datetime
                formatted_date = format_datetime(self.env, rec.record_date) if rec.record_date else "N/A"
                # Campos que queremos guardar
                messages.append((rec.employee_id, formatted_date))

        result = super().unlink()

        # Publicar después de unlink (los registros ya no existen, pero messages sí)
        for situation, pressure_display in messages:
            situation.message_post(
                body=Markup(
                    """
                    <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify;">
                        <b>📋 TOMA DE PRESION ELIMINADO</b><br/>
                        <span style="margin-left: 20px;">• Se eliminó el registro de la fecha: %s</span>
                    </div>
                    """) % (
                         pressure_display,
                     ),
            )

        return result

    # Convierte valores técnicos en texto legible para el usuario.
    def _format_value_for_display(self, field_name, value):
        field = self._fields[field_name]

        # Para campos many2one
        if field.type == 'many2one':
            return value.display_name if value else _('None')

        # Para campos boolean
        elif field.type == 'boolean':
            return _('Sí') if value else _('No')

        # Para campos selection
        elif field.type == 'selection':
            if value is False or value is None:
                return ''  # Manejar valores vacíos

            # field._description_selection(self.env) nos da la lista de tuplas [(key, label), ...]
            # dict(...) la convierte en un diccionario {key: label, ...}
            selection_dict = dict(field._description_selection(self.env))

            # Buscamos la etiqueta usando la clave (el 'value' almacenado en BD)
            # Usamos .get() por si acaso el valor almacenado no existe en la definición actual
            display_label = selection_dict.get(value, str(value))
            return display_label

        # Para campos char o text
        elif value is False and field.type in ('char', 'text'):
            return ''

        # Para fechas tipo date
        elif field.type == 'date':
            return format_date(self.env, value) if value else ''

        # Para fechas tipo datetime
        elif field.type == 'datetime':
            return format_datetime(self.env, value) if value else ''

        # Para otros campos no listados arriba
        else:
            return str(value) if value is not None else _('None')