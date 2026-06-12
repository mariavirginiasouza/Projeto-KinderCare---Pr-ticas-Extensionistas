from django import forms
from users.models import User
from .models import Terapeuta


class TerapeutaForm(forms.ModelForm):
    class Meta:
        model = Terapeuta
        fields = ['nome', 'especialidades', 'usuario', 'ativo']
        labels = {
            'nome': 'Nome',
            'especialidades': 'Especialidade',
            'usuario': 'Usuário',
            'ativo': 'Ativo',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do terapeuta'}),
            'especialidades': forms.Select(),
        }
        help_texts = {
            'nome': None,
            'especialidades': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuario'].empty_label = "Escolha um usuário"
        self.fields['usuario'].queryset = User.objects.filter(role=User.TERAPEUTA)
        self.fields['especialidades'].required = True
        self.fields['usuario'].required = True