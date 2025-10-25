#!/bin/bash
# ============================================
# Script de Instalação Rápida
# Sistema de Gestão de Equipamentos com WebSocket
# ============================================

echo "🚀 Iniciando instalação..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${YELLOW}Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 não encontrado. Instale Python 3.8+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python encontrado${NC}"

# Verificar Redis
echo -e "${YELLOW}Verificando Redis...${NC}"
if ! command -v redis-cli &> /dev/null; then
    echo -e "${RED}Redis não encontrado.${NC}"
    echo "Instale Redis:"
    echo "  Ubuntu/Debian: sudo apt install redis-server"
    echo "  macOS: brew install redis"
    echo "  Windows: docker run -d -p 6379:6379 redis"
    exit 1
fi

# Testar Redis
if ! redis-cli ping &> /dev/null; then
    echo -e "${RED}Redis não está rodando. Inicie o Redis:${NC}"
    echo "  Linux: sudo systemctl start redis"
    echo "  macOS: brew services start redis"
    exit 1
fi
echo -e "${GREEN}✓ Redis rodando${NC}"

# Criar ambiente virtual
echo -e "${YELLOW}Criando ambiente virtual...${NC}"
python3 -m venv venv
echo -e "${GREEN}✓ Ambiente virtual criado${NC}"

# Ativar ambiente virtual
echo -e "${YELLOW}Ativando ambiente virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"

# Instalar dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
pip install --upgrade pip
pip install Django>=4.2,<5.0
pip install Pillow>=10.0.0
pip install channels>=4.0.0
pip install channels-redis>=4.1.0
pip install daphne>=4.0.0
pip install redis>=5.0.0
echo -e "${GREEN}✓ Dependências instaladas${NC}"

# Criar estrutura de diretórios
echo -e "${YELLOW}Criando estrutura de diretórios...${NC}"
mkdir -p static/js
mkdir -p media/equipamentos
mkdir -p templates/equipamentos
mkdir -p templates/registration
mkdir -p equipamentos/management/commands
echo -e "${GREEN}✓ Diretórios criados${NC}"

# Executar migrações
echo -e "${YELLOW}Executando migrações...${NC}"
python manage.py makemigrations
python manage.py migrate
echo -e "${GREEN}✓ Migrações executadas${NC}"

# Criar superusuário
echo -e "${YELLOW}Criar superusuário (admin)...${NC}"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
echo -e "${GREEN}✓ Superusuário criado: admin/admin123${NC}"

# Criar dados de exemplo
if [ -f "equipamentos/management/commands/criar_dados_exemplo.py" ]; then
    echo -e "${YELLOW}Criando dados de exemplo...${NC}"
    python manage.py criar_dados_exemplo
    echo -e "${GREEN}✓ Dados de exemplo criados${NC}"
fi

# Mensagem final
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Instalação concluída com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Para iniciar o sistema:${NC}"
echo "  1. Certifique-se que Redis está rodando:"
echo "     redis-cli ping"
echo ""
echo "  2. Inicie o servidor Django:"
echo "     python manage.py runserver"
echo "     ou"
echo "     daphne -b 0.0.0.0 -p 8000 projeto.asgi:application"
echo ""
echo "  3. Acesse: http://localhost:8000"
echo ""
echo -e "${YELLOW}Credenciais:${NC}"
echo "  Admin: admin / admin123"
if [ -f "equipamentos/management/commands/criar_dados_exemplo.py" ]; then
    echo "  Utilizador: joao / senha123"
fi
echo ""
echo -e "${GREEN}Bom trabalho! 🚀${NC}"
