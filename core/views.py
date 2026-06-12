import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render

from agenda.models import Atendimento

MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}
from pacientes.models import Paciente
from terapeutas.models import Terapeuta
from users.models import User

MODULOS = [
    {'titulo': 'Usuários',          'descricao': 'Cadastro de usuários, perfis e permissões.',                'url': 'user_list',               'roles': ['coordenacao']},
    {'titulo': 'Pacientes',         'descricao': 'Cadastro de crianças, responsáveis e contatos.',            'url': 'paciente_list',           'roles': ['recepcao', 'coordenacao']},
    {'titulo': 'Terapeutas',        'descricao': 'Cadastro de profissionais e especialidades.',               'url': 'terapeuta_list',          'roles': ['recepcao', 'coordenacao']},
    {'titulo': 'Agenda semanal',    'descricao': 'Horários fixos recorrentes de segunda a sexta.',            'url': 'agenda_list',             'roles': ['recepcao', 'coordenacao']},
    {'titulo': 'Presenças',         'descricao': 'Lista diária para marcar presente, falta e justificativa.', 'url': 'atendimento_diario',      'roles': ['recepcao', 'coordenacao', 'terapeuta']},
    {'titulo': 'Atendimento extra', 'descricao': 'Cadastro de encaixes em horários vagos.',                   'url': 'atendimento_extra_create','roles': ['recepcao', 'coordenacao', 'terapeuta']},
    {'titulo': 'Relatórios',        'descricao': 'Produtividade por terapeuta e período.',                    'url': 'produtividade_view',      'roles': ['coordenacao']},
]


@login_required
def home(request):
    modulos_visiveis = [m for m in MODULOS if request.user.role in m['roles']]
    return render(request, 'core/home.html', {'modulos_visiveis': modulos_visiveis})


@login_required
def dashboard(request):
    hoje = date.today()

    # ── Cards de resumo ───────────────────────────────────────────────────
    total_pacientes   = Paciente.objects.count()
    total_terapeutas  = Terapeuta.objects.filter(ativo=True).count()
    total_usuarios    = User.objects.filter(is_active=True).count()
    atendimentos_hoje = Atendimento.objects.filter(data=hoje).count()

    totais_status = Atendimento.objects.aggregate(
        presentes    = Count('id', filter=Q(status_presenca=Atendimento.PRESENTE)),
        faltas       = Count('id', filter=Q(status_presenca=Atendimento.FALTA)),
        justificadas = Count('id', filter=Q(status_presenca=Atendimento.FALTA_JUSTIFICADA)),
        agendados    = Count('id', filter=Q(status_presenca=Atendimento.AGENDADO)),
    )

    # ── Gráfico 1: atendimentos por dia — últimos 14 dias ─────────────────
    inicio_14d = hoje - timedelta(days=13)
    qs_14d = (
        Atendimento.objects
        .filter(data__gte=inicio_14d)
        .values('data')
        .annotate(
            total     = Count('id'),
            presentes = Count('id', filter=Q(status_presenca=Atendimento.PRESENTE)),
        )
        .order_by('data')
    )
    data_map = {item['data']: item for item in qs_14d}
    labels_14d, totais_14d, presentes_14d = [], [], []
    for i in range(14):
        d = inicio_14d + timedelta(days=i)
        item = data_map.get(d, {})
        labels_14d.append(d.strftime('%d/%m'))
        totais_14d.append(item.get('total', 0))
        presentes_14d.append(item.get('presentes', 0))

    # ── Gráfico 2: distribuição de status (donut) ─────────────────────────
    status_data = [
        totais_status.get('presentes')    or 0,
        totais_status.get('faltas')       or 0,
        totais_status.get('justificadas') or 0,
        totais_status.get('agendados')    or 0,
    ]

    # ── Gráfico 3: top terapeutas no mês atual ────────────────────────────
    qs_terapeutas = (
        Atendimento.objects
        .filter(data__year=hoje.year, data__month=hoje.month)
        .values('terapeuta__nome')
        .annotate(total=Count('id'))
        .order_by('-total')[:8]
    )

    context = {
        'hoje':             hoje,
        'total_pacientes':  total_pacientes,
        'total_terapeutas': total_terapeutas,
        'total_usuarios':   total_usuarios,
        'atendimentos_hoje':atendimentos_hoje,
        'totais_status':    totais_status,

        'chart_labels_14d':    json.dumps(labels_14d),
        'chart_totais_14d':    json.dumps(totais_14d),
        'chart_presentes_14d': json.dumps(presentes_14d),
        'chart_status_data':   json.dumps(status_data),
        'chart_terap_labels':  json.dumps([t['terapeuta__nome'] or '—' for t in qs_terapeutas]),
        'chart_terap_data':    json.dumps([t['total'] for t in qs_terapeutas]),
        'mes_nome':            MESES_PT[hoje.month] + '/' + str(hoje.year),
    }
    return render(request, 'core/dashboard.html', context)
