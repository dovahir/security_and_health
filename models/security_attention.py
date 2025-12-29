from odoo import models, fields, _
from markupsafe import Markup
from odoo.tools import format_date, format_datetime

class SecurityAttention(models.Model):
    _name = 'security.attention'
    _description = 'Atención brindada a la Situación de Seguridad'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_time desc'

    name = fields.Char(string='Referencia', required=True, default='Atención')
    date_time = fields.Datetime(
        string='Fecha y Hora',
        required=True,
        default=fields.Datetime.now,
        tracking=True
    )
    attention_type = fields.Selection([
        ('note', 'Nota / Seguimiento'),
        ('investigation', 'Paso de Investigación'),
        ('action', 'Acción Tomada'),
        ('state_change', 'Cambio de Estado'),
    ], string='Tipo de Atención', default='note', required=True)
    responsible_id = fields.Many2one('hr.employee', string='Responsable de la Atención')
    action_taken = fields.Text(string='Acción tomada / Detalle de la atención', required=True)
    situation_id = fields.Many2one(
        'security.situation',
        string='Situación de Seguridad',
        ondelete='cascade',
        required=True
    )

    situation_employee_id = fields.Many2one(
        related='situation_id.employee_id',
        string='Empleado de la Situación',
        readonly=True,
        store=True  # Recomendado para que sea buscable y filtrable en la lista
    )

    # === SEGUIMIENTO EN EL CHATTER DE LA SITUACIÓN ===

    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.situation_id:
                attention_type_display = dict(rec._fields['attention_type'].selection).get(rec.attention_type)
                rec.situation_id.message_post(
                    body=Markup(
                        """
                        <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify;">
                            <b>📋 NUEVO SEGUIMIENTO/ATENCIÓN CREADO</b><br/>
                            <span style="margin-left: 20px;">• Tipo de atención: %s</span>
                        </div>
                        """) % (
                        attention_type_display
                    ),
                )
        return records

    def write(self, vals):
        # Guardar valores antiguos solo de campos relevantes para el mensaje
        # Solo estos campos generan mensajes si cambian.
        TRACKED_FIELDS = {'date_time', 'attention_type', 'responsible_id', 'action_taken'}
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
                    field_label = rec._fields[field_name].string or field_name
                    old_display = self._format_value_for_display(field_name, old_val)
                    new_display = self._format_value_for_display(field_name, new_val)
                    # Damos formato para que sea legible
                    changes.append(f"<li>{field_label}: {old_display} → {new_display}</li>")

            if changes and rec.situation_id:
                changes_html = Markup("".join(changes))
                rec.situation_id.message_post(
                    body=Markup(
                        """
                        <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify;">
                            <b>📋 SEGUIMIENTO/ATENCIÓN ACTUALIZADO</b><br/>
                            <span style="margin-left: 20px;">• Cambios:</span>
                            <ul style="margin-left: 40px;">%s</ul>
                        </div>
                        """) % (
                        changes_html,
                    ),
                )

        return result

    def unlink(self):
        # Guardar referencia antes de borrar
        messages = []
        for rec in self:
            if rec.situation_id:
                # Damos formato al campo selection
                attention_type_display = dict(rec._fields['attention_type'].selection).get(rec.attention_type)
                # Campos que queremos guardar
                messages.append((rec.situation_id, attention_type_display))

        result = super().unlink()

        # Publicar después de unlink (los registros ya no existen, pero messages sí)
        for situation, attention_type_display in messages:
            situation.message_post(
                body=Markup(
                    """
                    <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify;">
                        <b>📋 SEGUIMIENTO/ATENCIÓN ELIMINADO</b><br/>
                        <span style="margin-left: 20px;">• Se eliminó:</span>
                        <ul style="margin-left: 40px;"><li>%s</li></ul>
                    </div>
                    """) % (
                    attention_type_display,
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

