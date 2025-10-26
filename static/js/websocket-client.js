// ============================================
// WebSocket Manager para Sistema em Tempo Real
// ============================================
//
// Gerencia 3 conexões WebSocket (notificações, requisições, equipamentos)
// Reconexão automática (até 5 tentativas)
// Heartbeat (ping/pong a cada 30s para manter conexão viva)
// Notificações visuais (toasts no canto superior direito)
// Sons de alerta (diferentes para cada tipo)
// Atualização de interface (badges, contadores, estados)
// Indicador de conexão (verde/vermelho)
// Animações CSS (slide-in, flash, pulse)
//
// ws://localhost:8000/ws/notificacoes/
// ws://localhost:8000/ws/requisicoes/
// ws://localhost:8000/ws/equipamentos/




class WebSocketManager {
    constructor() {
        this.notificacoesSocket = null;
        this.requisicoesSocket = null;
        this.equipamentosSocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.heartbeatInterval = null;
        this.notificationQueue = [];
    }

    // Conectar ao WebSocket de notificações
    conectarNotificacoes() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notificacoes/`;

        this.notificacoesSocket = new WebSocket(wsUrl);

        this.notificacoesSocket.onopen = (e) => {
            console.log('✓ Conectado ao sistema de notificações');
            this.reconnectAttempts = 0;
            this.atualizarIndicadorConexao(true);
            this.mostrarNotificacaoSistema('Conectado ao sistema de notificações em tempo real', 'success');
            this.startHeartbeat();
        };

        this.notificacoesSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.processarNotificacao(data);
        };

        this.notificacoesSocket.onclose = (e) => {
            console.log('✗ Desconectado do sistema de notificações');
            this.atualizarIndicadorConexao(false);
            this.stopHeartbeat();
            this.tentarReconectar('notificacoes');
        };

        this.notificacoesSocket.onerror = (e) => {
            console.error('Erro no WebSocket de notificações:', e);
        };
    }

    // Conectar ao WebSocket de requisições
    conectarRequisicoes() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/requisicoes/`;

        this.requisicoesSocket = new WebSocket(wsUrl);

        this.requisicoesSocket.onopen = (e) => {
            console.log('✓ Conectado às atualizações de requisições');
        };

