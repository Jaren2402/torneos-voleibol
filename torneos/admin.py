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
    list_display = ['fecha', 'hora', 'equipo_local', 'equipo_visitante', 'torneo']
    list_filter = ['fecha', 'torneo']
    ordering = ['fecha', 'hora']

# Registra todos los modelos
admin.site.register(Categoria)
admin.site.register(Torneo)
admin.site.register(Equipo, EquipoAdmin)
admin.site.register(Partido, PartidoAdmin)
# Jugador no necesita registro aparte (está dentro de Equipo)

# Cambiar títulos
admin.site.site_header = "🏐 GESTIÓN DE TORNEOS DE VÓLEY"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Bienvenido al Sistema"

