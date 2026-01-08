from odoo import models, fields, api

# Modelo utilizado para conectar los resultados de análisis de un empleado con el tipo de analisis y
# parametros correspondientes,principalmente en un notebook en medical.analysis

class MedicalAnalysisLine(models.Model):
    _name = 'medical.analysis.line'
    _description = 'Notebook de Resultados de Análisis Médicos'

    analysis_id = fields.Many2one('medical.analysis',
                                  string='Análisis',
                                  ondelete='cascade',
                                  required=True)
    parameter_id = fields.Many2one('medical.analysis.parameter',
                                   string='Parámetro',
                                   required=True)
    result_value = fields.Char(string='Resultado', required=True)

    # Los siguientes campos se auto-completan al seleccionar el parámetro, pero se pueden sobrescribir.
    reference_range = fields.Text(string='Valores de Referencia', related='parameter_id.reference_range' )
    unit_of_measure = fields.Char(string='Unidad', related='parameter_id.unit_of_measure', readonly=False)

    @api.onchange('parameter_id')
    def _onchange_parameter_id(self):
        if self.parameter_id:
            self.reference_range = self.parameter_id.reference_range
            self.unit_of_measure = self.parameter_id.unit_of_measure

