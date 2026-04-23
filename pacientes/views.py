from django.shortcuts import get_object_or_404, redirect, render
from core.decorators import role_required
from .forms import PacienteForm
from .models import Paciente


@role_required('recepcao', 'coordenacao', 'terapeuta')
def paciente_list(request):
    busca = request.GET.get('q', '')
    pacientes = Paciente.objects.all().prefetch_related('terapeutas_responsaveis')
    if request.user.role == 'terapeuta':
        pacientes = pacientes.filter(
            terapeutas_responsaveis__usuario=request.user).distinct()
    if busca:
        pacientes = pacientes.filter(nome__icontains=busca)
    return render(request, 'pacientes/list.html', {'pacientes': pacientes, 'busca': busca})


@role_required('recepcao', 'coordenacao')
def paciente_create(request):
    form = PacienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('paciente_list')
    return render(request, 'pacientes/form.html', {'form': form, 'titulo': 'Cadastrar novo paciente'})


@role_required('recepcao', 'coordenacao')
def paciente_update(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente)
    if form.is_valid():
        form.save()
        return redirect('paciente_list')
    return render(request, 'pacientes/form.html', {'form': form, 'titulo': 'Editar paciente'})


@role_required('recepcao', 'coordenacao')
def paciente_delete(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        paciente.delete()
        return redirect('paciente_list')
    return render(request, 'confirm_delete.html', {'obj': paciente, 'titulo': 'Excluir paciente'})
