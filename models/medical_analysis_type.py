from odoo import models,fields

class MedicalAnalysisType(models.Model):
    _name = 'medical.analysis.type'
    _description = 'Configuración de Tipo de Análisis'

    name = fields.Char(string='Nombre del Análisis', required=True, help="Ej. Biometría Hemática")

    #Aquí definimos qué parametros componen este tipo de análisis
    parameter_ids = fields.Many2many('medical.analysis.parameter',
                                     string='Parámetros Incluidos'
    )

    # _sql_constraints = [
    #     ('name_unique_analysis_type', 'unique (name)', 'Este tipo de analisis ya existe')
    # ]

    _name_unique_analysis_type = models.Constraint('unique (name)',
                                                   'Este tipo de análisis ya existe')