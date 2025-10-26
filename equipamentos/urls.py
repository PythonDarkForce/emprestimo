from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Equipamentos
    path('equipamentos/', views.listar_equipamentos, name='listar_equipamentos'),
    path('equipamentos/<int:pk>/', views.detalhe_equipamento, name='detalhe_equipamento'),

    # Requisições
    path('requisicoes/nova/', views.criar_requisicao, name='criar_requisicao'),
    path('requisicoes/minhas/', views.minhas_requisicoes, name='minhas_requisicoes'),
    path('requisicoes/<int:pk>/', views.detalhe_requisicao, name='detalhe_requisicao'),

    # Gestão de requisições (staff)
    path('requisicoes/pendentes/', views.listar_requisicoes_pendentes, name='listar_requisicoes_pendentes'),
    path('requisicoes/<int:pk>/aprovar/', views.aprovar_requisicao, name='aprovar_requisicao'),
    path('requisicoes/<int:pk>/entrega/', views.registar_entrega, name='registar_entrega'),
    path('requisicoes/<int:pk>/devolucao/', views.registar_devolucao, name='registar_devolucao'),

    # Relatórios
    path('relatorios/equipamentos/', views.relatorio_equipamentos, name='relatorio_equipamentos'),
    
    # API
    path('api/contadores/', views.api_contadores, name='api_contadores'),
    path('api/equipamentos/<int:pk>/cronograma/', views.api_cronograma_equipamento, name='api_cronograma_equipamento'),
]