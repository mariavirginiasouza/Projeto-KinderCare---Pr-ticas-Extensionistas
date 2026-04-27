from django.conf import settings
from django.db import models


class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Especialidades'

    def __str__(self):
        return self.nome


class Terapeuta(models.Model):
    nome = models.CharField(max_length=150)
    especialidades = models.ManyToManyField(
        Especialidade, related_name='terapeutas', blank=True)  # ajustar isso depois
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
