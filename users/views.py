from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from core.decorators import role_required
from .forms import PasswordSetForm, UserForm

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


def _send_password_setup_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    link = request.build_absolute_uri(f'/usuarios/definir-senha/{uid}/{token}/')
    subject = 'KinderCare+ - Defina sua senha'
    message = (
        f'Olá, {user.get_full_name() or user.username}!\n\n'
        f'Sua conta foi criada no sistema KinderCare+.\n'
        f'Clique no link abaixo para definir sua senha de acesso:\n\n'
        f'{link}\n\n'
        f'Este link é válido por 3 dias.\n\n'
        f'KinderCare+ - Centro de Integração da Criança Especial'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


@role_required('coordenacao')
def user_list(request):
    busca = request.GET.get('q', '')
    usuarios = User.objects.all().order_by('first_name', 'username')
    if busca:
        usuarios = (
            usuarios.filter(username__icontains=busca)
            | usuarios.filter(first_name__icontains=busca)
            | usuarios.filter(last_name__icontains=busca)
        )
    return render(request, 'users/list.html', {'usuarios': usuarios, 'busca': busca})


@role_required('coordenacao')
def user_create(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_unusable_password()
        user.save()
        form.save_m2m()
        try:
            _send_password_setup_email(request, user)
            messages.success(
                request,
                f'Usuário criado com sucesso! Um email foi enviado para {user.email} com o link para definição de senha.'
            )
        except Exception as e:
            messages.warning(request, f'Usuário criado, mas erro ao enviar email: {str(e)}')
        return redirect('user_list')
    return render(request, 'users/form.html', {'form': form, 'titulo': 'Novo usuário'})


@role_required('coordenacao')
def user_update(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST or None, instance=usuario)
    if form.is_valid():
        form.save()
        return redirect('user_list')
    return render(request, 'users/form.html', {'form': form, 'titulo': 'Editar usuário', 'usuario': usuario})


@role_required('coordenacao')
def user_send_password_email(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    try:
        _send_password_setup_email(request, usuario)
        messages.success(request, f'Email de definição de senha enviado para {usuario.email}.')
    except Exception as e:
        messages.error(request, f'Erro: {str(e)}') 
    return redirect('user_list')


@role_required('coordenacao')
def user_delete(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        return redirect('user_list')
    return render(request, 'confirm_delete.html', {'obj': usuario, 'titulo': 'Excluir usuário'})


def password_set(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is None or not token_generator.check_token(user, token):
        return render(request, 'users/link_invalido.html')

    form = PasswordSetForm(request.POST or None)
    if form.is_valid():
        user.set_password(form.cleaned_data['nova_senha'])
        user.save()
        messages.success(request, 'Senha definida com sucesso! Faça seu login para acessar o sistema.')
        return redirect('login')

    return render(request, 'users/definir_senha.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        try:
            user = User.objects.get(username=username)
            try:
                _forgot_password_setup_email(request, user)
                messages.success(request, f'Email enviado para {user.email} com o link para redefinir sua senha.')
            except Exception as e:
                messages.error(request, f'Não foi possível enviar o email: {str(e)}')
        except User.DoesNotExist:
            messages.success(request, 'Se esse usuário existir, um email será enviado.')
        return redirect('forgot_password')
    return render(request, 'users/forgot_password.html')

def _forgot_password_setup_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    link = request.build_absolute_uri(f'/usuarios/definir-senha/{uid}/{token}/')
    subject = 'KinderCare+ - Redefina sua senha'
    message = (
        f'Olá, {user.get_full_name() or user.username}!\n\n'
        f'Clique no link abaixo para redefinir sua senha de acesso:\n\n'
        f'{link}\n\n'
        f'Este link é válido por 3 dias.\n\n'
        f'KinderCare+ - Centro de Integração da Criança Especial'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])