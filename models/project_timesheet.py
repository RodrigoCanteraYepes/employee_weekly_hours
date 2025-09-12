from odoo import models, fields, api

class ProjectTimesheet(models.Model):
    _inherit = 'account.analytic.line'

    @api.model_create_multi
    def create(self, vals_list):
        """Activar actualización de resumen semanal cuando se crean nuevas entradas de hoja de tiempo"""
        records = super().create(vals_list)
        
        # Obtener empleados únicos de los registros creados
        employees = records.mapped('employee_id')
        if employees:
            # Activar verificación de resumen semanal para empleados afectados
            self.env['employee.weekly.summary']._check_weekly_discrepancies(employees)
        
        return records

    def write(self, vals):
        """Activar actualización de resumen semanal cuando se modifican entradas de hoja de tiempo"""
        result = super().write(vals)
        
        if any(field in vals for field in ['unit_amount', 'date', 'employee_id']):
            employees = self.mapped('employee_id')
            if employees:
                self.env['employee.weekly.summary']._check_weekly_discrepancies(employees)
        
        return result
