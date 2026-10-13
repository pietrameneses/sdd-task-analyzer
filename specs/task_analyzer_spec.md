# Especificação SDD — TaskAnalyzer

Contrato executável transposto da Fase 1. É a fonte da verdade para o código gerado por IA e para o Test Harness.

- **Autora:** Pietra Meneses — Ciência da Computação, UniCEUB (Asa Norte)
- **Disciplina:** Bootcamp III — Fase 2
- **Versão:** 1.1 (nomes de campos alinhados ao enunciado da Fase 2)

---

## 1. Propósito

O TaskAnalyzer é um módulo de análise de tarefas e produtividade escrito em Python. Ele recebe uma lista de tarefas já registradas por um sistema externo e devolve métricas consolidadas: quantidade de tarefas, tempo médio de conclusão, taxa de atraso e os mesmos indicadores agrupados por prioridade.

O módulo **não** cadastra tarefas, não persiste dados, não expõe interface e não se comunica com serviços externos. Ele é uma biblioteca de cálculo, e essa fronteira é intencional: um escopo pequeno é o que permite validar o comportamento por testes automatizados.

## 2. Contrato Executável de Interface

### 2.1 Função pública

```python
analyze_tasks(tarefas: list[dict[str, Any]]) -> dict[str, Any]
```

### 2.2 Entradas

| Campo | Tipo | Obrigatório | Restrições |
|---|---|---|---|
| `id_tarefa` | `int` | Sim | Maior que zero |
| `titulo` | `str` | Não | Texto livre, não participa de cálculo |
| `prioridade` | `str` | Sim | `baixa`, `media` ou `alta` |
| `status` | `str` | Sim | `concluida`, `pendente` ou `cancelada` |
| `data_criacao` | `datetime` | Sim | Em UTC |
| `data_inicio` | `datetime` | Não | Em UTC, não anterior a `data_criacao` |
| `data_conclusao` | `datetime` | Condicional | Obrigatória quando `status` é `concluida` |
| `prazo` | `datetime` | Sim | Em UTC |

### 2.3 Saídas

| Campo | Tipo | Descrição |
|---|---|---|
| `total_tarefas` | `int` | Total de tarefas recebidas |
| `total_concluidas` | `int` | Total com status `concluida` |
| `total_pendentes` | `int` | Total com status `pendente` |
| `tempo_medio_conclusao_horas` | `float` | Tempo médio de conclusão em horas |
| `taxa_atraso_percentual` | `float` | Percentual de concluídas após o prazo |
| `indicadores_por_prioridade` | `dict` | Mesmas métricas por `baixa`, `media` e `alta` |

Exemplo de retorno:

```python
{
  "total_tarefas": 4,
  "total_concluidas": 3,
  "total_pendentes": 1,
  "tempo_medio_conclusao_horas": 6.0,
  "taxa_atraso_percentual": 33.33,
  "indicadores_por_prioridade": {
    "alta":  {"total_concluidas": 2, "tempo_medio_conclusao_horas": 4.0,  "taxa_atraso_percentual": 0.0},
    "baixa": {"total_concluidas": 1, "tempo_medio_conclusao_horas": 10.0, "taxa_atraso_percentual": 100.0},
    "media": {"total_concluidas": 0, "tempo_medio_conclusao_horas": 0.0,  "taxa_atraso_percentual": 0.0}
  }
}
```

## 3. Regras de Negócio

- **RN01** — Somente tarefas com status `concluida` entram no cálculo de tempo médio e taxa de atraso.
- **RN02** — A duração é a diferença entre `data_conclusao` e `data_inicio`, em horas; sem `data_inicio`, usa-se `data_criacao`.
- **RN03** — Uma tarefa está atrasada quando `data_conclusao` é **posterior** ao `prazo`; conclusão exatamente no prazo não conta como atraso.
- **RN04** — As datas devem ser consistentes: `data_conclusao` nunca anterior a `data_inicio`, nem `data_inicio` anterior a `data_criacao`.
- **RN05** — Tarefas com status `cancelada` são ignoradas nos cálculos.
- **RN06** — Sem tarefas concluídas, as métricas retornam zeradas, sem exceção e sem divisão por zero.
- **RN07** — Valores de ponto flutuante são arredondados para duas casas decimais.
- **RN08** — Entradas inválidas disparam `TaskValidationError` com mensagem clara indicando a tarefa e o campo.

## 4. Cenários de Aceite

### Cenário 1 — Sucesso
- **Dado** um conjunto de tarefas válidas com prioridades e status diferentes,
- **Quando** `analyze_tasks` for executada,
- **Então** devolve os totais, o tempo médio de conclusão e a taxa de atraso corretos, geral e por prioridade.

### Cenário 2 — Exceção / Erro
- **Dado** uma entrada com datas inconsistentes (`data_conclusao` anterior a `data_criacao`) ou campo obrigatório ausente,
- **Quando** `analyze_tasks` for executada,
- **Então** dispara `TaskValidationError` com mensagem clara identificando a tarefa e o campo.

### Casos de Borda
- Lista vazia devolve a estrutura completa zerada.
- Lista só com pendentes e canceladas devolve médias `0.0`, sem exceção.
- Conclusão exatamente no prazo não conta como atraso.

## 5. Test Harness

Os cenários acima são verificados em `tests/test_harness.py` com `pytest`:

| Cenário | Teste |
|---|---|
| 1 | `test_metricas_com_tarefas_validas`, `test_indicadores_por_prioridade` |
| 2 | `test_excecao_para_datas_inconsistentes` e demais testes de exceção |
| Borda | `test_lista_vazia_retorna_metricas_zeradas`, `test_apenas_pendentes_retorna_metricas_zeradas`, `test_conclusao_no_prazo_nao_conta_como_atraso` |
