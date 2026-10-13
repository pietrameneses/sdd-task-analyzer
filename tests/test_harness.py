"""Test Harness do TaskAnalyzer.

Traduz os cenários de aceite da especificação SDD (Fase 1) em testes
automatizados executáveis com pytest.

Mapeamento cenário -> teste:
    Cenário 1 (sucesso)        -> test_metricas_com_tarefas_validas
    Cenário 2 (exceção/erro)   -> test_excecao_para_datas_inconsistentes
    Casos de borda             -> test_lista_vazia_retorna_metricas_zeradas
                                  test_apenas_pendentes_retorna_metricas_zeradas
                                  test_conclusao_no_prazo_nao_conta_como_atraso
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.task_analyzer import TaskValidationError, analyze_tasks

BASE: datetime = datetime(2026, 10, 1, 8, 0, 0)


def criar_tarefa(
    id_tarefa: int,
    prioridade: str = "media",
    status: str = "concluida",
    horas_ate_inicio: float = 0.0,
    horas_ate_conclusao: float | None = 4.0,
    horas_ate_prazo: float = 8.0,
) -> dict[str, Any]:
    """Cria uma tarefa válida para uso nos testes.

    Args:
        id_tarefa: Identificador único da tarefa.
        prioridade: Prioridade da tarefa (`baixa`, `media` ou `alta`).
        status: Status da tarefa (`concluida`, `pendente` ou `cancelada`).
        horas_ate_inicio: Horas entre a criação e o início da execução.
        horas_ate_conclusao: Horas entre a criação e a conclusão; `None` para
            tarefas sem data de conclusão.
        horas_ate_prazo: Horas entre a criação e o prazo acordado.

    Returns:
        Dicionário representando a tarefa.
    """
    tarefa: dict[str, Any] = {
        "id_tarefa": id_tarefa,
        "titulo": f"Tarefa {id_tarefa}",
        "prioridade": prioridade,
        "status": status,
        "data_criacao": BASE,
        "data_inicio": BASE + timedelta(hours=horas_ate_inicio),
        "prazo": BASE + timedelta(hours=horas_ate_prazo),
    }
    if horas_ate_conclusao is not None:
        tarefa["data_conclusao"] = BASE + timedelta(hours=horas_ate_conclusao)
    return tarefa


@pytest.fixture
def tarefas_validas() -> list[dict[str, Any]]:
    """Conjunto misto de tarefas válidas, com prioridades e status diferentes.

    Returns:
        Lista com quatro tarefas: duas concluídas no prazo, uma concluída com
        atraso e uma pendente.
    """
    return [
        criar_tarefa(1, prioridade="alta", horas_ate_conclusao=2.0, horas_ate_prazo=8.0),
        criar_tarefa(2, prioridade="alta", horas_ate_conclusao=6.0, horas_ate_prazo=8.0),
        criar_tarefa(3, prioridade="baixa", horas_ate_conclusao=10.0, horas_ate_prazo=8.0),
        criar_tarefa(4, prioridade="media", status="pendente", horas_ate_conclusao=None),
    ]


# --- Cenário 1: sucesso -------------------------------------------------------


def test_metricas_com_tarefas_validas(tarefas_validas: list[dict[str, Any]]) -> None:
    """Dado tarefas válidas, quando analisadas, então as métricas são corretas."""
    resultado = analyze_tasks(tarefas_validas)

    assert resultado["total_tarefas"] == 4
    assert resultado["total_concluidas"] == 3
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 6.0
    assert resultado["taxa_atraso_percentual"] == 33.33


def test_indicadores_por_prioridade(tarefas_validas: list[dict[str, Any]]) -> None:
    """As métricas são agrupadas corretamente por prioridade."""
    indicadores = analyze_tasks(tarefas_validas)["indicadores_por_prioridade"]

    assert set(indicadores) == {"alta", "baixa", "media"}
    assert indicadores["alta"]["total_concluidas"] == 2
    assert indicadores["alta"]["tempo_medio_conclusao_horas"] == 4.0
    assert indicadores["alta"]["taxa_atraso_percentual"] == 0.0
    assert indicadores["baixa"]["taxa_atraso_percentual"] == 100.0
    assert indicadores["media"]["total_concluidas"] == 0


def test_tarefas_canceladas_sao_ignoradas() -> None:
    """Tarefas canceladas não entram em nenhuma métrica de conclusão."""
    tarefas = [
        criar_tarefa(1, horas_ate_conclusao=4.0),
        criar_tarefa(2, status="cancelada", horas_ate_conclusao=None),
    ]

    resultado = analyze_tasks(tarefas)

    assert resultado["total_tarefas"] == 2
    assert resultado["total_concluidas"] == 1
    assert resultado["total_pendentes"] == 0


def test_usa_data_criacao_quando_nao_ha_data_inicio() -> None:
    """Sem `data_inicio`, a duração é medida a partir de `data_criacao`."""
    tarefa = criar_tarefa(1, horas_ate_conclusao=5.0)
    del tarefa["data_inicio"]

    resultado = analyze_tasks([tarefa])

    assert resultado["tempo_medio_conclusao_horas"] == 5.0


# --- Cenário 2: exceção / erro ------------------------------------------------


def test_excecao_para_datas_inconsistentes() -> None:
    """Dado conclusão anterior à criação, então TaskValidationError é lançada."""
    tarefa = criar_tarefa(1)
    tarefa["data_conclusao"] = BASE - timedelta(hours=3)

    with pytest.raises(TaskValidationError, match="anterior a 'data_criacao'"):
        analyze_tasks([tarefa])


def test_excecao_para_campo_obrigatorio_ausente() -> None:
    """A ausência de um campo obrigatório é reportada com o nome do campo."""
    tarefa = criar_tarefa(1)
    del tarefa["prazo"]

    with pytest.raises(TaskValidationError, match="'prazo' ausente"):
        analyze_tasks([tarefa])


def test_excecao_para_prioridade_invalida() -> None:
    """Prioridade fora do domínio permitido é rejeitada."""
    tarefa = criar_tarefa(1, prioridade="urgentissima")

    with pytest.raises(TaskValidationError, match="'prioridade' invalida"):
        analyze_tasks([tarefa])


def test_excecao_para_status_invalido() -> None:
    """Status fora do domínio permitido é rejeitado."""
    tarefa = criar_tarefa(1)
    tarefa["status"] = "em_andamento"

    with pytest.raises(TaskValidationError, match="'status' invalido"):
        analyze_tasks([tarefa])


def test_excecao_para_concluida_sem_data_conclusao() -> None:
    """Tarefa concluída sem `data_conclusao` viola o contrato."""
    tarefa = criar_tarefa(1, horas_ate_conclusao=None)

    with pytest.raises(TaskValidationError, match="'data_conclusao' obrigatoria"):
        analyze_tasks([tarefa])


def test_excecao_para_tipo_de_data_incorreto() -> None:
    """Campo de data que não é `datetime` é rejeitado com mensagem clara."""
    tarefa = criar_tarefa(1)
    tarefa["prazo"] = "2026-10-01"

    with pytest.raises(TaskValidationError, match="deve ser datetime"):
        analyze_tasks([tarefa])


def test_excecao_para_entrada_que_nao_e_lista() -> None:
    """A entrada precisa ser uma lista de tarefas."""
    with pytest.raises(TaskValidationError, match="esperado list"):
        analyze_tasks({"id_tarefa": 1})  # type: ignore[arg-type]


# --- Casos de borda -----------------------------------------------------------


def test_lista_vazia_retorna_metricas_zeradas() -> None:
    """Lista vazia devolve a estrutura completa com zeros, sem exceção."""
    resultado = analyze_tasks([])

    assert resultado["total_tarefas"] == 0
    assert resultado["total_concluidas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0
    assert set(resultado["indicadores_por_prioridade"]) == {"alta", "baixa", "media"}


def test_apenas_pendentes_retorna_metricas_zeradas() -> None:
    """Sem tarefas concluídas, as médias são 0.0 e nenhuma divisão por zero ocorre."""
    tarefas = [
        criar_tarefa(1, status="pendente", horas_ate_conclusao=None),
        criar_tarefa(2, status="cancelada", horas_ate_conclusao=None),
    ]

    resultado = analyze_tasks(tarefas)

    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_conclusao_no_prazo_nao_conta_como_atraso() -> None:
    """Conclusão exatamente no prazo não é contabilizada como atraso."""
    tarefa = criar_tarefa(1, horas_ate_conclusao=8.0, horas_ate_prazo=8.0)

    resultado = analyze_tasks([tarefa])

    assert resultado["taxa_atraso_percentual"] == 0.0


def test_valores_arredondados_para_duas_casas() -> None:
    """Os valores de ponto flutuante têm no máximo duas casas decimais."""
    tarefas = [
        criar_tarefa(1, horas_ate_conclusao=1.0),
        criar_tarefa(2, horas_ate_conclusao=2.0),
        criar_tarefa(3, horas_ate_conclusao=4.0),
    ]

    resultado = analyze_tasks(tarefas)

    assert resultado["tempo_medio_conclusao_horas"] == 2.33
