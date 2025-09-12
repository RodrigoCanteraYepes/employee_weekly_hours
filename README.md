# Módulo de Seguimiento de Horas Semanales de Empleados

## Descripción General

El módulo de Seguimiento de Horas Semanales de Empleados es un complemento integral de Odoo diseñado para monitorear automáticamente las horas de trabajo de los empleados, detectar discrepancias entre las horas esperadas y registradas, y notificar a los gerentes cuando sea necesaria una intervención. Este módulo se integra perfectamente con los módulos existentes de RRHH, Proyectos y Hojas de Tiempo de Odoo para proporcionar información en tiempo real sobre la productividad y el cumplimiento de la fuerza laboral.

## Características Principales

### 📊 Seguimiento de Horas en Tiempo Real
- **Monitoreo de Semana Actual**: Calcula automáticamente las horas registradas por cada empleado para la semana actual
- **Actualizaciones Dinámicas**: Las horas se recalculan en tiempo real cuando los empleados registran entradas de hoja de tiempo
- **Integración de Proyectos**: Solo cuenta las horas registradas contra proyectos reales (excluye tiempo administrativo)

### 🎯 Detección de Discrepancias
- **Sistema de Estado Inteligente**: Categoriza a los empleados en cuatro niveles de estado:
  - **En Curso**: Dentro de 2 horas de las horas semanales esperadas
  - **Tiempo Extra**: 2-10 horas por encima de las horas esperadas
  - **Tiempo Insuficiente**: Más de 2 horas por debajo de las horas esperadas
  - **Crítico**: Más de 10 horas por encima de las horas esperadas
- **Umbrales Configurables**: Las horas semanales esperadas pueden personalizarse por empleado
- **Configuraciones de Tolerancia**: Niveles de tolerancia incorporados previenen alertas innecesarias por variaciones menores

### 📧 Notificaciones Automáticas a Gerentes
- **Alertas Inteligentes**: Notifica automáticamente a los gerentes cuando ocurren discrepancias significativas
- **Lógica de Tiempo**: Envía alertas los jueves/viernes para problemas de la semana actual (permitiendo tiempo para corrección)
- **Prevención de Duplicados**: Asegura que los gerentes no sean bombardeados con múltiples alertas por el mismo problema
- **Plantillas de Email Enriquecidas**: Notificaciones de email profesionales con desgloses detallados de horas

### 📈 Seguimiento Histórico
- **Resúmenes Semanales**: Mantiene registros históricos completos de resúmenes de horas semanales
- **Análisis de Tendencias**: Rastrea patrones en los hábitos de trabajo de los empleados a lo largo del tiempo
- **Pista de Auditoría**: Registra cuándo se notificó a los gerentes y por qué razones

## Componentes del Módulo

### Modelos

#### 1. Extensiones de Empleado RRHH (`hr_employee.py`)
Extiende el registro estándar de empleado con capacidades de seguimiento de horas semanales.

**Nuevos Campos:**
- `current_week_hours`: Campo calculado que muestra las horas totales de la semana actual
- `expected_weekly_hours`: Horas esperadas configurables (predeterminado: 40)
- `hours_discrepancy`: Diferencia entre horas registradas y esperadas
- `discrepancy_status`: Estado actual (en_curso, tiempo_extra, tiempo_insuficiente, crítico)
- `weekly_summary_ids`: Relación uno-a-muchos con resúmenes históricos

**Métodos Clave:**
- `_compute_weekly_hours()`: Calcula las horas de la semana actual desde las entradas de hoja de tiempo
- `_compute_hours_discrepancy()`: Determina la variación de las horas esperadas
- `_compute_discrepancy_status()`: Categoriza el estado del empleado basado en la discrepancia

#### 2. Extensiones de Hoja de Tiempo de Proyecto (`project_timesheet.py`)
Agrega disparadores automáticos al sistema de hoja de tiempo para monitoreo en tiempo real.

**Funcionalidad:**
- **Disparador de Creación**: Cuando se crean nuevas entradas de hoja de tiempo, verifica automáticamente las discrepancias
- **Disparador de Actualización**: Cuando se modifican entradas existentes, recalcula los resúmenes de empleados afectados
- **Procesamiento Inteligente**: Solo activa verificaciones para empleados cuyos registros fueron realmente afectados

#### 3. Modelo de Resumen Semanal (`weekly_summary.py`)
Modelo central para gestionar resúmenes de horas semanales y notificaciones.

**Campos:**
- `employee_id`: Referencia al empleado
- `week_start_date` / `week_end_date`: Período de semana (lunes a domingo)
- `logged_hours`: Horas reales trabajadas durante la semana
- `expected_hours`: Horas esperadas para el empleado
- `discrepancy`: Diferencia calculada
- `status`: Estado calculado basado en la discrepancia
- `manager_notified`: Bandera que indica si se alertó al gerente
- `notification_date`: Marca de tiempo de la notificación
- `notes`: Campo de texto libre para comentarios adicionales

