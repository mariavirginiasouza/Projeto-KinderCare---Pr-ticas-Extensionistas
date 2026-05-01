from django import forms
from .models import AgendaSemanal, Atendimento


class AgendaSemanalForm(forms.ModelForm):
    class Meta:
        model = AgendaSemanal
        fields = [
            'paciente',
            'terapeuta',
            'tipo_terapia',
            'dia_semana',
            'horario',
            'ativo'
        ]

        # Adicionado os labels organizados
        labels = {
            'paciente': 'Paciente',
            'terapeuta': 'Terapeuta',
            'tipo_terapia': 'Tipo de Terapia',
            'dia_semana': 'Dia da Semana',
            'horario': 'Horário de Atendimento',
            'ativo': 'Ativo',
        }

        widgets = {
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paciente'].empty_label = "Escolha um Paciente"
        self.fields['terapeuta'].empty_label = "Escolha um Terapeuta"

        # 2. CORREÇÃO PARA O DIA DA SEMANA:
        # Pega as opções originais e adiciona a frase personalizada no topo
        original_choices = list(self.fields['dia_semana'].choices)

        # Se a primeira opção for a em branco padrão (----------), nós a substituímos
        if original_choices and original_choices[0][0] in (None, ''):
            original_choices[0] = ('', 'Escolha um Dia da Semana')
            self.fields['dia_semana'].choices = original_choices


class PresencaForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = [
            'status_presenca', 
            'observacao_presenca'
        ]

        labels = {
            'status_presenca': 'Status de Presença:',
            'observacao_presenca': 'Observações da Presença:',
        }

        widgets = {
            'observacao_presenca': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Digite aqui observações relevantes...'
            }),
        }



class AtendimentoExtraForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ['paciente', 'terapeuta', 'tipo_terapia',
                  'data', 'horario', 'observacao_presenca']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TimeInput(attrs={'type': 'time'}),
        }
