from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Equipo, Partido, Torneo, Jugador, Categoria
from django.utils import timezone
from .forms import EquipoForm

@login_required
def dashboard(request):
    # Obtener estadísticas
    total_equipos = Equipo.objects.count()
    equipos_pagados = Equipo.objects.filter(pago_confirmado=True).count()
    equipos_pendientes = total_equipos - equipos_pagados
    total_partidos = Partido.objects.count()
    
    # Equipos con pago pendiente (máximo 10)
    equipos_pendientes_list = Equipo.objects.filter(
        pago_confirmado=False
    ).select_related('torneo')[:10]
    
    # Próximos partidos (5 próximos)
    hoy = timezone.now().date()
    proximos_partidos = Partido.objects.filter(
        fecha__gte=hoy
    ).select_related('equipo_local', 'equipo_visitante', 'torneo').order_by('fecha', 'hora')[:5]
    
    return render(request, 'dashboard.html', {
        'total_equipos': total_equipos,
        'equipos_pagados': equipos_pagados,
        'equipos_pendientes': equipos_pendientes,
        'equipos_pendientes_list': equipos_pendientes_list,
        'total_partidos': total_partidos,
        'proximos_partidos': proximos_partidos,
    })

@login_required
def inscribir_equipo(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            # Guardar equipo
            equipo = form.save(commit=False)
            equipo.pago_confirmado = False  # Por defecto no pagado
            equipo.save()
            
            # Guardar jugadores
            for i in range(1, 7):
                nombre_jugador = form.cleaned_data.get(f'jugador{i}')
                if nombre_jugador:
                    Jugador.objects.create(
                        equipo=equipo,
                        nombre=nombre_jugador,
                        edad=0  # Podemos agregar campo edad después
                    )
            
            return redirect('dashboard')
    else:
        form = EquipoForm()
    
    return render(request, 'inscribir_equipo.html', {'form': form})

@login_required
def lista_equipos(request):
    # Obtener filtros
    torneo_id = request.GET.get('torneo')
    pago_status = request.GET.get('pago')
    
    # Filtrar equipos
    equipos = Equipo.objects.all().select_related('torneo')
    
    if torneo_id:
        equipos = equipos.filter(torneo_id=torneo_id)
    
    if pago_status == 'pagado':
        equipos = equipos.filter(pago_confirmado=True)
    elif pago_status == 'pendiente':
        equipos = equipos.filter(pago_confirmado=False)
    
    # Obtener torneos para el filtro
    torneos = Torneo.objects.all()
    
    # Estadísticas
    total_equipos = equipos.count()
    pagados = equipos.filter(pago_confirmado=True).count()
    pendientes = total_equipos - pagados
    
    return render(request, 'lista_equipos.html', {
        'equipos': equipos,
        'torneos': torneos,
        'total_equipos': total_equipos,
        'pagados': pagados,
        'pendientes': pendientes,
        'torneo_seleccionado': torneo_id,
        'pago_seleccionado': pago_status,
    })

@login_required
def marcar_pago(request, equipo_id):
    """Marcar/desmarcar pago de un equipo"""
    equipo = get_object_or_404(Equipo, id=equipo_id)
    
    if request.method == 'POST':
        # Cambiar estado de pago
        equipo.pago_confirmado = not equipo.pago_confirmado
        equipo.save()
        
        # Redirigir de vuelta
        return redirect('lista_equipos')
    
    return redirect('lista_equipos')

@login_required
def calendario(request):
    """Vista principal del calendario"""
    # Filtros
    fecha_filtro = request.GET.get('fecha')
    torneo_id = request.GET.get('torneo')
    
    # Obtener partidos
    partidos = Partido.objects.all().select_related(
        'equipo_local', 'equipo_visitante', 'torneo'
    ).order_by('fecha', 'hora')
    
    if fecha_filtro:
        partidos = partidos.filter(fecha=fecha_filtro)
    
    if torneo_id:
        partidos = partidos.filter(torneo_id=torneo_id)
    
    # Obtener fechas únicas para el mini-calendario
    fechas_con_partidos = Partido.objects.dates('fecha', 'day')
    
    # Obtener torneos para filtro
    torneos = Torneo.objects.all()
    
    # Estadísticas
    partidos_hoy = Partido.objects.filter(fecha=timezone.now().date()).count()
    
    return render(request, 'calendario.html', {
        'partidos': partidos,
        'torneos': torneos,
        'fechas_con_partidos': fechas_con_partidos,
        'partidos_hoy': partidos_hoy,
        'fecha_filtro': fecha_filtro,
        'torneo_seleccionado': torneo_id,
        'hoy': timezone.now().date(),
    })

@login_required
def agregar_partido(request):
    """Agregar nuevo partido"""
    if request.method == 'POST':
        torneo_id = request.POST.get('torneo')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        equipo_local_id = request.POST.get('equipo_local')
        equipo_visitante_id = request.POST.get('equipo_visitante')
        
        # Validación básica
        if all([torneo_id, fecha, hora, equipo_local_id, equipo_visitante_id]):
            Partido.objects.create(
                torneo_id=torneo_id,
                fecha=fecha,
                hora=hora,
                equipo_local_id=equipo_local_id,
                equipo_visitante_id=equipo_visitante_id,
            )
            return redirect('calendario')
    
    # Si es GET o error, mostrar formulario
    torneos = Torneo.objects.all()
    equipos = Equipo.objects.all()
    
    return render(request, 'agregar_partido.html', {
        'torneos': torneos,
        'equipos': equipos,
    })
    
@login_required
def lista_torneos(request):
    """Ver y crear torneos simples"""
    torneos = Torneo.objects.all().order_by('-fecha_inicio')
    
    if request.method == 'POST':
        # Crear torneo simple
        nombre = request.POST.get('nombre')
        categoria_id = request.POST.get('categoria')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        precio = request.POST.get('precio', 0)
        
        if nombre and categoria_id and fecha_inicio:
            Torneo.objects.create(
                nombre=nombre,
                categoria_id=categoria_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin or fecha_inicio,
                precio_inscripcion=precio
            )
            return redirect('lista_torneos')
    
    categorias = Categoria.objects.all()
    return render(request, 'lista_torneos.html', {
        'torneos': torneos,
        'categorias': categorias,
    })
    
    
def historial_torneos(request):
    # Obtener torneos finalizados del más reciente al más antiguo
    torneos_finalizados = Torneo.objects.filter(
        estado='finalizado'
    ).order_by('-fecha_fin')
    
    # Pre-cargar datos relacionados para eficiencia
    torneos_con_datos = torneos_finalizados.select_related(
        'categoria', 'campeon'
    ).prefetch_related(
        'equipo_set__jugador_set',  # Incluye jugadores por equipo
        'partido_set'
    )
    
    # Preparar datos para el template
    torneos_procesados = []
    for torneo in torneos_con_datos:
        equipos_con_jugadores = []
        for equipo in torneo.equipo_set.all():
            equipos_con_jugadores.append({
                'equipo': equipo,
                'jugadores': list(equipo.jugador_set.all()[:5]),  # Primeros 5 jugadores
                'total_jugadores': equipo.jugador_set.count()
            })
        
        torneos_procesados.append({
            'torneo': torneo,
            'campeon': torneo.campeon,
            'subcampeon': torneo.partido_set.filter(
                ronda='final', terminado=True
            ).first().perdedor if torneo.partido_set.filter(ronda='final', terminado=True).exists() else None,
            'equipos_con_jugadores': equipos_con_jugadores,
            'total_equipos': torneo.equipo_set.count(),
            'total_partidos': torneo.partido_set.filter(terminado=True).count(),
            'partidos_finales': list(torneo.partido_set.filter(
                ronda__in=['final', 'semifinales']
            ).order_by('ronda')[:3]),
        })
    
    context = {
        'torneos': torneos_procesados,
        'total_torneos': torneos_finalizados.count(),
        'titulo': 'Historial de Torneos Finalizados',
    }
    return render(request, 'torneos/historial.html', context)