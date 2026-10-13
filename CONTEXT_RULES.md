# CONTEXT_RULES — Governança de Contexto para Agentes de IA

Regras persistentes fornecidas ao assistente de IA em toda solicitação de geração de código neste projeto. Transpostas da Fase 1 (especificação SDD).

## 1. Diretrizes Arquiteturais (obrigatórias)

- Linguagem Python na versão 3.11 ou superior.
- Uso de type hints em 100% das funções, métodos e parâmetros.
- Aderência ao PEP 8 e ao princípio de responsabilidade única (SRP).
- Documentação formal em docstrings no padrão Google, para módulos, funções e parâmetros.
- Funções pequenas, coesas e com um único propósito.
- Tratamento de exceções específico, com mensagens claras, usando a exceção customizada `TaskValidationError`.
- Logs estruturados com o módulo padrão `logging`, nunca com `print`.
- Prevenção explícita de divisão por zero.
- Nomes de variáveis e funções descritivos, mantendo o mesmo idioma em todo o projeto.
- Separação entre a lógica de cálculo (`src/`) e a validação automatizada (`tests/`).

## 2. Proibições Explícitas (regras restritivas)

- Não utilizar bibliotecas externas não autorizadas; apenas a biblioteca padrão do Python e o `pytest` para os testes.
- Não alterar, remover ou adaptar os cenários de teste definidos na especificação.
- Não modificar a estrutura de pastas definida neste repositório.
- Não persistir dados em arquivos ou bancos de dados.
- Não alterar a assinatura de `analyze_tasks` sem autorização.
- Não gerar código sem os testes correspondentes.
- Não inserir código duplicado ou desnecessário.
- Não comentar código em excesso, apenas onde o motivo não for evidente pela leitura.
- Não assumir comportamentos que não estejam especificados no contrato de negócio.
- Não retornar valores diferentes dos definidos no contrato de saída.

## 3. Regras de Interação com a IA

- Fornecer sempre o contexto completo antes da solicitação: este arquivo e `specs/task_analyzer_spec.md`.
- Validar cada trecho gerado contra o contrato antes de aceitá-lo.
- Solicitar explicação sempre que houver dúvida sobre a solução proposta, em vez de aceitar código que não se saiba explicar.
- Revisar criticamente todo o código gerado, sem exceção.
- Rejeitar e refazer qualquer resposta que viole as proibições da seção 2.