**Métodos Clave:**
- `_generate_weekly_summaries()`: Método programado para crear resúmenes de fin de semana
- `_check_weekly_discrepancies()`: Verificación de discrepancias en tiempo real para la semana actual
- `_notify_manager()`: Maneja la lógica de notificación al gerente y envío de emails

### Vistas e Interfaz de Usuario

#### 1. Vistas de Empleado Mejoradas
- **Barra de Estado**: Indicador visual de estado en la parte superior de los formularios de empleado
- **Pestaña de Horas Semanales**: Sección dedicada que muestra:
  - Estadísticas de la semana actual
  - Horas esperadas vs. reales
  - Cálculos de discrepancia
  - Resúmenes semanales históricos
- **Mejoras de Vista de Lista**: Resumen rápido de estado en listas de empleados

#### 2. Gestión de Resumen Semanal
- **Vistas Dedicadas**: Interfaz separada para revisar todos los resúmenes semanales
- **Opciones de Filtrado**: Filtrado fácil por empleado, rango de fechas o estado
- **Seguimiento de Notificaciones**: Indicación clara de qué resúmenes activaron alertas de gerente

#### 3. Indicadores Visuales de Estado
- **Insignias Codificadas por Color**: Verde (en curso), Amarillo (tiempo insuficiente), Naranja (tiempo extra), Rojo (crítico)
- **Barras de Estado**: Indicadores estilo progreso que muestran el estado actual del empleado
- **Identificación Rápida**: Los gerentes pueden detectar problemas de un vistazo

### Seguridad y Control de Acceso

#### Niveles de Acceso:
- **Todos los Usuarios**: Acceso de lectura a resúmenes semanales
- **Usuarios de RRHH**: Acceso completo para crear y modificar resúmenes
- **Gerentes de RRHH**: Control administrativo completo incluyendo eliminaciones

#### Grupos de Seguridad:
- Integración con grupos de seguridad estándar de RRHH de Odoo
- Respeta las restricciones de acceso de empleados existentes
- Los gerentes solo ven los datos de sus reportes directos

### Automatización y Programación

#### 1. Generación de Resumen Semanal
- **Acción Programada**: Se ejecuta automáticamente cada lunes a las 9:00 AM
- **Procesamiento de Semana Anterior**: Genera resúmenes para la semana completada
- **Procesamiento en Lote**: Maneja todos los empleados activos en una sola ejecución
- **Prevención de Duplicados**: Omite empleados que ya tienen resúmenes para el período

#### 2. Monitoreo en Tiempo Real
- **Disparadores de Hoja de Tiempo**: Verificaciones automáticas cuando se crean/modifican hojas de tiempo
- **Alertas Basadas en Umbral**: Solo envía notificaciones para discrepancias significativas (>5 horas)
- **Lógica de Tiempo**: Alertas de mitad de semana solo se envían jueves/viernes para permitir tiempo de corrección

### Notificaciones por Email

#### Características de Plantilla:
- **Formato Profesional**: Diseño de email limpio y con marca
- **Información Detallada**: Desglose completo de horas y discrepancias
- **Conciencia de Contexto**: Personalizado con nombres de gerente y empleado
- **Datos Accionables**: Indicación clara de qué acción puede ser necesaria

#### Lógica de Notificación:
- **Jerarquía de Gerente**: Usa las relaciones de gerente incorporadas de Odoo
- **Validación de Email**: Verifica direcciones de email válidas de gerente
- **Manejo de Errores**: Manejo elegante de gerentes faltantes o direcciones de email
- **Pista de Auditoría**: Registra todos los intentos de notificación y resultados

## Instalación y Configuración

### Prerrequisitos
- Odoo 17.0+
- Módulos requeridos: `hr`, `project`, `hr_timesheet`, `mail`

### Pasos de Instalación
1. Copiar el módulo a su directorio de complementos de Odoo
2. Actualizar la lista de aplicaciones en Odoo
3. Instalar el módulo "Seguimiento de Horas Semanales de Empleados"
4. Configurar las horas semanales esperadas para cada empleado
5. Configurar las relaciones de gerente en los registros de empleados

### Configuración Inicial
1. **Configuración de Empleado**: Establecer horas semanales esperadas para cada empleado (predeterminado: 40)
2. **Asignación de Gerente**: Asegurar que todos los empleados tengan gerentes asignados
3. **Configuración de Email**: Verificar que las direcciones de email de los gerentes sean correctas
4. **Integración de Hoja de Tiempo**: Asegurar que los empleados estén registrando tiempo en proyectos

## Guía de Uso

### Para Administradores de RRHH
1. **Panel de Monitoreo**: Usar la vista de lista de empleados para identificar rápidamente problemas de estado
2. **Revisar Resúmenes**: Acceder al menú de Resumen de Horas Semanales para análisis detallado
3. **Configurar Ajustes**: Ajustar las horas esperadas por empleado según sea necesario
4. **Auditar Notificaciones**: Rastrear qué gerentes han sido notificados sobre problemas

