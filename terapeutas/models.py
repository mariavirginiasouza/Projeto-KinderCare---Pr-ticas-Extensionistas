from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

ESPECIALIDADES_CHOICES = [
    ('', 'Selecione uma especialidade'),
    ('Fonoaudiologia', 'Fonoaudiologia'),
    ('Terapia Ocupacional', 'Terapia Ocupacional'),
    ('Fisioterapia', 'Fisioterapia'),
    ('Psicologia', 'Psicologia'),
    ('Psicopedagogia', 'Psicopedagogia'),
    ('Neuropsicologia', 'Neuropsicologia'),
    ('Musicoterapia', 'Musicoterapia'),
    ('Hidroterapia', 'Hidroterapia'),
    ('ABA (Análise do Comportamento Aplicada)', 'ABA (Análise do Comportamento Aplicada)'),
    ('Educação Especial', 'Educação Especial'),
    ('Neuropediatria', 'Neuropediatria'),
    ('Nutrição', 'Nutrição'),
]

class Terapeuta(models.Model):
    nome = models.CharField(max_length=150)
    especialidades = models.CharField(
    max_length=255,
    choices=ESPECIALIDADES_CHOICES,
    blank=True,
    null=True
)
    usuario = models.OneToOneField(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)
    ativo = models.BooleanField(default=True)

    def clean(self):
        if not self.especialidades:
            raise ValidationError({'especialidades': 'Selecione uma especialidade.'})

        if not self.usuario:
            raise ValidationError({'usuario': 'Selecione um usuário para o terapeuta.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
    