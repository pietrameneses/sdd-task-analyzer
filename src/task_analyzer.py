"""Módulo de análise de tarefas e produtividade (TaskAnalyzer).

Implementa o contrato executável definido em `specs/task_analyzer_spec.md`
e segue as diretrizes de `CONTEXT_RULES.md`.

Código gerado via assistente de IA e homologado por revisão humana.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Final

logger: Final[logging.Logger] = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: Final[frozenset[str]] = frozenset({"baixa", "media", "alta"})
STATUS_VALIDOS: Final[frozenset[str]] = frozenset({"concluida", "pendente", "cancelada"})
CAMPOS_OBRIGATORIOS: Final[tuple[str, ...]] = (
    "id_tarefa",
    "prioridade",
    "status",
    "data_criacao",
    "prazo",
)
SEGUNDOS_POR_HORA: Final[int] = 3600
CASAS_DECIMAIS: Final[int] = 2


class TaskValidationError(Exception):
    """Erro de validação de uma tarefa de entrada.

    Levantada quando uma tarefa não atende ao contrato de interface: campo
    obrigatório ausente, tipo incorreto, valor fora do domínio permitido ou
    datas inconsistentes entre si.
    """


def _exigir_campos_obrigatorios(tarefa: dict[str, Any], indice: int) -> None:
    """Valida a presença dos campos obrigatórios de uma tarefa.

    Args:
        tarefa: Dicionário que representa uma tarefa.
        indice: Posição da tarefa na lista de entrada, usada na mensagem de erro.

    Raises:
        TaskValidationError: Se algum campo obrigatório estiver ausente ou nulo.
    """
    for campo in CAMPOS_OBRIGATORIOS:
        if tarefa.get(campo) is None:
            raise TaskValidationError(
                f"Tarefa na posicao {indice}: campo obrigatorio '{campo}' ausente."
            )


def _exigir_datetime(valor: Any, campo: str, id_tarefa: Any) -> datetime:
    """Garante que um valor seja um `datetime`.

    Args:
        valor: Valor a ser verificado.
        campo: Nome do campo, usado na mensagem de erro.
        id_tarefa: Identificador da tarefa, usado na mensagem de erro.

    Returns:
        O próprio valor, já tipado como `datetime`.

    Raises:
        TaskValidationError: Se o valor não for um `datetime`.
    """
    if not isinstance(valor, datetime):
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: campo '{campo}' deve ser datetime, "
            f"recebido {type(valor).__name__}."
        )
    return valor


def _validar_tarefa(tarefa: Any, indice: int) -> dict[str, Any]:
    """Valida uma tarefa individual contra o contrato de interface.

    Args:
        tarefa: Item da lista de entrada, esperado como dicionário.
        indice: Posição do item na lista de entrada.

    Returns:
        A tarefa validada.

    Raises:
        TaskValidationError: Se a tarefa violar qualquer regra do contrato.
    """
    if not isinstance(tarefa, dict):
        raise TaskValidationError(
            f"Tarefa na posicao {indice}: esperado dicionario, "
            f"recebido {type(tarefa).__name__}."
        )

    _exigir_campos_obrigatorios(tarefa, indice)

    id_tarefa = tarefa["id_tarefa"]
    if not isinstance(id_tarefa, int) or isinstance(id_tarefa, bool) or id_tarefa <= 0:
        raise TaskValidationError(
            f"Tarefa na posicao {indice}: 'id_tarefa' deve ser inteiro maior que zero."
        )

    prioridade = tarefa["prioridade"]
    if prioridade not in PRIORIDADES_VALIDAS:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: 'prioridade' invalida ('{prioridade}'). "
            f"Valores aceitos: {sorted(PRIORIDADES_VALIDAS)}."
        )

    status = tarefa["status"]
    if status not in STATUS_VALIDOS:
        raise TaskValidationError(
            f"Tarefa {id_tarefa}: 'status' invalido ('{status}'). "
            f"Valores aceitos: {sorted(STATUS_VALIDOS)}."
        )

    data_criacao = _exigir_datetime(tarefa["data_criacao"], "data_criacao", id_tarefa)
    prazo = _exigir_datetime(tarefa["prazo"], "prazo", id_tarefa)

    data_inicio = tarefa.get("data_inicio")
    if data_inicio is not None:
        data_inicio = _exigir_datetime(data_inicio, "data_inicio", id_tarefa)
        if data_inicio < data_criacao:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: 'data_inicio' anterior a 'data_criacao'."
            )

    data_conclusao = tarefa.get("data_conclusao")
    if status == "concluida":
        if data_conclusao is None:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: 'data_conclusao' obrigatoria para status "
                f"'concluida'."
            )
        data_conclusao = _exigir_datetime(data_conclusao, "data_conclusao", id_tarefa)
        if data_conclusao < data_criacao:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: 'data_conclusao' anterior a 'data_criacao'."
            )
        referencia_inicio = data_inicio if data_inicio is not None else data_criacao
        if data_conclusao < referencia_inicio:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: 'data_conclusao' anterior a 'data_inicio'."
            )
    elif data_conclusao is not None:
        data_conclusao = _exigir_datetime(data_conclusao, "data_conclusao", id_tarefa)
        if data_conclusao < data_criacao:
            raise TaskValidationError(
                f"Tarefa {id_tarefa}: 'data_conclusao' anterior a 'data_criacao'."
            )

    return tarefa


def _calcular_duracao_horas(tarefa: dict[str, Any]) -> float:
    """Calcula a duração de uma tarefa concluída, em horas.

    A referência de início é `data_inicio` quando informada e `data_criacao`
    caso contrário, conforme a regra RN02 da especificação.

    Args:
        tarefa: Tarefa concluída e previamente validada.

    Returns:
        A duração em horas, como número de ponto flutuante.
    """
    inicio: datetime = tarefa.get("data_inicio") or tarefa["data_criacao"]
    conclusao: datetime = tarefa["data_conclusao"]
    return (conclusao - inicio).total_seconds() / SEGUNDOS_POR_HORA


def _esta_atrasada(tarefa: dict[str, Any]) -> bool:
    """Informa se uma tarefa concluída foi entregue após o prazo.

    Conclusão exatamente no prazo não é considerada atraso (regra RN03).

    Args:
        tarefa: Tarefa concluída e previamente validada.

    Returns:
        `True` quando a conclusão é posterior ao prazo, `False` caso contrário.
    """
    return tarefa["data_conclusao"] > tarefa["prazo"]


def _media(valores: list[float]) -> float:
    """Calcula a média de uma lista, devolvendo 0.0 quando ela está vazia.

    Evita divisão por zero conforme a regra RN06 da especificação.

    Args:
        valores: Lista de números.

    Returns:
        A média arredondada para duas casas decimais, ou 0.0 se não houver dados.
    """
    if not valores:
        return 0.0
    return round(sum(valores) / len(valores), CASAS_DECIMAIS)


def _percentual(parte: int, total: int) -> float:
    """Calcula um percentual protegido contra divisão por zero.

    Args:
        parte: Quantidade observada.
        total: Quantidade total de referência.

    Returns:
        O percentual arredondado para duas casas decimais, ou 0.0 se o total
        for zero.
    """
    if total == 0:
        return 0.0
    return round((parte / total) * 100, CASAS_DECIMAIS)


def _montar_indicadores(concluidas: list[dict[str, Any]]) -> dict[str, float | int]:
    """Monta o bloco de indicadores para um conjunto de tarefas concluídas.

    Args:
        concluidas: Tarefas concluídas e validadas.

    Returns:
        Dicionário com total, tempo médio de conclusão em horas e taxa de
        atraso percentual.
    """
    duracoes = [_calcular_duracao_horas(tarefa) for tarefa in concluidas]
    atrasadas = sum(1 for tarefa in concluidas if _esta_atrasada(tarefa))
    return {
        "total_concluidas": len(concluidas),
        "tempo_medio_conclusao_horas": _media(duracoes),
        "taxa_atraso_percentual": _percentual(atrasadas, len(concluidas)),
    }


def analyze_tasks(tarefas: list[dict[str, Any]]) -> dict[str, Any]:
    """Analisa uma lista de tarefas e devolve métricas de produtividade.

    Considera apenas tarefas com status `concluida` nos cálculos de tempo médio
    e taxa de atraso. Tarefas canceladas são ignoradas. Listas vazias ou sem
    tarefas concluídas produzem métricas zeradas, sem lançar exceção.

    Args:
        tarefas: Lista de dicionários, cada um representando uma tarefa conforme
            o contrato de interface da especificação.

    Returns:
        Dicionário com `total_tarefas`, `total_concluidas`, `total_pendentes`,
        `tempo_medio_conclusao_horas`, `taxa_atraso_percentual` e
        `indicadores_por_prioridade`.

    Raises:
        TaskValidationError: Se a entrada não for uma lista ou se alguma tarefa
            violar o contrato de interface.
    """
    if not isinstance(tarefas, list):
        raise TaskValidationError(
            f"Entrada invalida: esperado list, recebido {type(tarefas).__name__}."
        )

    validadas = [_validar_tarefa(tarefa, indice) for indice, tarefa in enumerate(tarefas)]
    logger.info("Tarefas recebidas para analise: %d", len(validadas))

    concluidas = [tarefa for tarefa in validadas if tarefa["status"] == "concluida"]
    pendentes = [tarefa for tarefa in validadas if tarefa["status"] == "pendente"]

    indicadores_gerais = _montar_indicadores(concluidas)
    resultado: dict[str, Any] = {
        "total_tarefas": len(validadas),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(pendentes),
        "tempo_medio_conclusao_horas": indicadores_gerais["tempo_medio_conclusao_horas"],
        "taxa_atraso_percentual": indicadores_gerais["taxa_atraso_percentual"],
        "indicadores_por_prioridade": {
            prioridade: _montar_indicadores(
                [tarefa for tarefa in concluidas if tarefa["prioridade"] == prioridade]
            )
            for prioridade in sorted(PRIORIDADES_VALIDAS)
        },
    }

    logger.info(
        "Analise concluida: %d concluidas, %d pendentes, taxa de atraso %.2f%%",
        resultado["total_concluidas"],
        resultado["total_pendentes"],
        resultado["taxa_atraso_percentual"],
    )
    return resultado
