# 🏨 Restful Booker API Automation

> **Automação de Testes de API REST Profissional** — Python · Pytest · Requests · Pydantic · CI/CD

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-8.2%2B-green?logo=pytest)](https://docs.pytest.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.7%2B-purple?logo=pydantic)](https://docs.pydantic.dev/)
[![Requests](https://img.shields.io/badge/Requests-2.32%2B-orange?logo=python)](https://requests.readthedocs.io/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI%2FCD-blue?logo=githubactions)](.github/workflows/api-tests.yml)

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Stack Tecnológica](#-stack-tecnológica)
- [Estratégia de Testes](#-estratégia-de-testes)
- [Validação de Contrato com Pydantic](#-validação-de-contrato-com-pydantic)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Execução](#-instalação-e-execução)
- [Solução de Problemas](#-solução-de-problemas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pipeline CI/CD](#-pipeline-cicd)
- [Relatórios](#-relatórios)
- [Contato](#-contato)

---

## 🎯 Sobre o Projeto

Este projeto é uma **suite completa de automação de testes de API REST** desenvolvida para demonstrar expertise em **Quality Assurance de Backend**. A automação cobre o fluxo completo de CRUD (Create, Read, Update, Delete) da API pública **Restful Booker**, incluindo autenticação JWT, validação rigorosa de contratos JSON e execução contínua via CI/CD.

A API Restful Booker é uma plataforma de aprendizado mantida por [Mark Winteringham](https://github.com/mwinteringham/restful-booker), projetada para ensinar boas práticas de testes de API e intencionalmente contém bugs sutis para exercitar habilidades de QA.

**Base URL:** `https://restful-booker.herokuapp.com`

---

## 🛠 Stack Tecnológica

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.11+ | Linguagem principal |
| **Pytest** | 8.2+ | Framework de testes com fixtures e parametrização |
| **Requests** | 2.32+ | Cliente HTTP para requisições REST |
| **Pydantic** | 2.7+ | Validação de contrato e tipagem estrita de schemas JSON |
| **pytest-html** | 4.1+ | Geração de relatórios HTML interativos |
| **GitHub Actions** | — | Pipeline CI/CD automatizada |

---

## 🧪 Estratégia de Testes

A suite de testes foi projetada seguindo os princípios da **Pirâmide de Testes** e **Testes de Contrato First**:

### 1. Testes de Autenticação (`tests/test_auth.py`)
- ✅ Geração de token JWT com credenciais válidas
- ✅ Validação de headers de resposta (`Content-Type`, `Status Code`)
- ✅ Comportamento com credenciais inválidas (teste de segurança)
- ✅ Casos de borda: payload vazio, campos ausentes

### 2. Testes de CRUD (`tests/test_booking_crud.py`)
- **CREATE (POST)** — Criar reservas com dados válidos e inválidos
- **READ (GET)** — Buscar todas as reservas, buscar por ID, filtros com query params
- **UPDATE (PUT)** — Atualização completa com autenticação obrigatória
- **PARTIAL UPDATE (PATCH)** — Atualização parcial de campos específicos
- **DELETE** — Exclusão com verificação de remoção
- **END-TO-END** — Fluxo completo CRUD em um único teste

### 3. Testes de Segurança
- 🔒 Tentativa de operações protegidas sem token JWT
- 🔒 Validação de retorno `403 Forbidden` para acessos não autorizados

### 4. Documentação de Bugs Conhecidos
A API Restful Booker contém bugs intencionais. Os testes documentam:
- DELETE retorna `201 Created` ao invés de `204 No Content`
- DELETE de ID inexistente retorna `405` ao invés de `404`
- Datas em formato inválido são aceitas mas corrompidas
- Autenticação só funciona via Cookie, não via header `Authorization`
- PUT em ID inexistente retorna `405` ao invés de `404`

---

## 🔐 Validação de Contrato com Pydantic

A validação de contrato é um dos pilares deste projeto. Utilizamos **Pydantic v2** para garantir que:

1. **Tipagem Estrita:** Cada campo possui tipo definido (`str`, `int`, `bool`, `datetime`)
2. **Constraints de Negócio:** Validações como `totalprice >= 0`, `bookingid > 0`, regex para datas `YYYY-MM-DD`
3. **Imutabilidade:** Schemas são modelos imutáveis que falham fast em caso de violação
4. **Auto-documentação:** Os schemas servem como documentação viva da API

### Exemplo de Schema — BookingDates
```python
class BookingDates(BaseModel):
    checkin: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    checkout: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")

    @field_validator("checkout")
    @classmethod
    def checkout_after_checkin(cls, v: str, info) -> str:
        if info.data.get("checkin") and v <= info.data["checkin"]:
            raise ValueError("Checkout must be after checkin")
        return v
```

### Benefícios
- 🚀 **Fail Fast:** Erros de contrato são detectados imediatamente
- 📊 **Relatórios Claros:** Mensagens de erro do Pydantic são descritivas
- 🔄 **Manutenibilidade:** Mudanças na API são detectadas automaticamente nos testes
- 🛡️ **Segurança:** Previne injeção de dados malformados

---

## 📦 Pré-requisitos

- **Python** 3.11 ou superior ([Download](https://www.python.org/downloads/))
  - ⚠️ **Nota:** Python 3.14 é uma versão de desenvolvimento instável. Recomendamos **Python 3.12** para máxima compatibilidade.
- **Git** ([Download](https://git-scm.com/downloads))
- **VS Code** (recomendado) com extensões:
  - Python (Microsoft)
  - Pylance
  - Python Test Explorer

---

## 🚀 Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/restful-booker-api-automation.git
cd restful-booker-api-automation
```

### 2. Crie e ative o ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute os testes
```bash
# Execução padrão
pytest

# Com relatório HTML
pytest --html=reports/report.html --self-contained-html

# Com verbose e cores
pytest -v --color=yes --tb=short

# Apenas testes de autenticação
pytest tests/test_auth.py -v

# Apenas testes de CRUD
pytest tests/test_booking_crud.py -v
```

### 5. Visualize o relatório
```bash
# Windows
start reports/report.html

# macOS
open reports/report.html

# Linux
xdg-open reports/report.html
```

---

## 🔧 Solução de Problemas

### Erro ao criar venv com Python 3.14
Se você receber erro ao executar `python -m venv venv` com Python 3.14:

**Opção 1 — Usar Python 3.12 (Recomendado):**
```bash
# Instale Python 3.12 e use-o explicitamente
py -3.12 -m venv venv
venv\Scripts\activate
```

**Opção 2 — Instalar pip manualmente no venv:**
```bash
python -m venv venv --without-pip
venv\Scripts\activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip install -r requirements.txt
```

**Opção 3 — Usar instalação global (sem venv):**
```bash
# Não recomendado para produção, mas funciona para testes rápidos
pip install --user -r requirements.txt
pytest
```

### Erro "No module named 'pytest'"
Certifique-se de que o ambiente virtual está ativado (você verá `(venv)` no prompt).

### Erro de SSL/Certificado
```bash
# Windows — desativar verificação SSL temporariamente (apenas para testes locais)
set PYTHONHTTPSVERIFY=0
pytest
```

---

## 📁 Estrutura do Projeto

```
restful-booker-api-automation/
│
├── .github/
│   └── workflows/
│       └── api-tests.yml          # Pipeline CI/CD GitHub Actions
│
├── schemas/                        # Schemas Pydantic para validação de contrato
│   ├── __init__.py
│   ├── auth_schema.py             # Modelos de autenticação
│   └── booking_schema.py          # Modelos de reservas
│
├── tests/                          # Suite de testes Pytest
│   ├── __init__.py
│   ├── conftest.py                # Fixtures compartilhadas
│   ├── test_auth.py               # Testes de autenticação
│   └── test_booking_crud.py       # Testes de CRUD
│
├── utils/                          # Utilitários e helpers
│   ├── __init__.py
│   └── api_client.py              # Cliente HTTP encapsulado
│
├── reports/                        # Relatórios HTML gerados (gitignored)
├── .gitignore                      # Arquivos ignorados pelo Git
├── pytest.ini                     # Configurações do Pytest
├── requirements.txt               # Dependências do projeto
└── README.md                      # Documentação do projeto
```

---

## 🔄 Pipeline CI/CD

O pipeline GitHub Actions executa automaticamente:

1. **Trigger:** Push para `main`/`develop`, Pull Requests ou cron diário
2. **Matrix:** Testes em Python 3.11 e 3.12
3. **Instalação:** Setup do ambiente e dependências
4. **Execução:** `pytest` com relatório HTML
5. **Artefatos:** Upload dos relatórios para download

**Status do Pipeline:**
![GitHub Actions](https://github.com/seu-usuario/restful-booker-api-automation/workflows/API%20Automation%20Tests/badge.svg)

---

## 📊 Relatórios

Os relatórios HTML gerados pelo `pytest-html` incluem:
- ✅ Resumo de pass/fail por teste
- ⏱️ Duração de cada teste
- 📝 Logs de stdout/stderr
- 🔍 Detalhes de falhas com traceback
- 📸 Screenshots de contexto (quando configurado)

---

## 👤 Autor

**Alexandre Claudino**
- 🔗 [LinkedIn](https://www.linkedin.com/in/alexandreclaudino)
- 🐙 [GitHub](https://github.com/aleclaudino17-collab)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

> 💡 **Dica para Portfólio:** Este projeto demonstra competências em automação de API, validação de contrato, design de testes, CI/CD e boas práticas de engenharia de software. Ideal para posições de QA Engineer, SDET e Test Automation Engineer.
