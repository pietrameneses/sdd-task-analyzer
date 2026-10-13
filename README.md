# sdd-task-analyzer

Implementação do **TaskAnalyzer** em Spec-Driven Development (SDD), com código gerado por assistente de IA sob contrato técnico e homologado por revisão humana.

- **Autora:** Pietra Meneses — Ciência da Computação, UniCEUB (Asa Norte)
- **Disciplina:** Bootcamp III — Fase 2 (Entrega Intermediária)
- **Status dos testes:** 15 testes, 100% aprovados com `pytest`

---

## O que é

O TaskAnalyzer é um módulo Python que recebe uma lista de tarefas e devolve métricas de produtividade: total de tarefas, concluídas e pendentes, tempo médio de conclusão em horas, taxa de atraso percentual e os mesmos indicadores agrupados por prioridade.

O diferencial não está no algoritmo, e sim no método: a especificação foi escrita **antes** do código e funciona como contrato. A IA gerou a implementação a partir dela, e os testes automatizados são a prova de que o resultado cumpre o contrato.

## Estrutura

```
sdd-task-analyzer/
├── README.md                     # Este arquivo
├── CONTEXT_RULES.md              # Regras de governança fornecidas à IA
├── requirements.txt              # Dependências autorizadas
├── .gitignore
├── specs/
│   └── task_analyzer_spec.md     # Contrato SDD (fonte da verdade)
├── src/
│   └── task_analyzer.py          # Código gerado via IA e homologado
└── tests/
    └── test_harness.py           # Suíte de testes (pytest)
```

## Como executar

Requisitos: Python 3.11 ou superior.

```bash
git clone https://github.com/SEU-USUARIO/sdd-task-analyzer.git
cd sdd-task-analyzer
pip install -r requirements.txt
python -m pytest tests/ -v
```

Saída esperada: `15 passed`.

## Exemplo de uso

```python
from datetime import datetime
from src.task_analyzer import analyze_tasks

tarefas = [
    {
        "id_tarefa": 1,
        "titulo": "Revisar documentacao",
        "prioridade": "alta",
        "status": "concluida",
        "data_criacao": datetime(2026, 10, 1, 8, 0),
        "data_inicio": datetime(2026, 10, 1, 8, 0),
        "data_conclusao": datetime(2026, 10, 1, 12, 0),
        "prazo": datetime(2026, 10, 1, 16, 0),
    }
]

print(analyze_tasks(tarefas))
```

## Fluxo de trabalho SDD

1. **Especificar** — contrato, regras de negócio e cenários de aceite em `specs/`
2. **Contextualizar** — regras rígidas para a IA em `CONTEXT_RULES.md`
3. **Gerar** — código produzido pelo assistente a partir dos dois arquivos acima
4. **Validar** — execução do Test Harness com `pytest`
5. **Homologar** — revisão crítica humana antes do merge via Pull Request

A IA é a executora; a decisão final e a responsabilidade técnica permanecem humanas.

## Fases do projeto

| Fase | Entrega | Status |
|---|---|---|
| 1 | Especificação SDD, cenários de aceite e governança de contexto | Concluída |
| 2 | Repositório, geração de código via IA, Test Harness e versionamento | Esta entrega |
| 3 | CI/CD com GitHub Actions, containerização e revisão ética | Próxima |
