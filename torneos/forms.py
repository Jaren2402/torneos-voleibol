from django import forms
from .models import Equipo, Jugador, Torneo

class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ['torneo', 'nombre', 'capitan', 'telefono', 'email']
    
    # Campos para 6 jugadores
    jugador1 = forms.CharField(label='Jugador 1', max_length=100)
    jugador2 = forms.CharField(label='Jugador 2', max_length=100)
    jugador3 = forms.CharField(label='Jugador 3', max_length=100)
    jugador4 = forms.CharField(label='Jugador 4', max_length=100)
    jugador5 = forms.CharField(label='Jugador 5', max_length=100)
    jugador6 = forms.CharField(label='Jugador 6', max_length=100, required=False)