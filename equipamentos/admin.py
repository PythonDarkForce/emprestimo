from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CategoriaEquipamento,
    Equipamento,
    Requisicao,
    HistoricoManutencao,
    Acessorio
)


@admin.register(CategoriaEquipamento)
class CategoriaEquipamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao', 'total_equipamentos']
    search_fields = ['nome']

    def total_equipamentos(self, obj):
        return obj.equipamentos.count()

    total_equipamentos.short_description = 'Total de Equipamentos'


class AcessorioInline(admin.TabularInline):
    model = Acessorio
    extra = 1


class HistoricoManutencaoInline(admin.TabularInline):
    model = HistoricoManutencao
    extra = 0
    fields = ['data', 'tipo', 'descricao', 'custo']
    readonly_fields = ['data']


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_interno',
        'nome',
        'marca',
        'modelo',
        'categoria',
        'estado_badge',
        'valor_estimado'
    ]
    list_filter = ['estado', 'categoria', 'data_aquisicao']
    search_fields = ['nome', 'marca', 'modelo', 'codigo_interno', 'numero_serie']
    readonly_fields = ['imagem_preview']
    fieldsets = (
        ('Informação Básica', {
            'fields': ('categoria', 'nome', 'marca', 'modelo')
        }),
        ('Identificação', {
            'fields': ('codigo_interno', 'numero_serie')
        }),
        ('Estado e Valor', {
            'fields': ('estado', 'valor_estimado', 'data_aquisicao')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'observacoes')
        }),
        ('Imagem', {
            'fields': ('imagem', 'imagem_preview'),
            'classes': ('collapse',)
        }),
    )
    inlines = [AcessorioInline, HistoricoManutencaoInline]

    def estado_badge(self, obj):
        cores = {
            'disponivel': 'green',
            'emprestado': 'orange',
            'manutencao': 'red',
            'inativo': 'gray'
        }
        cor = cores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            cor, obj.get_estado_display()
        )

    estado_badge.short_description = 'Estado'

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.imagem.url)
        return "Sem imagem"

    imagem_preview.short_description = 'Pré-visualização'


@admin.register(Requisicao)
class RequisicaoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'utilizador',
        'data_requisicao',
        'data_inicio_prevista',
        'data_fim_prevista',
        'estado_badge',
        'num_equipamentos',
        'esta_atrasada'
    ]
    list_filter = ['estado', 'data_requisicao', 'data_inicio_prevista']
    search_fields = ['utilizador__username', 'utilizador__first_name', 'utilizador__last_name', 'motivo']
    readonly_fields = ['data_requisicao', 'data_aprovacao', 'data_entrega_real', 'data_devolucao_real']
    filter_horizontal = ['equipamentos']

    fieldsets = (
        ('Utilizador e Datas', {
            'fields': ('utilizador', 'data_requisicao', 'data_inicio_prevista', 'data_fim_prevista')
        }),
        ('Equipamentos', {
            'fields': ('equipamentos',)
        }),
        ('Motivo', {
            'fields': ('motivo', 'observacoes_requisicao')
        }),
        ('Aprovação', {
            'fields': ('estado', 'aprovado_por', 'data_aprovacao', 'observacoes_aprovacao')
        }),
        ('Entrega e Devolução', {
            'fields': ('data_entrega_real', 'data_devolucao_real', 'observacoes_devolucao')
        }),
    )

    def estado_badge(self, obj):
        cores = {
            'pendente': 'orange',
            'aprovada': 'blue',
            'rejeitada': 'red',
            'em_curso': 'green',
            'concluida': 'gray',
            'atrasada': 'darkred'
        }
        cor = cores.get(obj.estado, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            cor, obj.get_estado_display()
        )

    estado_badge.short_description = 'Estado'

    def num_equipamentos(self, obj):
        return obj.equipamentos.count()

    num_equipamentos.short_description = 'Nº Equipamentos'


