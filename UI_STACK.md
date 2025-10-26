# UI Stack Documentation

## Framework de Interface

Este projeto utiliza **Tabler** como framework principal de UI.

### Tabler

- **Versão**: 1.4.0
- **CDN CSS**: https://cdn.jsdelivr.net/npm/@tabler/core@1.4.0/dist/css/tabler.min.css
- **CDN JS**: https://cdn.jsdelivr.net/npm/@tabler/core@1.4.0/dist/js/tabler.min.js
- **Documentação**: https://tabler.io/docs

### Ícones

O projeto utiliza **Tabler Icons** para ícones:

- **Versão**: Latest
- **CDN**: https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css
- **Documentação**: https://tabler-icons.io/
- **Uso**: Adicione classes como `ti ti-camera`, `ti ti-user`, etc.

## Componentes Principais

### Cards
```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Título</h3>
    </div>
    <div class="card-body">
        Conteúdo
    </div>
    <div class="card-footer">
        Rodapé
    </div>
</div>
```

### Buttons
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-danger">Danger</button>
<button class="btn btn-warning">Warning</button>
```

### Tables
```html
<table class="table table-vcenter card-table">
    <thead>
        <tr>
            <th>Coluna 1</th>
            <th>Coluna 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Dado 1</td>
            <td>Dado 2</td>
        </tr>
    </tbody>
</table>
```

### Forms
```html
<div class="mb-3">
    <label class="form-label">Label</label>
    <input type="text" class="form-control" placeholder="Placeholder">
    <small class="form-hint">Texto de ajuda</small>
</div>
```

### Badges
```html
<span class="badge bg-success">Success</span>
<span class="badge bg-danger">Danger</span>
<span class="badge bg-warning">Warning</span>
<span class="badge bg-azure">Info</span>
```

### Alerts
```html
<div class="alert alert-success" role="alert">
    <div class="d-flex">
        <div>
            <i class="ti ti-check"></i>
        </div>
        <div>
            <h4 class="alert-title">Título</h4>
            <div class="text-muted">Mensagem</div>
        </div>
    </div>
</div>
```

### Empty States
```html
<div class="empty">
    <div class="empty-icon">
        <i class="ti ti-search"></i>
    </div>
    <p class="empty-title">Título</p>
    <p class="empty-subtitle text-muted">Descrição</p>
    <div class="empty-action">
        <button class="btn btn-primary">Ação</button>
    </div>
</div>
```

## Layout

### Estrutura de Página
```html
<div class="page-wrapper">
    <div class="page-body">
        <div class="container-xl">
            <!-- Conteúdo -->
        </div>
    </div>
</div>
```

### Page Header
```html
<div class="page-header d-print-none">
    <div class="container-xl">
        <div class="row g-2 align-items-center">
            <div class="col">
                <h2 class="page-title">Título da Página</h2>
            </div>
            <div class="col-auto ms-auto">
                <!-- Ações -->
            </div>
        </div>
    </div>
</div>
```

## Grid System

Tabler utiliza o sistema de grid do Bootstrap 5:
- Containers: `.container-xl`, `.container-fluid`
- Rows: `.row`, `.row-cards`
- Columns: `.col`, `.col-md-6`, `.col-lg-4`, etc.

## Utilitários

### Spacing
- Margin: `m-0` a `m-5`, `mt-3`, `mb-4`, etc.
- Padding: `p-0` a `p-5`, `pt-3`, `pb-4`, etc.

### Display
- `d-none`, `d-block`, `d-flex`, `d-inline-block`
- `d-md-none`, `d-lg-block` (responsive)

### Flexbox
- `d-flex`, `justify-content-between`, `align-items-center`
- `flex-row`, `flex-column`

### Text
- `text-muted`, `text-primary`, `text-success`
- `text-center`, `text-start`, `text-end`

## Cores Disponíveis

- **Primary**: Azul principal
- **Success**: Verde (sucesso, disponível)
- **Danger**: Vermelho (erro, manutenção)
- **Warning**: Amarelo (aviso, emprestado)
- **Azure**: Azul claro (informação)
- **Secondary**: Cinza (concluído)

## Migração do Bootstrap

Este projeto foi migrado do Bootstrap 5.3.0 para o Tabler. As principais mudanças incluem:

1. **CDN**: Substituído Bootstrap por Tabler
2. **Ícones**: `bi bi-*` → `ti ti-*`
3. **Navegação**: Estrutura do navbar adaptada para Tabler
4. **Layout**: Adicionado `.page-wrapper` e `.page-body`
5. **Componentes**: Ajustados para usar variantes do Tabler

### Compatibilidade

A maioria das classes do Bootstrap 5 são compatíveis com Tabler, incluindo:
- Sistema de grid (`.row`, `.col-*`)
- Utilitários de espaçamento (`.m-*`, `.p-*`)
- Classes de formulário (`.form-control`, `.form-label`)
- Flexbox (`.d-flex`, `.justify-content-*`)

## Desenvolvimento

Ao criar novos componentes:

1. Consulte a documentação do Tabler: https://tabler.io/docs
2. Use ícones do Tabler Icons: https://tabler-icons.io/
3. Mantenha consistência com os templates existentes
4. Teste a responsividade em diferentes tamanhos de tela
5. Use as variáveis CSS do Tabler quando possível

## Temas e Customização

Para customizar o tema, você pode:

1. Sobrescrever variáveis CSS do Tabler no arquivo `base.html`
2. Adicionar estilos personalizados em arquivos CSS na pasta `static/css/`
3. Usar as classes utilitárias do Tabler para ajustes rápidos

## Recursos

- **Tabler**: https://tabler.io/
- **Tabler GitHub**: https://github.com/tabler/tabler
- **Tabler Icons**: https://tabler-icons.io/
- **Exemplos**: https://preview.tabler.io/
