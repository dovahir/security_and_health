from odoo import fields, models


class ActivitiesType(models.Model):
    _name = 'activities.type'
    _description = 'Tipos de actividad'

    name = fields.Char(string='Nombre de la Actividad', required=True)

    # _sql_constraints = [
    #     ('name_unique_activities', 'unique (name)', 'Este tipo de actividad ya existe')
    # ]

    _name_unique_activities = models.Constraint('unique (name)',
                                                   'Este tipo de actividad ya existe')