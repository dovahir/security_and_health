from odoo import models, fields

class MedicalAnalysisParameter(models.Model):
    _name = 'medical.analysis.parameter'
    _description = 'Parámetro de Análisis Médico (Catálogo)'

    # Campos para almacenar un parametro
    name = fields.Char(string='Nombre del Parámetro', required=True)
    reference_range = fields.Text(string='Valores de Referencia', size=255)
    unit_of_measure = fields.Char(string='Unidad de Medida')

    # Restriccion en BD para el nombre del parametro
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Este parámetro ya existe.')
    ]