        this.requisicoesSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.atualizarRequisicao(data);
        };

        this.requisicoesSocket.onclose = (e) => {
            console.log('✗ Desconectado das atualizações de requisições');
            this.tentarReconectar('requisicoes');
        };
    }

    // Conectar ao WebSocket de equipamentos
    conectarEquipamentos() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/equipamentos/`;

        this.equipamentosSocket = new WebSocket(wsUrl);

        this.equipamentosSocket.onopen = (e) => {
            console.log('✓ Conectado às atualizações de equipamentos');
        };

        this.equipamentosSocket.onmessage = (e) => {
            const data = JSON.parse(e.data);
            this.atualizarEquipamento(data);
        };

        this.equipamentosSocket.onclose = (e) => {
            console.log('✗ Desconectado das atualizações de equipamentos');
            this.tentarReconectar('equipamentos');
        };
    }

    // Processar notificações recebidas
    processarNotificacao(data) {
        console.log('Notificação recebida:', data);

        switch(data.type) {
            case 'connection_established':
                // Conexão estabelecida
                break;

            case 'nova_requisicao':
                this.mostrarNotificacao(
                    'Nova Requisição',
                    data.message,
                    'info',
                    `/requisicoes/${data.requisicao_id}/`
                );
                this.tocarSom('notification');
                this.atualizarContadores();
                break;

            case 'requisicao_aprovada':
                this.mostrarNotificacao(
                    'Requisição Aprovada! 🎉',
                    data.message,
                    'success',
                    `/requisicoes/${data.requisicao_id}/`
                );
                this.tocarSom('success');
                break;

            case 'requisicao_rejeitada':
                this.mostrarNotificacao(
                    'Requisição Rejeitada',
                    `${data.message}${data.motivo ? '<br><small>' + data.motivo + '</small>' : ''}`,
                    'danger',
                    `/requisicoes/${data.requisicao_id}/`
                );
                this.tocarSom('error');
                break;

            case 'equipamento_entregue':
                this.mostrarNotificacao(
                    'Equipamento Entregue',
                    data.message,
                    'info',
                    `/requisicoes/${data.requisicao_id}/`
                );
                break;

            case 'lembrete_devolucao':
                this.mostrarNotificacao(
                    'Lembrete de Devolução ⏰',
                    data.message,
                    'warning',
                    `/requisicoes/${data.requisicao_id}/`
                );
                this.tocarSom('alert');
                break;

            case 'requisicao_atrasada':
                this.mostrarNotificacao(
                    'Requisição Atrasada! ⚠️',
                    data.message,
                    'danger',
                    `/requisicoes/${data.requisicao_id}/`
                );
                this.tocarSom('urgent');
                break;

            case 'pong':
                // Resposta ao ping
                break;
        }
    }

    // Atualizar requisição na interface
    atualizarRequisicao(data) {
        if (data.type !== 'requisicao_update') return;

        console.log('Atualizar requisição:', data);



        // Atualizar badge de estado se elemento existir
        const badge = document.querySelector(`[data-requisicao-id="${data.requisicao_id}"] .estado-badge`);
        if (badge) {
            badge.textContent = this.traduzirEstado(data.estado);
            badge.className = `badge estado-badge ${this.getEstadoClass(data.estado)}`;
        }

        // Se estiver na página de requisições pendentes, remover item se não estiver mais pendente
        if (window.location.pathname.includes('/requisicoes/pendentes/')) {
            if (data.estado !== 'pendente') {
                const row = document.querySelector(`[data-requisicao-id="${data.requisicao_id}"]`);
                if (row) {
                    row.style.transition = 'opacity 0.3s';
                    row.style.opacity = '0';
                    setTimeout(() => row.remove(), 300);
                }
            }
        }

        // Atualizar contadores
        this.atualizarContadores();
    }

    // Atualizar equipamento na interface
    atualizarEquipamento(data) {
        if (data.type !== 'equipamento_update') return;

        console.log('Atualizar equipamento:', data);

        // Atualizar badge de estado
        const badge = document.querySelector(`[data-equipamento-id="${data.equipamento_id}"] .estado-badge`);
        if (badge) {
            badge.textContent = this.traduzirEstado(data.estado);
            badge.className = `badge estado-badge ${this.getEstadoClass(data.estado)}`;
        }

        // Atualizar card de equipamento se existir
        const card = document.querySelector(`[data-equipamento-id="${data.equipamento_id}"]`);
        if (card) {
            card.classList.add('updated-flash');
            setTimeout(() => card.classList.remove('updated-flash'), 1000);
        }
    }

    // Mostrar notificação na interface
    mostrarNotificacao(titulo, mensagem, tipo = 'info', link = null) {
        const notificacao = document.createElement('div');
        // Map Bootstrap alert types to Tabler types
        const tipoMap = {
            'success': 'success',
            'danger': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        const tipoTabler = tipoMap[tipo] || 'info';
        notificacao.className = `alert alert-${tipoTabler} alert-dismissible notification-toast`;
        notificacao.setAttribute('role', 'alert');

        let conteudo = `
            <div class="d-flex">
                <div>
                    <h4 class="alert-title">${titulo}</h4>
                    <div class="text-muted">${mensagem}</div>
                </div>
            </div>
        `;

        if (link) {
            conteudo += `<div class="mt-2"><a href="${link}" class="btn btn-sm btn-${tipoTabler}">Ver detalhes</a></div>`;
        }

        conteudo += `
            <a class="btn-close" data-bs-dismiss="alert" aria-label="close"></a>
        `;

        notificacao.innerHTML = conteudo;

        let container = document.getElementById('notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notifications-container';
            container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; max-width: 400px;';
            document.body.appendChild(container);
        }

        container.appendChild(notificacao);

        setTimeout(() => {
            notificacao.style.opacity = '0';
            setTimeout(() => notificacao.remove(), 300);
        }, 10000);
    }

    // Adicionar ao websocket-client.js
    solicitarPermissaoNotificacoes() {
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }
    }

    mostrarNotificacaoNavegador(titulo, mensagem) {
        if ("Notification" in window && Notification.permission === "granted") {
            new Notification(titulo, {
                body: mensagem,
                icon: '/static/images/logo.png',
                badge: '/static/images/badge.png',
                tag: 'equipamentos-notification',
                requireInteraction: false
            });
        }
    }

    // // Usar nas notificações importantes
    // case 'requisicao_aprovada':
    //     this.mostrarNotificacaoNavegador('Requisição Aprovada', data.message);
    //     break;

    // Mostrar notificação do sistema (menos intrusiva)
    mostrarNotificacaoSistema(mensagem, tipo = 'info') {
        const toast = document.createElement('div');
        // Map to Tabler color classes
        const tipoMap = {
            'success': 'green',
            'danger': 'red',
            'warning': 'yellow',
            'info': 'blue'
        };
        const bgColor = tipoMap[tipo] || 'blue';
        toast.className = `toast align-items-center text-bg-${bgColor} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${mensagem}</div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }

        container.appendChild(toast);
        // Bootstrap Toast API is compatible with Tabler
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }

    // Tocar som de notificação
    tocarSom(tipo = 'notification') {
        const audio = new Audio();
        audio.volume = 0.3;


        // switch(tipo) {
        //     case 'success':
        //         // Som de sucesso
        //         audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZRA==';
        //         break;
        //     case 'error':
        //         // Som de erro
        //         audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAA

        // Usar data URI simples para compatibilidade
        const beep = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF==';
        audio.src = beep;
        audio.play().catch(e => console.log('Não foi possível tocar som:', e));
    }

    // Heartbeat (ping/pong)
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.notificacoesSocket && this.notificacoesSocket.readyState === WebSocket.OPEN) {
                this.notificacoesSocket.send(JSON.stringify({
                    type: 'ping',
                    timestamp: new Date().getTime()
                }));
            }
        }, 30000);
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
    }

    // Tentar reconectar
    tentarReconectar(tipo) {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Número máximo de tentativas de reconexão atingido');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * this.reconnectAttempts;

        console.log(`Tentando reconectar (${this.reconnectAttempts}/${this.maxReconnectAttempts}) em ${delay/1000}s...`);

        setTimeout(() => {
            switch(tipo) {
                case 'notificacoes':
                    this.conectarNotificacoes();
                    break;
                case 'requisicoes':
                    this.conectarRequisicoes();
                    break;
                case 'equipamentos':
                    this.conectarEquipamentos();
                    break;
            }
        }, delay);
    }

    // Atualizar contadores na interface
    atualizarContadores() {
        fetch('/api/contadores/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            const badgePendentes = document.getElementById('badge-pendentes');
            if (badgePendentes && data.requisicoes_pendentes !== undefined) {
                badgePendentes.textContent = data.requisicoes_pendentes;
                if (data.requisicoes_pendentes > 0) {
                    badgePendentes.classList.remove('d-none');
                } else {
                    badgePendentes.classList.add('d-none');
                }
            }

            const badgeAtrasadas = document.getElementById('badge-atrasadas');
            if (badgeAtrasadas && data.requisicoes_atrasadas !== undefined) {
                badgeAtrasadas.textContent = data.requisicoes_atrasadas;
                if (data.requisicoes_atrasadas > 0) {
                    badgeAtrasadas.classList.remove('d-none');
                } else {
                    badgeAtrasadas.classList.add('d-none');
                }
            }
        })
        .catch(error => console.error('Erro ao atualizar contadores:', error));
    }

    // Atualizar indicador de conexão
    atualizarIndicadorConexao(conectado) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.querySelector('#connection-status .d-none.d-lg-inline');

        if (statusDot) {
            if (conectado) {
                statusDot.classList.remove('status-offline');
                statusDot.classList.add('status-online');
                if (statusText) statusText.textContent = 'Online';
            } else {
                statusDot.classList.remove('status-online');
                statusDot.classList.add('status-offline');
                if (statusText) statusText.textContent = 'Desconectado';
            }
        }
    }

    // Traduzir estados
    traduzirEstado(estado) {
        const traducoes = {
            'pendente': 'Pendente',
            'aprovada': 'Aprovada',
            'rejeitada': 'Rejeitada',
            'em_curso': 'Em Curso',
            'concluida': 'Concluída',
            'atrasada': 'Atrasada',
            'disponivel': 'Disponível',
            'emprestado': 'Emprestado',
            'manutencao': 'Em Manutenção',
            'inativo': 'Inativo'
        };
        return traducoes[estado] || estado;
    }

    // Obter classe CSS para estado
    getEstadoClass(estado) {
        // Using Tabler's color classes
        const classes = {
            'pendente': 'bg-warning',
            'aprovada': 'bg-green',
            'rejeitada': 'bg-danger',
            'em_curso': 'bg-blue',
            'concluida': 'bg-secondary',
            'atrasada': 'bg-danger',
            'disponivel': 'bg-green',
            'emprestado': 'bg-yellow',
            'manutencao': 'bg-red',
            'inativo': 'bg-secondary'
        };
        return classes[estado] || 'bg-secondary';
    }

    // Desconectar todos os sockets
    desconectarTodos() {
        if (this.notificacoesSocket) {
            this.notificacoesSocket.close();
        }
        if (this.requisicoesSocket) {
            this.requisicoesSocket.close();
        }
        if (this.equipamentosSocket) {
            this.equipamentosSocket.close();
        }
        this.stopHeartbeat();
    }

    // Inicializar todas as conexões
    inicializar() {
        this.conectarNotificacoes();
        this.conectarRequisicoes();
        this.conectarEquipamentos();

        this.atualizarContadores();

        window.addEventListener('beforeunload', () => {
            this.desconectarTodos();
        });
    }
}

// Instância global
let wsManager;

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    wsManager = new WebSocketManager();
    wsManager.inicializar();

    console.log('WebSocket Manager inicializado');
});


// Adicionar estilos CSS para animações
const style = document.createElement('style');
style.textContent = `
    .notification-toast {
        animation: slideInRight 0.3s ease-out;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .updated-flash {
        animation: flashUpdate 1s ease;
    }
    
    @keyframes flashUpdate {
        0%, 100% { background-color: transparent; }
        50% { background-color: rgba(255, 193, 7, 0.3); }
    }
    
    .notification-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        padding: 2px 6px;
        border-radius: 10px;
        font-size: 0.7rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
`;
document.head.appendChild(style);