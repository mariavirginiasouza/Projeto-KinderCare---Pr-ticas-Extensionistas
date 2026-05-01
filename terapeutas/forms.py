from django import forms
from .models import Terapeuta


class TerapeutaForm(forms.ModelForm):
    class Meta:
        model = Terapeuta
        fields = ['nome', 'especialidades', 'usuario', 'ativo']
        labels = {
            'nome': 'Nome',
            'especialidades': 'Especialidades',
            'usuario': 'Usuário',
            'ativo': 'Ativo',
        }

        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite o nome completo do terapeuta', 'required': 'required'}),
            'especialidades': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Altera o texto padrão do "---------"
        self.fields['usuario'].empty_label = "Escolha um usuário"
