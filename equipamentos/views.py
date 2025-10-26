from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
import json
import logging
from .models import Equipamento, Requisicao, CategoriaEquipamento, HistoricoManutencao
from .forms import RequisicaoForm, AprovarRequisicaoForm, DevolucaoForm, EquipamentoForm
from .services import processar_devolucao

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Dashboard principal"""
    # Estatísticas gerais
    total_equipamentos = Equipamento.objects.count()
    equipamentos_disponiveis = Equipamento.objects.filter(estado='disponivel').count()
    equipamentos_emprestados = Equipamento.objects.filter(estado='emprestado').count()

    # Requisições do utilizador
    minhas_requisicoes = Requisicao.objects.filter(utilizador=request.user).order_by('-data_requisicao')[:5]

    # Requisições atrasadas (se for staff)
    requisicoes_atrasadas = []
    if request.user.is_staff:
        requisicoes_atrasadas = Requisicao.objects.filter(
            estado='em_curso',
            data_fim_prevista__lt=timezone.now().date()
        )

    context = {
        'total_equipamentos': total_equipamentos,
        'equipamentos_disponiveis': equipamentos_disponiveis,
        'equipamentos_emprestados': equipamentos_emprestados,
        'minhas_requisicoes': minhas_requisicoes,
        'requisicoes_atrasadas': requisicoes_atrasadas,
    }
    return render(request, 'equipamentos/dashboard.html', context)


@login_required
def listar_equipamentos(request):
    """Lista todos os equipamentos disponíveis"""
    equipamentos = Equipamento.objects.all()

    # Filtros
    categoria_id = request.GET.get('categoria')
    estado = request.GET.get('estado')
    busca = request.GET.get('busca')

    if categoria_id:
        equipamentos = equipamentos.filter(categoria_id=categoria_id)

    if estado:
        equipamentos = equipamentos.filter(estado=estado)

    if busca:
        equipamentos = equipamentos.filter(
            Q(nome__icontains=busca) |
            Q(marca__icontains=busca) |
            Q(modelo__icontains=busca) |
            Q(codigo_interno__icontains=busca)
        )

    categorias = CategoriaEquipamento.objects.all()

    context = {
        'equipamentos': equipamentos,
        'categorias': categorias,
        'categoria_selecionada': categoria_id,
        'estado_selecionado': estado,
        'busca': busca,
    }
    return render(request, 'equipamentos/listar_equipamentos.html', context)


@login_required
def detalhe_equipamento(request, pk):
    """Detalhes de um equipamento específico"""
    equipamento = get_object_or_404(Equipamento, pk=pk)
    historico_manutencao = equipamento.historico_manutencao.all()[:10]
    requisicoes_recentes = equipamento.requisicoes.all()[:10]

    context = {
        'equipamento': equipamento,
        'historico_manutencao': historico_manutencao,
        'requisicoes_recentes': requisicoes_recentes,
    }
    return render(request, 'equipamentos/detalhe_equipamento.html', context)


@login_required
def criar_requisicao(request):
    """Criar nova requisição de equipamento"""
    if request.method == 'POST':
        form = RequisicaoForm(request.POST)
        if form.is_valid():
            requisicao = form.save(commit=False)
            requisicao.utilizador = request.user
            requisicao.save()
            form.save_m2m()  # Salvar os equipamentos (ManyToMany)

            messages.success(request, 'Requisição criada com sucesso! Aguarde aprovação.')
            return redirect('minhas_requisicoes')
    else:
        form = RequisicaoForm()

    return render(request, 'equipamentos/criar_requisicao.html', {'form': form})


@login_required
def minhas_requisicoes(request):
    """Lista as requisições do utilizador"""
    requisicoes = Requisicao.objects.filter(utilizador=request.user).order_by('-data_requisicao')

    context = {
        'requisicoes': requisicoes,
    }
    return render(request, 'equipamentos/minhas_requisicoes.html', context)


@login_required
def detalhe_requisicao(request, pk):
    """Detalhes de uma requisição"""
    requisicao = get_object_or_404(Requisicao, pk=pk)

    # Verificar permissões
    if not request.user.is_staff and requisicao.utilizador != request.user:
        return HttpResponseForbidden("Não tem permissão para ver esta requisição.")

    context = {
        'requisicao': requisicao,
    }
    return render(request, 'equipamentos/detalhe_requisicao.html', context)


@user_passes_test(lambda u: u.is_staff)
def listar_requisicoes_pendentes(request):
    """Lista requisições pendentes (apenas staff)"""
    requisicoes = Requisicao.objects.filter(estado='pendente').order_by('data_requisicao')

    context = {
        'requisicoes': requisicoes,
    }
    return render(request, 'equipamentos/requisicoes_pendentes.html', context)


@user_passes_test(lambda u: u.is_staff)
def aprovar_requisicao(request, pk):
    """Aprovar ou rejeitar requisição (apenas staff)"""
    requisicao = get_object_or_404(Requisicao, pk=pk)

    if request.method == 'POST':
        form = AprovarRequisicaoForm(request.POST, instance=requisicao)
        if form.is_valid():
            requisicao = form.save(commit=False)
            requisicao.aprovado_por = request.user
            requisicao.data_aprovacao = timezone.now()

            # Se aprovado, marcar equipamentos como emprestados
            if requisicao.estado == 'aprovada':
                requisicao.equipamentos.all().update(estado='emprestado')
                messages.success(request, 'Requisição aprovada com sucesso!')
            else:
                messages.info(request, 'Requisição rejeitada.')

            requisicao.save()
            return redirect('listar_requisicoes_pendentes')
    else:
        form = AprovarRequisicaoForm(instance=requisicao)

    context = {
        'form': form,
        'requisicao': requisicao,
    }
    return render(request, 'equipamentos/aprovar_requisicao.html', context)


@user_passes_test(lambda u: u.is_staff)
def registar_entrega(request, pk):
    """Registar entrega de equipamento (apenas staff)"""
    requisicao = get_object_or_404(Requisicao, pk=pk)

    if requisicao.estado != 'aprovada':
        messages.error(request, 'Esta requisição não está aprovada.')
        return redirect('detalhe_requisicao', pk=pk)

    requisicao.data_entrega_real = timezone.now()
    requisicao.estado = 'em_curso'
    requisicao.save()

    messages.success(request, 'Entrega registada com sucesso!')
    return redirect('detalhe_requisicao', pk=pk)


@user_passes_test(lambda u: u.is_staff)
def registar_devolucao(request, pk):
    """Registar devolução de equipamento (apenas staff)"""
    requisicao = get_object_or_404(Requisicao, pk=pk)

    if request.method == 'POST':
        form = DevolucaoForm(request.POST, instance=requisicao)
        if form.is_valid():
            requisicao = form.save(commit=False)
            requisicao.data_devolucao_real = timezone.now()
            requisicao.estado = 'concluida'
            requisicao.save()

            # Marcar equipamentos como disponíveis novamente
            requisicao.equipamentos.all().update(estado='disponivel')

            messages.success(request, 'Devolução registada com sucesso!')
            return redirect('detalhe_requisicao', pk=pk)
    else:
        form = DevolucaoForm(instance=requisicao)

    context = {
        'form': form,
        'requisicao': requisicao,
    }
    return render(request, 'equipamentos/registar_devolucao.html', context)


@user_passes_test(lambda u: u.is_staff)
def relatorio_equipamentos(request):
    """Relatório de utilização de equipamentos"""
    equipamentos = Equipamento.objects.annotate(
        num_requisicoes=Count('requisicoes')
    ).order_by('-num_requisicoes')

    context = {
        'equipamentos': equipamentos,
    }
    return render(request, 'equipamentos/relatorio_equipamentos.html', context)


@login_required
@require_http_methods(["GET"])
def api_contadores(request):
    """API para obter contadores em tempo real"""
    contadores = {
        'total_equipamentos': Equipamento.objects.count(),
        'equipamentos_disponiveis': Equipamento.objects.filter(estado='disponivel').count(),
        'equipamentos_emprestados': Equipamento.objects.filter(estado='emprestado').count(),
    }

    if request.user.is_staff:
        contadores.update({
            'requisicoes_pendentes': Requisicao.objects.filter(estado='pendente').count(),
            'requisicoes_atrasadas': Requisicao.objects.filter(
                estado='em_curso',
                data_fim_prevista__lt=timezone.now().date()
            ).count(),
        })

    # Requisições do utilizador
    contadores['minhas_requisicoes_ativas'] = Requisicao.objects.filter(
        utilizador=request.user,
        estado__in=['pendente', 'aprovada', 'em_curso']
    ).count()

    return JsonResponse(contadores)


@user_passes_test(lambda u: u.is_staff)
@require_http_methods(["POST"])
def api_processar_devolucao(request, pk):
    """API endpoint to process equipment return"""
    try:
        # Parse request body if present
        observacao = None
        estado_item = None
        
        if request.body:
            try:
                data = json.loads(request.body)
                observacao = data.get('observacao')
                estado_item = data.get('estado_item')
            except json.JSONDecodeError:
                pass
        
        # Process return
        resultado = processar_devolucao(
            emprestimo_id=pk,
            observacao=observacao,
            estado_item=estado_item,
            operador=request.user
        )
        
        # Prepare response
        response_data = {
            'success': resultado['devolucao_efetivada'],
            'message': resultado['mensagem'],
        }
        
        if resultado['emprestimo']:
            response_data['emprestimo'] = {
                'id': resultado['emprestimo'].id,
                'estado': resultado['emprestimo'].estado,
                'data_devolucao_real': resultado['emprestimo'].data_devolucao_real.isoformat() if resultado['emprestimo'].data_devolucao_real else None,
            }
        
        status_code = 200 if resultado['devolucao_efetivada'] else 400
        return JsonResponse(response_data, status=status_code)
        
    except Exception:
        # Log the exception for debugging but don't expose details to users
        logger.exception('Error processing return for loan %s', pk)
        
        return JsonResponse({
            'success': False,
            'message': 'Erro ao processar devolução. Por favor, tente novamente ou contacte o suporte.'
        }, status=500)



"""
# Resumo das Views em equipamentos/views.py

