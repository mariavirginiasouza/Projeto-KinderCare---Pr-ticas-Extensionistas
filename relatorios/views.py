from datetime import date, datetime
from django.shortcuts import render
from core.decorators import role_required
from agenda.models import Atendimento
from terapeutas.models import Terapeuta
from pacientes.models import Paciente
from presencas.models import PresencaAula


@role_required('coordenacao')
def produtividade_view(request):
    hoje = date.today()
    inicio = request.GET.get('inicio') or hoje.replace(day=1).isoformat()
    fim = request.GET.get('fim') or hoje.isoformat()
    inicio_dt = datetime.strptime(inicio, '%Y-%m-%d').date()
    fim_dt = datetime.strptime(fim, '%Y-%m-%d').date()

    dados_terapeutas = []
    for terapeuta in Terapeuta.objects.all():
        atendimentos = terapeuta.atendimentos.filter(data__range=[inicio_dt, fim_dt])
        total_agendado = atendimentos.count()
        realizados = atendimentos.filter(status_presenca=Atendimento.PRESENTE).count()
        faltas = atendimentos.filter(status_presenca=Atendimento.FALTA).count()
        faltas_justificadas = atendimentos.filter(status_presenca=Atendimento.FALTA_JUSTIFICADA).count()
        extras = atendimentos.filter(tipo=Atendimento.EXTRA).count()
        produtividade = round((realizados / total_agendado) * 100, 2) if total_agendado else 0
        dados_terapeutas.append({
            'nome': terapeuta.nome,
            'total_agendado': total_agendado,
            'realizados': realizados,
            'faltas': faltas,
            'faltas_justificadas': faltas_justificadas,
            'extras': extras,
            'produtividade': produtividade,
        })

    dados_pacientes = []
    for paciente in Paciente.objects.all():
        atendimentos = paciente.atendimentos.filter(data__range=[inicio_dt, fim_dt])
        total_agendado = atendimentos.count()
        realizados = atendimentos.filter(status_presenca=Atendimento.PRESENTE).count()
        faltas = atendimentos.filter(status_presenca=Atendimento.FALTA).count()
        faltas_justificadas = atendimentos.filter(status_presenca=Atendimento.FALTA_JUSTIFICADA).count()
        extras = atendimentos.filter(tipo=Atendimento.EXTRA).count()
        presenca = round((realizados / total_agendado) * 100, 2) if total_agendado else 0
        dados_pacientes.append({
            'nome': paciente.nome,
            'responsavel': paciente.responsavel,
            'total_agendado': total_agendado,
            'realizados': realizados,
            'faltas': faltas,
            'faltas_justificadas': faltas_justificadas,
            'extras': extras,
            'presenca': presenca,
        })

    dados_aulas = []
    for paciente in Paciente.objects.all():
        presencas = PresencaAula.objects.filter(paciente=paciente, data__range=[inicio_dt, fim_dt])
        total = presencas.count()
        presentes = presencas.filter(presente=True).count()
        ausentes = total - presentes
        percentual = round((presentes / total) * 100, 2) if total else 0
        dados_aulas.append({
            'nome': paciente.nome,
            'total': total,
            'presentes': presentes,
            'ausentes': ausentes,
            'percentual': percentual,
        })

    return render(request, 'relatorios/produtividade.html', {
        'dados_terapeutas': dados_terapeutas,
        'dados_pacientes': dados_pacientes,
        'dados_aulas': dados_aulas,
        'inicio': inicio,
        'fim': fim,
        'aba': request.GET.get('aba', 'terapeutas'),
    })
