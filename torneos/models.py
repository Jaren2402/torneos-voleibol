from django.db import models

class Categoria(models.Model):
    """Ejemplo: Sub-15, Sub-17, Libre, Mixto"""
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre

class Torneo(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    
    # NUEVOS CAMPOS
    num_equipos = models.IntegerField(
        choices=[(4, '4 equipos'), (8, '8 equipos'), (16, '16 equipos')],
        default=8
    )
    llave_generada = models.BooleanField(default=False)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('planificacion', 'En planificación'),
            ('en_curso', 'En curso'),
            ('finalizado', 'Finalizado')
        ],
        default='planificacion'
    )
    campeon = models.ForeignKey(
        'Equipo', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='torneos_ganados'
    )
    
    # MÉTODO AQUÍ (4 espacios de indentación)
    def generar_llave(self):
        if self.llave_generada:
            return
        
        # Configuración directa
        config = {
            4: {'semifinales': 2, 'final': 1},
            8: {'cuartos': 4, 'semifinales': 2, 'final': 1},
            16: {'octavos': 8, 'cuartos': 4, 'semifinales': 2, 'final': 1}
        }
        
        if self.num_equipos not in config:
            raise ValueError("Número de equipos no válido")
        
        for ronda, cantidad in config[self.num_equipos].items():
            for i in range(cantidad):
                self.partido_set.create(
                    ronda=ronda,
                    fecha=None,
                    hora=None,
                    equipo_local=None,
                    equipo_visitante=None,
                    terminado=False
                )
        
        self.llave_generada = True
        self.estado = 'en_curso'
        self.save()
        
    # NUEVO MÉTODO - 4 espacios desde el margen
    def asignar_equipos_llave(self):
        """Asigna equipos inscritos a partidos de primera ronda"""
        if not self.llave_generada:
            raise ValueError("Primero genera la llave")
        
        equipos = list(self.equipo_set.all())
        
        if len(equipos) != self.num_equipos:
            raise ValueError(f"Necesitas {self.num_equipos} equipos, tienes {len(equipos)}")
        
        primera_ronda = {
            4: 'semifinales',
            8: 'cuartos',
            16: 'octavos'
        }
        
        partidos = self.partido_set.filter(ronda=primera_ronda[self.num_equipos]).order_by('id')
        
        for i in range(0, len(equipos), 2):
            if i + 1 < len(equipos):
                partido = partidos[i // 2]
                partido.equipo_local = equipos[i]
                partido.equipo_visitante = equipos[i + 1]
                partido.save()    
    
    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

class Equipo(models.Model):
    """Equipo de vóley"""
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    capitan = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    pago_confirmado = models.BooleanField(default=False)  # ¡TU IDEA!
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre

class Jugador(models.Model):
    """Jugador individual dentro de un equipo"""
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    edad = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.nombre} ({self.equipo})"

class Partido(models.Model):
    """Un partido programado"""
    torneo = models.ForeignKey(Torneo, on_delete=models.CASCADE)
    fecha = models.DateField(null=True, blank=True)
    hora = models.TimeField(null=True, blank=True)
    equipo_local = models.ForeignKey(Equipo, null=True, blank=True, related_name='partidos_local', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Equipo, null=True, blank=True, related_name='partidos_visitante', on_delete=models.CASCADE)
    
    # NUEVOS CAMPOS
    ronda = models.CharField(
        max_length=20,
        choices=[
            ('cuartos', 'Cuartos de final'),
            ('semifinales', 'Semifinales'),
            ('final', 'Final'),
            ('terminado', 'Terminado')
        ],
        default='cuartos'
    )
    
    ganador = models.ForeignKey(
        'Equipo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='partidos_ganados'
    )
    
    terminado = models.BooleanField(default=False)
    
    # Método para marcar ganador
    def marcar_ganador(self, equipo_ganador):
        self.ganador = equipo_ganador
        self.terminado = True
        self.save()
        
        # Aquí después agregaremos la lógica para mover a siguiente ronda
        return True
    
    class Meta:
        ordering = ['fecha', 'hora']
    
    def __str__(self):
        if self.terminado and self.ganador:
            return f"{self.equipo_local} vs {self.equipo_visitante} - Ganó: {self.ganador}"
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha}"
