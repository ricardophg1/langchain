# src/sample_data.py

SAMPLE_DATA = {
    'ACME Corp': {
        'setor': 'Tecnologia',
        'fundacao': 1990,
        'produtos': ['Software', 'Hardware', 'Cloud Services'],
        'indicadores_base': {
            'funcionarios': 5000,
            'mercados': ['América', 'Europa', 'Ásia'],
            'receita_base': 1000000000
        }
    },
    'Globex Corporation': {
        'setor': 'Manufatura',
        'fundacao': 1985,
        'produtos': ['Eletrônicos', 'Automação', 'IoT'],
        'indicadores_base': {
            'funcionarios': 8000,
            'mercados': ['América do Norte', 'América do Sul', 'Europa'],
            'receita_base': 1500000000
        }
    }
    # Adicione mais empresas conforme necessário
}

# Dados de exemplo para relatórios comerciais
COMMERCIAL_METRICS = {
    'metricas_vendas': [
        'Volume de Vendas',
        'Ticket Médio',
        'Taxa de Conversão',
        'Custo de Aquisição de Cliente'
    ],
    'canais_vendas': [
        'Vendas Diretas',
        'E-commerce',
        'Distribuidores',
        'Parcerias'
    ]
}

# Dados de exemplo para relatórios operacionais
OPERATIONAL_METRICS = {
    'metricas_producao': [
        'Eficiência Operacional',
        'Tempo de Ciclo',
        'Taxa de Defeitos',
        'Utilização de Capacidade'
    ],
    'indicadores_qualidade': [
        'Conformidade',
        'Satisfação do Cliente',
        'Tempo de Resposta',
        'Incidentes'
    ]
}