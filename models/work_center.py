from odoo import models, fields, api, _


class WorkCenter(models.Model):
    _name = "work.center"
    _description = "Centro de Trabajo"

    name = fields.Char(string="Nombre del centro", required=True)
    area_ids = fields.One2many(comodel_name='work.area',
                               inverse_name='work_center_id',
                               string="Áreas")

    num_areas = fields.Integer(string='Número de áreas registradas', compute='_compute_count_areas')

    # Metodo para contar cuantas areas existen en el centro de trabajo
    @api.depends('area_ids', 'num_areas')
    def _compute_count_areas(self):
        for record in self:
            record.num_areas = len(record.area_ids)

    # Metodo para hacer funcionar el boton duplicar aun con sql_constraints
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if 'name' not in default:
            default['name'] = _("%s (Copia)", self.name)

        return super(WorkCenter, self).copy(default = default)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Este centro de trabajo ya existe')
    ]
