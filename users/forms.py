from django import forms
from django.contrib.auth import get_user_model, password_validation

User = get_user_model()

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'is_active',
            'is_staff',
        ]

        labels = {
            'username': 'Nome de Usuário',
            'first_name': 'Primeiro Nome',
            'last_name': 'Último Nome',
            'email': 'E-mail',
            'role': 'Cargo',
            'is_active': 'Ativo',
            'is_staff': 'Membro da Equipe Diretiva',
        }

        help_texts = {
            'username': None,
            'is_active': None,
            'is_staff': None,
        }

        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Defina um nome de usuário', 'required': 'required'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Digite o primeiro nome do usuário', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Digite o último nome do usuário', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Digite o email do usuário', 'required': 'required'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe um usuário com esse nome de usuário.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe um usuário com esse e-mail.')
        return email

class PasswordSetForm(forms.Form):
    nova_senha = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Digite sua nova senha'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirme sua nova senha'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        if nova_senha and confirmar_senha and nova_senha != confirmar_senha:
            raise forms.ValidationError('As senhas não coincidem.')
        if nova_senha:
            password_validation.validate_password(nova_senha)
        return cleaned_data
