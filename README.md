# QICR — Quadruple-based Intent Conflict Resolution

Implementação e ambiente de simulação do esquema **QICR** (*Quadruple-based Intent Conflict Resolution*) para detecção e resolução automática de conflitos de intenções em Redes Orientadas a Intenções (IDN/SDN), utilizando Grafo de Conhecimento (`NetworkX`), validação de modelos (`Pydantic`) e linguagem declarativa **Nile**.

---

## Estrutura Principal do Projeto

```text
qicr_project/
├── src/
│   ├── core/
│   │   ├── kg.py            # Grafo de Conhecimento (topologia hierárquica e nós atômicos)
│   │   └── engine.py        # Motor QICR (detecção, decomposição, deny-overrides e DAG SFC)
│   ├── domain/
│   │   ├── models.py        # Modelo Pydantic da quádrupla de intenção
│   │   ├── parser.py        # Parser e validador sintático Nile
│   │   └── exceptions.py    # Exceções de domínio
│   ├── repository/
│   │   ├── interfaces.py    # Interface do repositório de intenções ativas
│   │   └── memory.py        # Implementação em memória do repositório
│   └── scheduler/
│       └── calendar.py      # Módulo de janelamento temporal (CalendarModule)
├── simulacao.py             # Simulação principal com 500 intenções (5 janelas de 100)
└── requirements.txt         # Dependências Python do projeto
```

---

## Pré-requisitos

* **Python 3.11 ou superior** (testado em Python 3.14.4; compatível com `!=3.14.1,>=3.11` exigido pelo `networkx==3.6.1`)
* `pip` e `venv` habilitados

---

## Instalação

### 1. Baixe o projeto e acesse a pasta

Se estiver usando Git:
```bash
git clone <URL_DO_REPOSITORIO>
cd qicr_project
```
*(Ou baixe/extraia os arquivos do projeto e entre na pasta raiz `qicr_project` pelo terminal.)*

### 2. Crie e ative o ambiente virtual (`venv`)

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bat
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Instale as dependências

Com o ambiente virtual ativado, execute:
```bash
pip install -r requirements.txt
```

---

## Como Executar a Simulação (`simulacao.py`)

Certifique-se de estar na pasta raiz do projeto e com o ambiente virtual `(venv)` ativado.

### Opção 1: Executar salvando toda a saída em arquivo (recomendado)

Como a simulação processa 500 intenções e gera milhares de linhas de log detalhando cada conflito e resolução, o terminal pode ocultar as linhas iniciais. Para visualizar no terminal **e** salvar a saída completa em `saida_simulacao.txt`:

**Linux / macOS (ou Git Bash no Windows):**
```bash
python simulacao.py 2>&1 | tee saida_simulacao.txt
```

**Windows (PowerShell):**
```powershell
python simulacao.py 2>&1 | Tee-Object -FilePath saida_simulacao.txt
```

Após a execução, abra o arquivo `saida_simulacao.txt` em qualquer editor de texto para consultar todo o processamento na íntegra.

### Opção 2: Execução direta no terminal

Para rodar a simulação exibindo os logs e a tabela resumo diretamente no terminal sem gerar arquivo:
```bash
python simulacao.py
```

---

## O que a `simulacao.py` executa

Ao rodar o script, quatro módulos são executados sequencialmente:
1. **Módulo 1 — Validação Topológica:** constrói e valida o Grafo de Conhecimento corporativo (17 nós atômicos: 12 IPs de usuários na Matriz e 5 servidores no Datacenter).
2. **Módulo 2 — Auditoria do Parser Nile:** submete as 500 intenções escritas por extenso ao `NileParser`, listando quantas foram traduzidas, quantas foram rejeitadas e os motivos técnicos de cada rejeição.
3. **Módulo 3 — Execução Multitemporal:** envia as intenções em **5 janelamentos sequenciais de 100 intenções**, exibindo o recebimento pelo `CalendarModule`, os conflitos encontrados e a resolução pelo `QICREngine`.
4. **Módulo 4 — Tabela Resumo e Síntese Final:** imprime a tabela comparativa com as 19 métricas avaliadas por janela (aceitação do compilador, conflitos encontrados/resolvidos, regras finais, tempos de parsing/motor/janelamento, latência e uso de memória) e a síntese consolidada do experimento.