Este ficheiro contém ** 12 views ** que controlam toda a lógica da aplicação:

** Views Públicas(login required): **

1. ** dashboard ** - Página
inicial
- Estatísticas gerais
- Últimas requisições do utilizador
- Alertas de requisições atrasadas(staff)

2. ** listar_equipamentos ** 
- Catálogo com filtros
- Filtros: categoria, estado, busca
- Pesquisa por nome, marca, modelo, código

3. ** detalhe_equipamento ** 
- Ficha completa
- Informações detalhadas
- Histórico de manutenção
- Requisições recentes

4. ** criar_requisicao ** 
- Nova requisição
- Formulário com validação
- Salva utilizador atual
- Notificação de sucesso

5. ** minhas_requisicoes ** 
- Histórico pessoal
- Todas as requisições doutilizador
- Ordenadas por data

6. ** detalhe_requisicao ** 
- Detalhes da requisição
- Controle de permissões(staff ou dono)
- Histórico completo
- Timeline de eventos

** Views
Staff(apenas
administradores): **

7. ** listar_requisicoes_pendentes ** 
- Fila de aprovação
- Requisições aguardando decisão
- Ordenadas por data de requisição

8. ** aprovar_requisicao ** 
- Aprovar / rejeitar
- Formulário de decisão
- Atualiza estado dos equipamentos
- Registra quem aprovou e quando

