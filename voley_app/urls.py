from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import path, include
from django.contrib.auth import views as auth_views
from torneos.views import dashboard, inscribir_equipo, lista_equipos, marcar_pago, calendario, agregar_partido, lista_torneos, historial_torneos

urlpatterns = [
    path('admin/', admin.site.urls),  # Lo dejamos pero no lo usaremos
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('inscribir/', inscribir_equipo, name='inscribir_equipo'),
    path('', RedirectView.as_view(pattern_name='dashboard')),
    path('equipos/', lista_equipos, name='lista_equipos'),
    path('equipos/<int:equipo_id>/pago/', marcar_pago, name='marcar_pago'),
    path('calendario/', calendario, name='calendario'),
    path('calendario/nuevo/', agregar_partido, name='agregar_partido'),
    path('torneos/', lista_torneos, name='lista_torneos'),
    path('historial/', historial_torneos, name='historial'),
]