### Para Gerentes
1. **Recibir Alertas**: Notificaciones automáticas por email para discrepancias de miembros del equipo
2. **Revisar Estado del Equipo**: Verificar formularios de empleados para el estado de la semana actual
3. **Análisis Histórico**: Revisar el historial de resumen semanal para patrones
4. **Tomar Acción**: Hacer seguimiento con miembros del equipo basado en información de alerta

### Para Empleados
1. **Visibilidad de Estado**: Ver el estado de la semana actual en el registro de empleado
2. **Seguimiento de Horas**: Ver horas registradas vs. esperadas en tiempo real
3. **Vista Histórica**: Acceder al historial personal de resumen semanal
4. **Transparencia**: Comprensión clara de las expectativas de horas y rendimiento

## Opciones de Personalización

### Umbrales Configurables
- **Horas Esperadas**: Ajustables por empleado (soporta tiempo parcial, contratistas)
- **Niveles de Tolerancia**: Modificar la tolerancia de 2 horas en el código si es necesario
- **Umbrales Críticos**: Ajustar el nivel crítico de 10 horas de tiempo extra
- **Tiempo de Alerta**: Cambiar el tiempo de alerta de jueves/viernes si se desea

### Plantillas de Email
- **Marca**: Personalizar plantillas de email con la marca de la empresa
- **Contenido**: Modificar el contenido y formato de notificación
- **Destinatarios**: Agregar destinatarios CC o modificar la lógica de notificación
- **Idiomas**: Soporte para plantillas de email multiidioma

### Categorías de Estado
- **Estados Personalizados**: Agregar categorías de estado adicionales si es necesario
- **Esquemas de Color**: Modificar indicadores visuales y codificación de colores
- **Lógica de Cálculo**: Ajustar métodos de cálculo de discrepancia
- **Períodos de Reporte**: Modificar definiciones de período semanal (actualmente lunes-domingo)

## Detalles Técnicos

### Estructura de Base de Datos
- **Nuevas Tablas**: `employee_weekly_summary`
- **Tablas Extendidas**: `hr_employee` (solo campos calculados)
- **Relaciones**: Mantiene integridad referencial con datos de RRHH existentes

### Consideraciones de Rendimiento
- **Campos Calculados**: Calculados eficientemente usando consultas de base de datos
- **Procesamiento en Lote**: Resúmenes semanales generados en lote
- **Indexación**: Índices apropiados de base de datos en campos de fecha y empleado
- **Caché**: Aprovecha el caché de campos incorporado de Odoo

### Puntos de Integración
- **Sistema de Hoja de Tiempo**: Integración perfecta con `account.analytic.line`
- **Módulo de RRHH**: Extiende la gestión de empleados existente
- **Módulo de Proyecto**: Respeta el seguimiento de tiempo basado en proyectos
- **Sistema de Correo**: Usa la infraestructura de email de Odoo

## Solución de Problemas

### Problemas Comunes
1. **Notificaciones Faltantes**: Verificar asignaciones de gerente y direcciones de email
2. **Horas Incorrectas**: Verificar que las entradas de hoja de tiempo estén vinculadas a proyectos
3. **Estado No Se Actualiza**: Asegurar que las acciones programadas se estén ejecutando correctamente
4. **Problemas de Acceso**: Verificar asignaciones de grupos de seguridad

### Registro y Depuración
- **Registros del Sistema**: El módulo registra actividades en el sistema de registro de Odoo
- **Manejo de Errores**: Manejo elegante de errores con mensajes informativos
- **Modo de Depuración**: Registro adicional disponible en modo de depuración

## Soporte y Mantenimiento

### Mantenimiento Regular
- **Revisiones Semanales**: Monitorear el proceso de generación de resumen semanal
- **Entregabilidad de Email**: Asegurar que los emails de notificación se estén entregando
- **Limpieza de Datos**: Limpieza periódica de registros de resumen antiguos si es necesario
- **Monitoreo de Rendimiento**: Vigilar cualquier impacto en el rendimiento

### Consideraciones de Actualización
- **Migración de Datos**: Los resúmenes se preservan durante las actualizaciones del módulo
- **Respaldo de Configuración**: Exportar horas esperadas de empleados antes de actualizaciones importantes
- **Pruebas**: Probar la funcionalidad de notificación después de actualizaciones

## Historial de Versiones

### Versión 1.0.0
- Lanzamiento inicial
- Seguimiento básico de horas semanales
- Sistema de notificación a gerentes
- Generación de resumen histórico
- Categorización de estado de empleados

---

## Licencia y Soporte

Este módulo se proporciona tal como está para uso educativo y empresarial. Para soporte, solicitudes de personalización o reportes de errores, por favor contacte a su administrador del sistema o desarrollador del módulo.