@admin.register(HistoricoManutencao)
class HistoricoManutencaoAdmin(admin.ModelAdmin):
    list_display = ['equipamento', 'data', 'tipo', 'custo', 'responsavel']
    list_filter = ['tipo', 'data']
    search_fields = ['equipamento__nome', 'equipamento__codigo_interno', 'descricao']
    date_hierarchy = 'data'

    fieldsets = (
        ('Informação Básica', {
            'fields': ('equipamento', 'data', 'tipo', 'responsavel')
        }),
        ('Detalhes', {
            'fields': ('descricao', 'custo')
        }),
    )


@admin.register(Acessorio)
class AcessorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'equipamento', 'quantidade']
    list_filter = ['equipamento__categoria']
    search_fields = ['nome', 'equipamento__nome', 'equipamento__codigo_interno']


"""

Este ficheiro configura a ** interface de administração Django ** com personalizações avançadas:

** 5 ModelAdmins Registrados: **

** 1. CategoriaEquipamentoAdmin **
- Lista: nome, descrição, total de equipamentos
- Método custom: `total_equipamentos()` - conta equipamentos da categoria
- Busca: por nome

** 2. EquipamentoAdmin ** (Mais completo)
- Lista: código, nome, marca, modelo, categoria, estado(colorido), valor
- Filtros: estado, categoria, data de aquisição
- Busca: nome, marca, modelo, código, número de série
- ** Inlines **:
- `AcessorioInline` 
- adicionar acessórios direto na página
- `HistoricoManutencaoInline` 
- histórico de manutenção
- ** Fieldsets **: organiza campos em seções colapsáveis
- ** Métodos custom **:
- `estado_badge()` 
- mostra círculo colorido + texto do estado
- `imagem_preview()` 
- preview da
imagem
do
equipamento

** 3.
RequisicaoAdmin **
- Lista: ID, utilizador, datas, estado(colorido), nº
equipamentos, atraso
- Filtros: estado, datas
- Busca: username, nome
completo, motivo
- ** filter_horizontal **: interface
melhorada
para
ManyToMany(equipamentos)
- Campos
readonly: datas
automáticas
- ** Fieldsets **: 5
seções
organizadas(utilizador, equipamentos, motivo, aprovação, entrega)
- ** Métodos
custom **:
- `estado_badge()` - visualização
colorida
do
estado
- `num_equipamentos()` - conta
equipamentos
da
requisição

** 4.
HistoricoManutencaoAdmin **
- Lista: equipamento, data, tipo, custo, responsável
- Filtros: tipo, data
- ** date_hierarchy **: navegação
por
ano / mês / dia
- Busca: equipamento, código, descrição

** 5.
AcessorioAdmin **
- Lista: nome, equipamento, quantidade
- Filtros: categoria
do
equipamento
- Busca: nome, equipamento

** Características
Avançadas: **

✅ ** Badges
coloridos ** com
`format_html()`:
- Verde = disponível
- Laranja = emprestado
- Vermelho = manutenção
- Azul = aprovada
- Cinza = inativo / concluída

✅ ** Inlines ** (edição na mesma página):
- Acessórios
dentro
de
Equipamento
- Histórico
de
manutenção
dentro
de
Equipamento

✅ ** Fieldsets ** organizados:
- Agrupa
campos
relacionados
- Seções
colapsáveis(collapse)

✅ ** filter_horizontal **:
- Interface
drag - and -drop
para
ManyToMany
- Muito
melhor
que
checkbox
list

✅ ** date_hierarchy **:
- Navegação
temporal
no
admin

✅ ** Campos
readonly **:
- Protege
timestamps
automáticos

✅ ** Preview
de
imagem **:
- Mostra
imagem
do
equipamento
no
admin

✅ ** Métodos
custom **:
- Adiciona
colunas
calculadas
- Formatação
personalizada

** Exemplo
de
uso: **
```
Admin → Equipamentos
├─ Ver
lista
com
badges
coloridos
├─ Filtrar
por
estado / categoria
├─ Clicar
em
equipamento
│   ├─ Editar
campos
organizados
em
seções
│   ├─ Ver
preview
da
imagem
│   ├─ Adicionar
acessórios(inline)
│   └─ Adicionar
manutenções(inline)
└─ Buscar
por
código / nome / marca
"""