from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput,
        required=False,
        # help_text='Preencha para definir ou alterar a senha.'
    )

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
            'password'
        ]

        labels = {
            'username': 'Nome de Usuário',
            'first_name': 'Primeiro Nome',
            'last_name': 'Último Nome',
            'email': 'E-mail',
            'role': 'Cargo',
            'is_active': 'Ativo',
            'is_staff': 'Membro da Equipe Diretiva',
            'password': 'Senha'
        }

        help_texts = {
            'username': None,
            'is_active': None,
            'is_staff': None
        }

        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Defina um nome de usuário', 'required': 'required'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Digite o primeiro nome do usuário', 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Digite o último nome do usuário', 'required': 'required'}),
            'email': forms.TextInput(attrs={'placeholder': 'Digite o email do usuário', 'required': 'required'}),
            'password': forms.TextInput(attrs={'placeholder': 'Defina uma senha para o usuário', 'required': 'required'}),
        }

    # 2. CORRIGIDO: Validação para impedir criação de usuário sem senha
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Se o usuário for novo (não tem ID ainda) e não digitou senha, gera erro
        if not self.instance.pk and not password:
            raise forms.ValidationError(
                "Você precisa definir uma senha para um novo usuário.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        if commit:
            user.save()
            # 3. CORRIGIDO: Salva as relações ManyToMany se houverem
            self.save_m2m()

        return user

