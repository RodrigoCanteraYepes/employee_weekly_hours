# __manifest__.py
{
    'name': 'Seguimiento de Horas Semanales de Empleados',
    'version': '18.0.1.0.0',
    'category': 'Recursos Humanos',
    'summary': 'Seguimiento de horas semanales de empleados con notificaciones a gerentes por discrepancias',
    'description': '''
        Este módulo calcula automáticamente las horas trabajadas semanalmente basándose en las hojas de tiempo de proyectos
        y notifica a los gerentes cuando hay discrepancias entre las horas registradas y las horas asignadas.
    ''',
    'author': 'Tu Empresa',
    'depends': ['hr', 'project', 'hr_timesheet', 'mail'],
    'data': [
        'data/model_records.xml',
        'views/hr_employee_views.xml',
        'views/weekly_summary_views.xml',
        'security/ir.model.access.csv',
        'data/mail_templates.xml',
        'data/scheduled_actions.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