9. ** registar_entrega ** 
- Entrega ao utilizador
- Muda estado para "em_curso"
- Registra data / hora real

10. ** registar_devolucao ** 
- Receber devolução
- Formulário com observações
- Marca equipamentos como disponíveis
- Finaliza requisição

11. ** relatorio_equipamentos ** 
- Estatísticas
- Equipamentos mais / menos requisitados
- Análise de utilização

** API(AJAX): **

12. ** api_contadores ** 
- EndpointJSON
- Retorna contadores em tempo real
- Usado pelo WebSocket client
- Dados diferentes para staff / utilizador

** Características: **

- ✅ ** Decorators ** para autenticação e permissões
- ✅ ** Validação ** de permissões(staff vs utilizador)
- ✅ ** Messages ** para feedback ao utilizador
- ✅ ** Query optimization ** (select_related, prefetch_related implícito)
- ✅ ** Filtros ** dinâmicos via GET parameters
- ✅ ** Segurança ** - HttpResponseForbidden para acesso não autorizado
- ✅ ** API REST ** para JavaScript assíncrono

** Fluxo completo de uma requisição: **
```
1. Utilizador: criar_requisicao(POST)
2. Signal dispara → notifica staff via WebSocket
3. Staff: listar_requisicoes_pendentes
4. Staff: aprovar_requisicao(aprovar / rejeitar)
5. Signal dispara → notifica utilizador
6. Staff: registar_entrega(quando utilizadorlevanta)
7. Staff: registar_devolucao(quando utilizador devolve)
8. Equipamentos ficam disponíveis novamente
"""