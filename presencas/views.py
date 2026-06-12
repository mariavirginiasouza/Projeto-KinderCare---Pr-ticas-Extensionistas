import calendar
import json
from datetime import date, datetime

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from core.decorators import role_required
from pacientes.models import Paciente

from .models import PresencaAula

MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro',
}

DIAS_PT = [
    'segunda-feira', 'terça-feira', 'quarta-feira',
    'quinta-feira', 'sexta-feira', 'sábado', 'domingo',
]

DIAS_SEMANA_CURTOS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']


@role_required('recepcao', 'coordenacao', 'terapeuta')
def presenca_calendario(request):
    hoje = date.today()
    try:
        ano = int(request.GET.get('ano', hoje.year))
        mes = int(request.GET.get('mes', hoje.month))
        mes = max(1, min(12, mes))
    except (ValueError, TypeError):
        ano, mes = hoje.year, hoje.month

    presencas_mes = (
        PresencaAula.objects
        .filter(data__year=ano, data__month=mes, presente=True)
        .values('data')
        .annotate(total=Count('id'))
    )
    presencas_por_dia = {p['data'].day: p['total'] for p in presencas_mes}

    semanas_data = []
    for semana in calendar.monthcalendar(ano, mes):
        week = []
        for dia in semana:
            if dia == 0:
                week.append(None)
            else:
                data_str = f'{ano}-{mes:02d}-{dia:02d}'
                week.append({
                    'dia': dia,
                    'data_str': data_str,
                    'presentes': presencas_por_dia.get(dia, 0),
                    'eh_hoje': (ano == hoje.year and mes == hoje.month and dia == hoje.day),
                })
        semanas_data.append(week)

    mes_ant = 12 if mes == 1 else mes - 1
    ano_ant = ano - 1 if mes == 1 else ano
    mes_prox = 1 if mes == 12 else mes + 1
    ano_prox = ano + 1 if mes == 12 else ano

    context = {
        'semanas_data': semanas_data,
        'dias_semana': DIAS_SEMANA_CURTOS,
        'ano': ano,
        'mes': mes,
        'mes_nome': MESES_PT[mes],
        'mes_ant': mes_ant,
        'ano_ant': ano_ant,
        'mes_prox': mes_prox,
        'ano_prox': ano_prox,
    }
    return render(request, 'presencas/calendario.html', context)

@role_required('recepcao', 'coordenacao', 'terapeuta')
def presenca_dia(request, data):
    try:
        data_obj = datetime.strptime(data, '%Y-%m-%d').date()
    except ValueError:
        data_obj = date.today()

    pacientes = Paciente.objects.all().order_by('nome')

    presencas_qs = PresencaAula.objects.filter(data=data_obj).select_related('paciente')
    presencas_map = {p.paciente_id: p.presente for p in presencas_qs}

    pacientes_presencas = [(p, presencas_map.get(p.id, False)) for p in pacientes]

    dia_semana = DIAS_PT[data_obj.weekday()].capitalize()
    data_formatada = f"{dia_semana}, {data_obj.day} de {MESES_PT[data_obj.month].lower()} de {data_obj.year}"

    context = {
        'data': data_obj,
        'data_str': data_obj.strftime('%Y-%m-%d'),
        'data_formatada': data_formatada,
        'pacientes_presencas': pacientes_presencas,
    }
    return render(request, 'presencas/dia.html', context)

@role_required('recepcao', 'coordenacao', 'terapeuta')
@require_POST
def toggle_presenca(request):
    try:
        body = json.loads(request.body)
        paciente_id = int(body['paciente_id'])
        data_obj = datetime.strptime(body['data'], '%Y-%m-%d').date()
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'error': 'Dados inválidos.'}, status=400)

    paciente = get_object_or_404(Paciente, pk=paciente_id)
    presenca, _ = PresencaAula.objects.get_or_create(paciente=paciente, data=data_obj)
    presenca.presente = not presenca.presente
    presenca.save()
    return JsonResponse({'presente': presenca.presente})
