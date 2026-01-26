from django.contrib import admin
from .models import Categoria, Torneo, Equipo, Jugador, Partido

class JugadorInline(admin.TabularInline):
    """Para agregar jugadores directamente al crear equipo"""
    model = Jugador
    extra = 6  # 6 jugadores por equipo (ajusta si quieres)
    max_num = 12  # Máximo de jugadores

class EquipoAdmin(admin.ModelAdmin):
    """Configuración especial para Equipos"""
    list_display = ['nombre', 'torneo', 'capitan', 'pago_confirmado']
    list_filter = ['pago_confirmado', 'torneo']
    search_fields = ['nombre', 'capitan']
    inlines = [JugadorInline]  # ¡Jugadores dentro del Equipo!

class PartidoAdmin(admin.ModelAdmin):
    """Configuración especial para Partidos"""
    list_display = ['torneo', 'ronda', 'equipo_local', 'equipo_visitante', 'estado_partido', 'fecha', 'hora', 'acciones']
    list_filter = ['fecha', 'torneo', 'ronda', 'terminado']
    ordering = ['fecha', 'hora']
    
    def estado_partido(self, obj):
        """Muestra un emoji según el estado"""
        if obj.terminado:
            return '✅ Terminado'
        elif obj.equipo_local and obj.equipo_visitante:
            return '⏳ Programado'
        else:
            return '🔄 Por llenar'
    estado_partido.short_description = 'Estado'
    
    def acciones(self, obj):
        """Botón para marcar ganador (solo si el partido está listo)"""
        if not obj.terminado and obj.equipo_local and obj.equipo_visitante:
            # Generar URL para la acción personalizada
            from django.urls import reverse
            from django.utils.html import format_html
            
            url = reverse('admin:marcar_ganador', args=[obj.id])
            return format_html(
                '<a class="button" href="{}" style="background: #2c5282; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: 500; display: inline-block; min-width: 140px; text-align: center; border: none;">🏆 Marcar Ganador</a>',
                url
            )
        return '-'
    acciones.short_description = 'Acciones'
    
    # Agregar URL personalizada para marcar ganador  # ← 4 ESPACIOS AQUÍ, NO 8
    def get_urls(self):  # ← 4 ESPACIOS
        from django.urls import path
        
        urls = super().get_urls()
        custom_urls = [
            path('<int:partido_id>/marcar_ganador/',
                 self.admin_site.admin_view(self.marcar_ganador_view),
                 name='marcar_ganador'),
        ]
        return custom_urls + urls
    
    def marcar_ganador_view(self, request, partido_id):  # ← 4 ESPACIOS
        """Vista para mostrar formulario de selección de ganador"""
        from django.shortcuts import render, redirect, get_object_or_404
        from django.contrib import messages
        from .models import Partido
        
        partido = get_object_or_404(Partido, id=partido_id)
        
        if request.method == 'POST':
            # Determinar qué equipo ganó
            if 'ganador_local' in request.POST:
                equipo_ganador = partido.equipo_local
            elif 'ganador_visitante' in request.POST:
                equipo_ganador = partido.equipo_visitante
            else:
                messages.error(request, '❌ No se seleccionó ningún ganador')
                return redirect('admin:torneos_partido_changelist')
            
            # Usar tu método avanzar_ganador
            try:
                resultado = partido.torneo.avanzar_ganador(partido, equipo_ganador)
                messages.success(request, resultado)
            except Exception as e:
                messages.error(request, f'❌ Error: {e}')
            
            return redirect('admin:torneos_partido_changelist')
        
        # GET: Mostrar la página de selección
        return render(request, 'admin/marcar_ganador.html', {
            'partido': partido,
            'title': f'Marcar ganador: {partido}',
        })

# Registra todos los modelos

# Registra todos los modelos
admin.site.register(Categoria)
admin.site.register(Torneo)  # ← SIN TorneoAdmin
admin.site.register(Equipo, EquipoAdmin)
admin.site.register(Partido, PartidoAdmin)
# Jugador no necesita registro aparte (está dentro de Equipo)

# Cambiar títulos
admin.site.site_header = "🏐 GESTIÓN DE TORNEOS DE VÓLEY"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Bienvenido al Sistema"

# ===== BOTÓN PARA PROFESORES =====
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

class TorneoAdminSimple(admin.ModelAdmin):
    """Admin simple con solo el botón que necesitan los profesores"""
    list_display = ('nombre', 'categoria', 'num_equipos', 'estado', 'campeon', 'boton_preparar')
    
    def boton_preparar(self, obj):
        """Botón que prepara todo el torneo automáticamente"""
        from django.urls import reverse
        
        # Si ya tiene llave, mostrar mensaje
        if obj.llave_generada:
            return format_html(
                '<span style="color: #666; padding: 5px 10px;">✅ Llave lista</span>'
            )
        
        # Si no tiene equipos suficientes
        if obj.equipo_set.count() < obj.num_equipos:
            return format_html(
                '<span style="color: #f00; padding: 5px 10px;">⚠️ Faltan equipos</span>'
            )
        
        # Botón para preparar torneo
        url = reverse('admin:preparar_torneo', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" style="background: #4299e1; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 500; display: inline-block; min-width: 160px; text-align: center; border: none;">🎯 PREPARAR TORNEO</a>',
            url
        )
    boton_preparar.short_description = 'Acción'
    
    def get_urls(self):
        urls = super().get_urls()
        
        def preparar_torneo_view(request, torneo_id):
            from .models import Torneo
            torneo = Torneo.objects.get(id=torneo_id)
            
            try:
                # 1. Generar llave
                torneo.generar_llave()
                
                # 2. Asignar equipos (si hay suficientes)
                if torneo.equipo_set.count() >= torneo.num_equipos:
                    torneo.asignar_equipos_llave()
                    messages.success(request, f'✅ Torneo "{torneo.nombre}" listo. Se crearon {torneo.partido_set.count()} partidos con equipos asignados.')
                else:
                    messages.warning(request, f'⚠️ Se creó la llave pero faltan equipos. Necesitas {torneo.num_equipos}, tienes {torneo.equipo_set.count()}.')
                    
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
            
            return redirect('admin:torneos_torneo_changelist')
        
        custom_urls = [
            path('<int:torneo_id>/preparar/',
                 self.admin_site.admin_view(preparar_torneo_view),
                 name='preparar_torneo'),
        ]
        return custom_urls + urls

# Re-registrar Torneo con la nueva configuración SIMPLE
admin.site.unregister(Torneo)
admin.site.register(Torneo, TorneoAdminSimple)
