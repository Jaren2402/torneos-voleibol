from django.db import models

class Categoria(models.Model):
    """Ejemplo: Sub-15, Sub-17, Libre, Mixto"""
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre

class Torneo(models.Model):
    """Un torneo específico"""
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_inscripcion = models.DecimalField(max_digits=10, decimal_places=2)
    
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
    fecha = models.DateField()
    hora = models.TimeField()
    equipo_local = models.ForeignKey(Equipo, related_name='partidos_local', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Equipo, related_name='partidos_visitante', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['fecha', 'hora']  # Ordenar por fecha y hora
    
    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha}"
