from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class EmployeeWeeklySummary(models.Model):
    _name = 'employee.weekly.summary'
    _description = 'Resumen de Horas Semanales del Empleado'
    _order = 'week_start_date desc, employee_id'

    employee_id = fields.Many2one('hr.employee', string="Empleado", required=True)
    week_start_date = fields.Date(string="Inicio de Semana", required=True)
    week_end_date = fields.Date(string="Fin de Semana", required=True)
    
    logged_hours = fields.Float(string="Horas Registradas")
    expected_hours = fields.Float(string="Horas Esperadas")
    discrepancy = fields.Float(string="Discrepancia", compute="_compute_discrepancy", store=True)
    
    status = fields.Selection([
        ('on_track', 'En Seguimiento'),
        ('overtime', 'Horas Extra'),
        ('undertime', 'Horas Insuficientes'),
        ('critical', 'Discrepancia Crítica')
    ], string="Estado", compute="_compute_status", store=True)
    
    manager_notified = fields.Boolean(string="Gerente Notificado", default=False)
    notification_date = fields.Datetime(string="Fecha de Notificación")
    
    notes = fields.Text(string="Notas")

    @api.depends('logged_hours', 'expected_hours')
    def _compute_discrepancy(self):
        for record in self:
            record.discrepancy = record.logged_hours - record.expected_hours

    @api.depends('discrepancy')
    def _compute_status(self):
        for record in self:
            discrepancy = record.discrepancy
            if abs(discrepancy) <= 2:
                record.status = 'on_track'
            elif discrepancy > 10:
                record.status = 'critical'
            elif discrepancy > 2:
                record.status = 'overtime'
            else:
                record.status = 'undertime'

    @api.model
    def _generate_weekly_summaries(self):
        """Scheduled action to generate weekly summaries and check for discrepancies"""
        _logger.info("Starting weekly summary generation...")
        
        # Get the previous week (Monday to Sunday)
        today = fields.Date.today()
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        # Get all active employees
        employees = self.env['hr.employee'].search([('active', '=', True)])
        
        for employee in employees:
            # Check if summary already exists for this week
            existing_summary = self.sudo().search([
                ('employee_id', '=', employee.id),
                ('week_start_date', '=', last_monday)
            ])
            
            if existing_summary:
                continue
            
            # Calculate logged hours for the week
            timesheets = self.env['account.analytic.line'].search([
                ('employee_id', '=', employee.id),
                ('date', '>=', last_monday),
                ('date', '<=', last_sunday),
                ('project_id', '!=', False)
            ])
            
            logged_hours = sum(timesheets.mapped('unit_amount'))
            
            # Create weekly summary
            summary = self.sudo().create({
                'employee_id': employee.id,
                'week_start_date': last_monday,
                'week_end_date': last_sunday,
                'logged_hours': logged_hours,
                'expected_hours': employee.expected_weekly_hours,
            })
            
            # Check if manager notification is needed
            if summary.status in ['overtime', 'undertime', 'critical']:
                self._notify_manager(summary)

    def _check_weekly_discrepancies(self, employees):
        """Check current week discrepancies for given employees and notify if needed"""
        today = fields.Date.today()
        start_of_week = today - timedelta(days=today.weekday())
        
        for employee in employees:
            # Only check on Thursday/Friday for current week
            if today.weekday() >= 3:  # Thursday = 3, Friday = 4
                discrepancy = employee.hours_discrepancy
                
                # Check if significant discrepancy and manager not yet notified this week
                if abs(discrepancy) > 5:  # More than 5 hours discrepancy
                    recent_notification = self.sudo().search([
                        ('employee_id', '=', employee.id),
                        ('week_start_date', '=', start_of_week),
                        ('manager_notified', '=', True)
                    ])
                    
                    if not recent_notification:
                        # Create current week summary for notification
                        summary = self.sudo().create({
                            'employee_id': employee.id,
                            'week_start_date': start_of_week,
                            'week_end_date': start_of_week + timedelta(days=6),
                            'logged_hours': employee.current_week_hours,
                            'expected_hours': employee.expected_weekly_hours,
                        })
                        self._notify_manager(summary)

    def _notify_manager(self, summary):
        """Send notification to manager about hour discrepancy"""
        employee = summary.employee_id
        manager = employee.parent_id
        
        if not manager:
            _logger.warning(f"No manager found for employee {employee.name}")
            return
        
        if not manager.work_email:
            _logger.warning(f"No work email found for manager {manager.name}")
            return
        
        # Prepare email template context
        template = self.env.ref('employee_weekly_hours.mail_template_hours_discrepancy', raise_if_not_found=False)
        if not template:
            _logger.warning("Email template not found")
            return
        
        # Send email with proper context
        try:
            template.with_context(
                employee_name=employee.name,
                manager_name=manager.name,
                manager_email=manager.work_email,
                logged_hours=summary.logged_hours,
                expected_hours=summary.expected_hours,
                discrepancy=summary.discrepancy,
                status=summary.status,
                week_start=summary.week_start_date.strftime('%Y-%m-%d'),
                week_end=summary.week_end_date.strftime('%Y-%m-%d')
            ).send_mail(summary.id, force_send=True)
            
            # Mark as notified
            summary.write({
                'manager_notified': True,
                'notification_date': fields.Datetime.now()
            })
            
            _logger.info(f"Manager notification sent for {employee.name}")
            
        except Exception as e:
            _logger.error(f"Failed to send manager notification: {str(e)}")
