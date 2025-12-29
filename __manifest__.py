# noinspection PyStatementEffect
{
    'name': 'Seguridad y Salud',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Lleve un seguimiento de los accidentes de sus empleados, '
               'y tenga un control de datos de salud general',
    'description': 'Modulo integrado con Empleados de Odoo',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    # Recordar que el orden en que se declaran los archivos importa cuando se accede a ellos.
    'data': [
        'security/security_and_health_security.xml',
        'security/ir.model.access.csv',
        'views/security_situation_view.xml',
        'views/work_center_view.xml',
        'views/hr_employee_view.xml',
        'views/injury_type_view.xml',
        'report/report_templates.xml',
        'views/final_report_view.xml',
        'views/employee_pressure_view.xml',
        'views/employee_health_view.xml',
        'views/medical_analysis_view.xml',
        'views/medical_analysis_type_view.xml',
        'views/medical_analysis_parameter_view.xml',
        'views/security_attention_view.xml',
        'views/menu_view.xml',
        'data/lang_no_seconds.xml',
        'data/medical_analysis_parameter_data.xml',
        'data/ir_sequence_data.xml',
],

    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'icon': '/security_and_health/static/description/icon.png',

}
