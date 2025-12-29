from odoo import models, fields, api, _

class WorkArea(models.Model):
    _name = "work.area"
    _description = "Área de trabajo"

    name = fields.Char(string="Nombre del área", required=True)
    location_id = fields.Many2one(comodel_name='hr.work.location',
                                   string="Ubicación",
                                   ondelete='cascade')

    # _sql_constraints = [
    #     ('name_unique', 'unique (work_center_id, name)', 'Esta área de trabajo ya existe en este centro')
    # ]


class WorkCenter(models.Model):
    _inherit = 'hr.work.location'

    area_ids = fields.One2many(comodel_name='work.area',
                               inverse_name='location_id',
                               string="Áreas")

    # num_areas = fields.Integer(string='Número de áreas registradas', compute='_compute_count_areas')
    #
    # # Metodo para contar cuantas areas existen en el centro de trabajo
    # @api.depends('area_ids', 'num_areas')
    # def _compute_count_areas(self):
    #     for record in self:
    #         record.num_areas = len(record.area_ids)
    #
    # # Metodo para hacer funcionar el boton duplicar aun con sql_constraints
    # @api.returns('self', lambda value: value.id)
    # def copy(self, default=None):
    #     default = dict(default or {})
    #     if 'name' not in default:
    #         default['name'] = _("%s (Copia)", self.name)
    #
    #     return super(WorkCenter, self).copy(default = default)
    #
    # _sql_constraints = [
    #     ('name_uniq', 'unique (name)', 'Este centro de trabajo ya existe')
    # ]
