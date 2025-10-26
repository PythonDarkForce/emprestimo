"""
Domain service for processing equipment returns
"""
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import Requisicao


def processar_devolucao(
    emprestimo_id,
    *,
    data_devolucao=None,
    observacao=None,
    estado_item=None,
    operador=None
):
    """
    Process equipment return in an idempotent and transactional way.
    
    Args:
        emprestimo_id: ID of the loan/requisition to process
        data_devolucao: Optional return date (defaults to now)
        observacao: Optional observation/notes about the return
        estado_item: Optional equipment condition
        operador: Optional operator user who processed the return
        
    Returns:
        dict with:
            - devolucao_efetivada: bool indicating if return was processed
            - emprestimo: the Requisicao instance
            - mensagem: status message
    """
    with transaction.atomic():
        # Lock the requisition to prevent race conditions
        try:
            emprestimo = Requisicao.objects.select_for_update().get(pk=emprestimo_id)
        except Requisicao.DoesNotExist:
            return {
                'devolucao_efetivada': False,
                'emprestimo': None,
                'mensagem': f'Empréstimo #{emprestimo_id} não encontrado.'
            }
        
        # Check if already returned (idempotency)
        if emprestimo.estado == 'concluida' and emprestimo.data_devolucao_real:
            return {
                'devolucao_efetivada': False,
                'emprestimo': emprestimo,
                'mensagem': f'Empréstimo #{emprestimo_id} já foi devolvido.'
            }
        
        # Set return date
        if data_devolucao is None:
            data_devolucao = timezone.now()
        
        # Update requisition
        emprestimo.estado = 'concluida'
        emprestimo.data_devolucao_real = data_devolucao
        
        # Update observations if provided
        if observacao:
            emprestimo.observacoes_devolucao = observacao
        
        # Save the requisition
        # Note: We set _skip_signal to prevent recursive signal firing
        # This is checked in signals.py to avoid infinite loops
        emprestimo._skip_signal = True
        emprestimo.save()
        
        # Update equipment availability
        emprestimo.equipamentos.all().update(estado='disponivel')
        
        # Get equipment IDs for the event
        item_ids = list(emprestimo.equipamentos.values_list('id', flat=True))
        
        # Emit WebSocket event
        _emitir_evento_devolucao(
            emprestimo_id=emprestimo.id,
            status='concluida',
            data_devolucao=data_devolucao.isoformat() if isinstance(data_devolucao, datetime) else str(data_devolucao),
            item_ids=item_ids
        )
        
        return {
            'devolucao_efetivada': True,
            'emprestimo': emprestimo,
            'mensagem': f'Devolução do empréstimo #{emprestimo_id} processada com sucesso.'
        }


def _emitir_evento_devolucao(emprestimo_id, status, data_devolucao, item_ids):
    """
    Emit WebSocket event for return processing.
    
    Args:
        emprestimo_id: ID of the loan
        status: Current status
        data_devolucao: Return date
        item_ids: List of equipment IDs
    """
    channel_layer = get_channel_layer()
    
    # Prepare event payload
    event_payload = {
        'type': 'emprestimo.updated',
        'id': emprestimo_id,
        'status': status,
        'data_devolucao': data_devolucao,
        'item_ids': item_ids
    }
    
    # Send to emprestimos group
    async_to_sync(channel_layer.group_send)(
        'emprestimos',
        {
            'type': 'emprestimo_update',
            **event_payload
        }
    )
