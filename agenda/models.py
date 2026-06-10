from datetime import timedelta
from django.db import models
from pacientes.models import Paciente
from terapeutas.models import Terapeuta
from django.core.exceptions import ValidationError

class AgendaSemanal(models.Model):
    SEGUNDA = 0
    TERCA = 1
    QUARTA = 2
    QUINTA = 3
    SEXTA = 4
    DIA_CHOICES = [
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='agendamentos')
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, related_name='agendamentos')
    tipo_terapia = models.CharField(max_length=100)
    dia_semana = models.IntegerField(choices=DIA_CHOICES)
    horario = models.TimeField()
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Agenda semanal'
        verbose_name_plural = 'Agenda semanal'
        ordering = ['dia_semana', 'horario']
        unique_together = ('paciente', 'terapeuta', 'dia_semana', 'horario')

    def __str__(self):
        return f'{self.get_dia_semana_display()} - {self.horario} - {self.paciente}'

    def clean(self):
        conflito = AgendaSemanal.objects.exclude(pk=self.pk).filter(
            paciente=self.paciente,
            terapeuta=self.terapeuta,
            dia_semana=self.dia_semana,
            horario=self.horario
        ).exists()

        if conflito:
            raise ValidationError(
                'Já existe uma agenda semanal cadastrada para este paciente com este terapeuta, nesse dia e horário.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Atendimento(models.Model):
    NORMAL = 'normal'
    EXTRA = 'extra'
    TIPO_CHOICES = [
        (NORMAL, 'Normal'),
        (EXTRA, 'Extra'),
    ]

    AGENDADO = 'agendado'
    PRESENTE = 'presente'
    FALTA = 'falta'
    FALTA_JUSTIFICADA = 'falta_justificada'
    STATUS_CHOICES = [
        (AGENDADO, 'Agendado'),
        (PRESENTE, 'Presente'),
        (FALTA, 'Falta'),
        (FALTA_JUSTIFICADA, 'Falta justificada'),
    ]

    agenda_semanal = models.ForeignKey(AgendaSemanal, on_delete=models.SET_NULL, null=True, blank=True, related_name='atendimentos')
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='atendimentos')
    terapeuta = models.ForeignKey(Terapeuta, on_delete=models.CASCADE, related_name='atendimentos')
    tipo_terapia = models.CharField(max_length=100)
    data = models.DateField()
    horario = models.TimeField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default=NORMAL)
    status_presenca = models.CharField(max_length=20, choices=STATUS_CHOICES, default=AGENDADO)
    observacao_presenca = models.CharField(max_length=255, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data', 'horario']
        unique_together = ('paciente', 'terapeuta', 'data', 'horario', 'tipo')

    def __str__(self):
        return f'{self.data} {self.horario} - {self.paciente}'
    
    def clean(self):
        conflito_paciente = Atendimento.objects.exclude(pk=self.pk).filter(
            paciente=self.paciente,
            data=self.data,
            horario=self.horario
        ).exists()

        if conflito_paciente:
            raise ValidationError({
                'paciente': 'Já existe atendimento para este paciente nesta data e horário.'
            })

        conflito_terapeuta = Atendimento.objects.exclude(pk=self.pk).filter(
            terapeuta=self.terapeuta,
            data=self.data,
            horario=self.horario
        ).exists()

        if conflito_terapeuta:
            raise ValidationError({
                'terapeuta': 'Já existe atendimento para este terapeuta nesta data e horário.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def gerar_atendimentos_periodo(cls, data_inicial, data_final):
        agendamentos = AgendaSemanal.objects.filter(ativo=True)
        data_atual = data_inicial
        while data_atual <= data_final:
            for ag in agendamentos.filter(dia_semana=data_atual.weekday()):
                cls.objects.get_or_create(
                    agenda_semanal=ag,
                    paciente=ag.paciente,
                    terapeuta=ag.terapeuta,
                    tipo_terapia=ag.tipo_terapia,
                    data=data_atual,
                    horario=ag.horario,
                    tipo=cls.NORMAL,
                )
            data_atual += timedelta(days=1)
