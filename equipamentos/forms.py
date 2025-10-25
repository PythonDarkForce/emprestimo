from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Requisicao, Equipamento, HistoricoManutencao


class RequisicaoForm(forms.ModelForm):
    """Formulário para criar requisição"""

    class Meta:
        model = Requisicao
        fields = ['equipamentos', 'data_inicio_prevista', 'data_fim_prevista', 'motivo', 'observacoes_requisicao']
        widgets = {
            'data_inicio_prevista': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim_prevista': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'observacoes_requisicao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'equipamentos': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mostrar apenas equipamentos disponíveis
        self.fields['equipamentos'].queryset = Equipamento.objects.filter(estado='disponivel')
        self.fields['observacoes_requisicao'].required = False

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio_prevista')
        data_fim = cleaned_data.get('data_fim_prevista')
        equipamentos = cleaned_data.get('equipamentos')

        # Validar datas
        if data_inicio and data_fim:
            if data_fim < data_inicio:
                raise ValidationError('A data de fim não pode ser anterior à data de início.')

            if data_inicio < timezone.now().date():
                raise ValidationError('A data de início não pode ser no passado.')

        # Validar se selecionou pelo menos um equipamento
        if not equipamentos or equipamentos.count() == 0:
            raise ValidationError('Deve selecionar pelo menos um equipamento.')

        return cleaned_data


class AprovarRequisicaoForm(forms.ModelForm):
    """Formulário para aprovar/rejeitar requisição"""

    DECISAO_CHOICES = [
        ('aprovada', 'Aprovar'),
        ('rejeitada', 'Rejeitar'),
    ]

    decisao = forms.ChoiceField(
        choices=DECISAO_CHOICES,
        widget=forms.RadioSelect,
        label='Decisão'
    )

    class Meta:
        model = Requisicao
        fields = ['decisao', 'observacoes_aprovacao']
        widgets = {
            'observacoes_aprovacao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['observacoes_aprovacao'].required = False

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.estado = self.cleaned_data['decisao']
        if commit:
            instance.save()
        return instance


class DevolucaoForm(forms.ModelForm):
    """Formulário para registar devolução"""

    class Meta:
        model = Requisicao
        fields = ['observacoes_devolucao']
        widgets = {
            'observacoes_devolucao': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Estado do equipamento, eventuais danos, etc.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['observacoes_devolucao'].required = False


class EquipamentoForm(forms.ModelForm):
    """Formulário para adicionar/editar equipamento"""

    class Meta:
        model = Equipamento
        fields = [
            'categoria', 'nome', 'marca', 'modelo', 'numero_serie',
            'codigo_interno', 'descricao', 'estado', 'valor_estimado',
            'data_aquisicao', 'observacoes', 'imagem'
        ]
        widgets = {
            'data_aquisicao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_interno': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'valor_estimado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['descricao'].required = False
        self.fields['observacoes'].required = False
        self.fields['imagem'].required = False


class HistoricoManutencaoForm(forms.ModelForm):
    """Formulário para registar manutenção"""

    class Meta:
        model = HistoricoManutencao
        fields = ['equipamento', 'data', 'tipo', 'descricao', 'custo']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'equipamento': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'custo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['custo'].required = False


class FiltroEquipamentoForm(forms.Form):
    """Formulário para filtrar equipamentos"""

    categoria = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Todas as categorias",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    estado = forms.ChoiceField(
        choices=[('', 'Todos os estados')] + Equipamento.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    busca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome, marca, modelo ou código...'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import CategoriaEquipamento
        self.fields['categoria'].queryset = CategoriaEquipamento.objects.all()