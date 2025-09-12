from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Seguimiento de horas semanales
    current_week_hours = fields.Float(
        string="Horas de la Semana Actual",
        compute="_compute_weekly_hours"
    )
    
    expected_weekly_hours = fields.Float(
        string="Horas Semanales Esperadas",
        default=40.0,
        help="Número esperado de horas por semana basado en el horario de trabajo"
    )
    
    hours_discrepancy = fields.Float(
        string="Discrepancia de Horas",
        compute="_compute_hours_discrepancy",
        help="Diferencia entre horas registradas y esperadas (positivo = horas extra, negativo = horas faltantes)"
    )
    
    discrepancy_status = fields.Selection([
        ('on_track', 'En Seguimiento'),
        ('overtime', 'Horas Extra'),
        ('undertime', 'Horas Faltantes'),
        ('critical', 'Discrepancia Crítica')
    ], string="Estado Semanal", compute="_compute_discrepancy_status")
    
    weekly_summary_ids = fields.One2many(
        'employee.weekly.summary',
        'employee_id',
        string="Resúmenes Semanales"
    )

    def _compute_weekly_hours(self):
        """Calcular horas semanales sin @api.depends ya que estamos buscando registros externos"""
        for employee in self:
            # Obtener fechas de la semana actual (lunes a domingo)
            today = fields.Date.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            # Sumar horas de hojas de tiempo para la semana actual
            timesheets = self.env['account.analytic.line'].search([
                ('employee_id', '=', employee.id),
                ('date', '>=', start_of_week),
                ('date', '<=', end_of_week),
                ('project_id', '!=', False)
            ])
            
            employee.current_week_hours = sum(timesheets.mapped('unit_amount'))

    def _compute_hours_discrepancy(self):
        for employee in self:
            employee.hours_discrepancy = employee.current_week_hours - employee.expected_weekly_hours

    def _compute_discrepancy_status(self):
        for employee in self:
            discrepancy = employee.hours_discrepancy
            if abs(discrepancy) <= 2:  # Dentro de la tolerancia de 2 horas
                employee.discrepancy_status = 'on_track'
            elif discrepancy > 10:  # Más de 10 horas extra
                employee.discrepancy_status = 'critical'
            elif discrepancy > 2:
                employee.discrepancy_status = 'overtime'
            else:
                employee.discrepancy_status = 'undertime'
