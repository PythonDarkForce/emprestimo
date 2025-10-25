from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class CategoriaEquipamento(models.Model):
    """Categorias de equipamento (Câmeras, Lentes, Iluminação, etc.)"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoria de Equipamento"
        verbose_name_plural = "Categorias de Equipamento"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Equipamento(models.Model):
    """Equipamento disponível para empréstimo"""
    ESTADO_CHOICES = [
        ('disponivel', 'Disponível'),
        ('emprestado', 'Emprestado'),
        ('manutencao', 'Em Manutenção'),
        ('inativo', 'Inativo'),
    ]

    categoria = models.ForeignKey(CategoriaEquipamento, on_delete=models.PROTECT, related_name='equipamentos')
    nome = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)
    codigo_interno = models.CharField(max_length=50, unique=True, help_text="Código de identificação interna")
    descricao = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponivel')
    valor_estimado = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    data_aquisicao = models.DateField()
    observacoes = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='equipamentos/', blank=True, null=True)

    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"
        ordering = ['categoria', 'nome']

    def __str__(self):
        return f"{self.codigo_interno} - {self.nome} ({self.marca} {self.modelo})"

    def esta_disponivel(self):
        return self.estado == 'disponivel'


class Requisicao(models.Model):
    """Requisição/Empréstimo de equipamento"""
    ESTADO_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('em_curso', 'Em Curso'),
        ('concluida', 'Concluída'),
        ('atrasada', 'Atrasada'),
    ]

    utilizador = models.ForeignKey(User, on_delete=models.PROTECT, related_name='requisicoes')
    equipamentos = models.ManyToManyField(Equipamento, related_name='requisicoes')
    data_requisicao = models.DateTimeField(auto_now_add=True)
    data_inicio_prevista = models.DateField()
    data_fim_prevista = models.DateField()
    data_entrega_real = models.DateTimeField(null=True, blank=True)
    data_devolucao_real = models.DateTimeField(null=True, blank=True)

    motivo = models.TextField(help_text="Motivo/projeto para o qual necessita do equipamento")
    observacoes_requisicao = models.TextField(blank=True)
    observacoes_aprovacao = models.TextField(blank=True)
    observacoes_devolucao = models.TextField(blank=True)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendente')
    aprovado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='requisicoes_aprovadas')
    data_aprovacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Requisição"
        verbose_name_plural = "Requisições"
        ordering = ['-data_requisicao']

    def __str__(self):
        return f"Requisição #{self.id} - {self.utilizador.get_full_name() or self.utilizador.username}"

    def esta_atrasada(self):
        """Verifica se a requisição está atrasada"""
        if self.estado == 'em_curso' and self.data_fim_prevista:
            return timezone.now().date() > self.data_fim_prevista
        return False

    def duracao_prevista(self):
        """Calcula a duração prevista em dias"""
        if self.data_inicio_prevista and self.data_fim_prevista:
            return (self.data_fim_prevista - self.data_inicio_prevista).days
        return 0


class HistoricoManutencao(models.Model):
    """Histórico de manutenção dos equipamentos"""
    TIPO_CHOICES = [
        ('preventiva', 'Manutenção Preventiva'),
        ('corretiva', 'Manutenção Corretiva'),
        ('limpeza', 'Limpeza'),
        ('calibracao', 'Calibração'),
        ('outro', 'Outro'),
    ]

    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='historico_manutencao')
    data = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descricao = models.TextField()
    custo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)],
                                null=True, blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Histórico de Manutenção"
        verbose_name_plural = "Históricos de Manutenção"
        ordering = ['-data']

    def __str__(self):
        return f"{self.equipamento.codigo_interno} - {self.get_tipo_display()} ({self.data})"


class Acessorio(models.Model):
    """Acessórios associados a equipamentos (baterias, cartões, cabos, etc.)"""
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='acessorios')
    nome = models.CharField(max_length=200)
    quantidade = models.PositiveIntegerField(default=1)
    descricao = models.TextField(blank=True)

    class Meta:
        verbose_name = "Acessório"
        verbose_name_plural = "Acessórios"

    def __str__(self):
        return f"{self.nome} ({self.quantidade}x) - {self.equipamento.codigo_interno}"


"""

Este
ficheiro
define ** 5
modelos
Django ** que
representam
a
estrutura
do
banco
de
dados:

** Modelos: **

1. ** CategoriaEquipamento ** - Organização
de
equipamentos
- Campos: nome, descrição
- Ex: Câmeras, Lentes, Iluminação, Áudio, Estabilização

2. ** Equipamento ** - Catálogo
de
equipamentos
- Campos: categoria, nome, marca, modelo, número
de
série, código
interno
- Estados: disponível, emprestado, em
manutenção, inativo
- Campos
extras: descrição, valor, data
aquisição, imagem
- Método: `esta_disponivel()` - verifica
se
pode
ser
requisitado

3. ** Requisicao ** - Empréstimos / requisições
- Relações: utilizador, equipamentos(ManyToMany)
- Datas: requisição, início
prevista, fim
prevista, entrega
real, devolução
real
- Estados: pendente, aprovada, rejeitada, em
curso, concluída, atrasada
- Observações: requisição, aprovação, devolução
- Métodos:
- `esta_atrasada()` - verifica
atraso
- `duracao_prevista()` - calcula
duração
em
dias

4. ** HistoricoManutencao ** - Registo
de
manutenções
- Campos: equipamento, data, tipo, descrição, custo, responsável
- Tipos: preventiva, corretiva, limpeza, calibração, outro
- Útil
para
rastrear
custos
e
histórico
de
cada
equipamento

5. ** Acessorio ** - Acessórios
dos
equipamentos
- Campos: equipamento, nome, quantidade, descrição
- Ex: Baterias(2
x), Cartão
SD
64
GB, Cabo
HDMI

** Características: **

- ✅ ** Related
names ** para
navegação
reversa
- ✅ ** Validators ** (valores positivos)
- ✅ ** Choices ** para
estados
e
tipos
- ✅ ** Meta
classes ** com
ordenação
e
nomes
verbosos
- ✅ ** Métodos
helper ** para
lógica
de
negócio
- ✅ ** Foreign
Keys ** com
proteção
adequada(PROTECT, CASCADE, SET_NULL)
- ✅ ** auto_now_add ** para
timestamps
automáticos

** Relações: **
```
CategoriaEquipamento(1) ←→ (N)
Equipamento
Equipamento(N) ←→ (N)
Requisicao
User(1) ←→ (N)
Requisicao
Equipamento(1) ←→ (N)
HistoricoManutencao
Equipamento(1) ←→ (N)
Acessorio
"""