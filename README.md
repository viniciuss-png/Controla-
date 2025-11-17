# Controlaê - Backend API

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Django 5.2.7](https://img.shields.io/badge/Django-5.2.7-darkgreen)](https://www.djangoproject.com/)
[![DRF 3.16](https://img.shields.io/badge/DRF-3.16-red)](https://www.django-rest-framework.org/)
[![Tests: 25/25 Passing](https://img.shields.io/badge/Tests-25%2F25%20✓-brightgreen)]()
[![Coverage 76%](https://img.shields.io/badge/Coverage-76%25-yellowgreen)]()

**Controlaê** é uma plataforma de gestão financeira desenvolvida para alunos do ensino médio que recebem o benefício **Pé-de-Meia**. O sistema permite que os beneficiários rastreiem receitas, despesas, contas bancárias e metas de poupança.

# Índice

- [Visão Geral](#visão-geral)
- [Tecnologias](#tecnologias)
- [Instalação e Setup](#instalação-e-setup)
- [Configuração](#configuração)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Autenticação](#autenticação)
- [Exemplos de Uso](#exemplos-de-uso)
- [Testes](#testes)
- [Banco de Dados](#banco-de-dados)
- [Segurança](#segurança)
- [Troubleshooting](#troubleshooting)

---

# Visão Geral

# Problema Resolvido
Alunos do ensino médio que recebem o Pé-de-Meia (benefício governamental) precisam de ferramentas simples e seguras para:
- Registrar entradas (Pé-de-Meia, bolsas, mesada)
- Categorizar despesas
- Gerenciar múltiplas contas
- Rastrear metas de poupança

# Funcionalidades Principais
 **Autenticação JWT** - Segura e escalável  
 **Isolamento de Dados** - Cada usuário vê apenas seus dados  
 **CRUD Completo** - Categorias, Contas, Transações, Metas  
 **Transações Atômicas** - Transferências e depósitos garantem integridade  
 **Validações Robustas** - Campos obrigatórios, valores positivos, isolamento por usuário  
 **Testes Automatizados** - 25 testes com 76% de cobertura  
 **CORS Configurado** - Frontend e backend rodando em portas diferentes  

---

# Tecnologias

| Tecnologia | Versão | Propósito |
|-----------|--------|----------|
| **Python** | 3.13 | Linguagem base |
| **Django** | 5.2.7 | Framework web |
| **Django REST Framework** | 3.16.1 | API RESTful |
| **djangorestframework-simplejwt** | 5.5.1 | Autenticação JWT |
| **django-cors-headers** | 4.9.0 | CORS para frontend |
| **SQLite** | 3 | Banco de dados (desenvolvimento) |
| **pytest** | 9.0.1 | Framework de testes |
| **pytest-django** | 4.11.1 | Integração Django com pytest |

---

# Instalação e Setup

# Pré-requisitos
- Python 3.13+
- pip (gerenciador de pacotes Python)
- Git

# 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/Backend_Controlae.git
cd Backend_Controlae
```

# 2. Criar Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

# 4. Configurar Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```env
# Django Settings
SECRET_KEY=sua-chave-secreta-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Timezone e Idioma
TIME_ZONE=America/Sao_Paulo
LANGUAGE_CODE=pt-br

# JWT Settings
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
```

# 5. Executar Migrações

```bash
python manage.py migrate
```

# 6. Criar Superusuário (Opcional)

```bash
python manage.py createsuperuser
```

# 7. Iniciar Servidor

```bash
python manage.py runserver
```

O servidor estará disponível em: `http://127.0.0.1:8000/`

---

# Configuração

# Estrutura de Diretórios

```
Backend_Controlae/
├── controlae/                 # Configurações do projeto
│   ├── settings.py            # Configurações Django
│   ├── urls.py                # URLs principais
│   ├── asgi.py                # ASGI config
│   └── wsgi.py                # WSGI config
├── core/                      # Aplicação principal
│   ├── models.py              # Modelos do BD
│   ├── views.py               # ViewSets da API
│   ├── serializers.py         # Serializers
│   ├── permissions.py         # Permissões customizadas
│   ├── services.py            # Lógica de negócio
│   ├── signals.py             # Sinais Django
│   ├── tests.py               # Testes unitários
│   └── migrations/            # Histórico de migrações
├── db.sqlite3                 # Banco de dados
├── manage.py                  # CLI do Django
├── requirements.txt           # Dependências
├── pytest.ini                 # Configuração pytest
├── README.md                  # Este arquivo
└── .env                       # Variáveis de ambiente (não versionado)
```

# Variáveis de Ambiente Importantes

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DEBUG` | False | Modo desenvolvimento |
| `SECRET_KEY` | - | Chave secreta para sessões |
| `TIME_ZONE` | America/Sao_Paulo | Fuso horário |
| `CORS_ALLOWED_ORIGINS` | localhost:3000 | Origens CORS permitidas |

---

# Estrutura do Projeto

# Modelos de Dados

# 1. **User** (Django built-in)
```python
{
  "id": 1,
  "username": "joao_silva",
  "email": "joao@example.com",
  "first_name": "João",
  "last_name": "Silva"
}
```

# 2. **PerfilAluno** (Perfil do Aluno)
```python
{
  "usuario": 1,
  "serie_em": 1,              # 1º, 2º ou 3º ano
  "ano_registro": 2024,
  "concluiu": false
}
```

# 3. **Categoria** (Categorização de Transações)
```python
{
  "id": 1,
  "nome": "Alimentação",
  "tipo_categoria": "saida",  # 'entrada' ou 'saida'
  "usuario": 1
}
```

# 4. **Conta** (Contas Bancárias)
```python
{
  "id": 1,
  "nome": "Conta Corrente Banco XYZ",
  "saldo_inicial": 1000.00,
  "usuario": 1
}
```

# 5. **Transacao** (Transações Financeiras)
```python
{
  "id": 1,
  "usuario": 1,
  "categoria": 1,
  "conta": 1,
  "tipo": "entrada",
  "descricao": "Recebimento Pé-de-Meia",
  "valor": 200.00,
  "data": "2024-01-15",
  "parcelas": 1,
  "vencimento": null,
  "pago": true
}
```

# 6. **MetaFinanceira** (Metas de Poupança)
```python
{
  "id": 1,
  "usuario": 1,
  "nome": "Viagem de Férias",
  "valor_alvo": 1500.00,
  "conta_vinculada": 2,
  "data_alvo": "2024-12-20",
  "ativa": true,
  "valor_atual": 450.00 
}
```

---

# API Endpoints

# Autenticação

# Registrar Novo Usuário
```
POST /api/register/
Content-Type: application/json

{
  "username": "novo_usuario",
  "password": "senha_segura_123",
  "serie_em": 1
}

Response: 201 Created
{
  "id": 5,
  "username": "novo_usuario"
}
```

# Obter Token JWT
```
POST /api/token/
Content-Type: application/json

{
  "username": "novo_usuario",
  "password": "senha_segura_123"
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

# Renovar Token
```
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

# Categorias

## Listar Categorias
```
GET /api/categorias/
Authorization: Bearer {access_token}

Response: 200 OK
[
  {
    "id": 1,
    "nome": "Alimentação",
    "tipo_categoria": "saida"
  },
  {
    "id": 2,
    "nome": "Pé-de-Meia",
    "tipo_categoria": "entrada"
  }
]
```

# Criar Categoria
```
POST /api/categorias/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "nome": "Transporte",
  "tipo_categoria": "saida"
}

Response: 201 Created
```

# Atualizar Categoria
```
PUT /api/categorias/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "nome": "Transporte Urbano",
  "tipo_categoria": "saida"
}

Response: 200 OK
```

# Deletar Categoria
```
DELETE /api/categorias/{id}/
Authorization: Bearer {access_token}

Response: 204 No Content
```

# Contas

# Listar Contas
```
GET /api/contas/
Authorization: Bearer {access_token}

Response: 200 OK
[
  {
    "id": 1,
    "nome": "Conta Corrente",
    "saldo_inicial": 1000.00
  }
]
```

# Criar Conta
```
POST /api/contas/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "nome": "Poupança Meta",
  "saldo_inicial": 500.00
}

Response: 201 Created
```

# Transferir Entre Contas
```
POST /api/contas/{id}/transferir/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "conta_destino_id": 2,
  "valor": 250.00
}

Response: 200 OK
{
  "message": "Transferência realizada com sucesso"
}
```

# Transações

# Listar Transações
```
GET /api/transacoes/
Authorization: Bearer {access_token}

Response: 200 OK
[
  {
    "id": 1,
    "tipo": "entrada",
    "descricao": "Recebimento Pé-de-Meia",
    "valor": 200.00,
    "data": "2024-01-15",
    "categoria_nome": "Pé-de-Meia",
    "conta_nome": "Conta Corrente",
    "pago": true
  }
]
```

# Criar Transação
```
POST /api/transacoes/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "categoria": 1,
  "conta": 1,
  "tipo": "saida",
  "descricao": "Almoço na cantina",
  "valor": 25.50,
  "data": "2024-01-20",
  "parcelas": 1,
  "pago": false
}

Response: 201 Created
```

# Resumo Financeiro
```
GET /api/transacoes/resumo_financeiro/?from_date=2024-01-01&to_date=2024-01-31
Authorization: Bearer {access_token}

Response: 200 OK
{
  "total_entradas": 2000.00,
  "total_saidas": 450.00,
  "saldo": 1550.00,
  "por_categoria": {
    "Pé-de-Meia": 2000.00,
    "Alimentação": 300.00,
    "Transporte": 150.00
  }
}
```

# Confirmar Recebimento Pé-de-Meia
```
POST /api/transacoes/confirmar_recebimento/?mes=1&ano=2024
Authorization: Bearer {access_token}

Response: 200 OK
{
  "message": "Frequência confirmada para janeiro/2024"
}
```

# Metas Financeiras

# Listar Metas
```
GET /api/metas/
Authorization: Bearer {access_token}

Response: 200 OK
[
  {
    "id": 1,
    "nome": "Viagem de Férias",
    "valor_alvo": 1500.00,
    "valor_atual": 450.00,
    "data_alvo": "2024-12-20",
    "ativa": true,
    "conta_nome": "Poupança Meta"
  }
]
```

# Criar Meta
```
POST /api/metas/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "nome": "Comprar Notebook",
  "valor_alvo": 3000.00,
  "conta_vinculada": 2,
  "data_alvo": "2024-06-30"
}

Response: 201 Created
```

# Progresso da Meta
```
GET /api/metas/{id}/progresso/
Authorization: Bearer {access_token}

Response: 200 OK
{
  "nome": "Viagem de Férias",
  "valor_alvo": 1500.00,
  "valor_atual": 450.00,
  "percentual_concluido": 30.0,
  "valor_faltante": 1050.00
}
```

# Depositar em Meta
```
POST /api/metas/{id}/depositar/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "valor": 200.00
}

Response: 200 OK
{
  "message": "Depósito de R$ 200.00 realizado com sucesso"
}
```

---

# Autenticação

# Token JWT

O Controlaê usa **JWT (JSON Web Tokens)** para autenticação segura.

# Fluxo de Autenticação

1. **Registrar**: `POST /api/register/` → Cria novo usuário
2. **Obter Token**: `POST /api/token/` → Retorna access + refresh tokens
3. **Usar Token**: Adicionar header `Authorization: Bearer {access_token}` em requisições
4. **Renovar**: `POST /api/token/refresh/` → Novo access token

# Headers Necessários

```javascript
headers: {
  'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGc...',
  'Content-Type': 'application/json'
}
```

# Permissões

-  **IsAuthenticated**: Requer token válido
-  **IsOwner**: Requer que o recurso pertença ao usuário
-  **AllowAny**: Registro e token sem autenticação

---

# Exemplos de Uso

# JavaScript/Fetch API

```javascript
// 1. Registrar
const register = async () => {
  const response = await fetch('http://localhost:8000/api/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'novo_aluno',
      password: 'senha_segura',
      serie_em: 1
    })
  });
  return response.json();
};

// 2. Obter Token
const getToken = async (username, password) => {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return response.json(); // { access: '...', refresh: '...' }
};

// 3. Listar Transações
const getTransacoes = async (accessToken) => {
  const response = await fetch('http://localhost:8000/api/transacoes/', {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};

// 4. Criar Transação
const createTransacao = async (accessToken, dados) => {
  const response = await fetch('http://localhost:8000/api/transacoes/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(dados)
  });
  return response.json();
};
```

# Python/Requests

```python
import requests

BASE_URL = 'http://localhost:8000/api'

# 1. Registrar
response = requests.post(f'{BASE_URL}/register/', json={
    'username': 'novo_aluno',
    'password': 'senha_segura',
    'serie_em': 1
})

# 2. Obter Token
response = requests.post(f'{BASE_URL}/token/', json={
    'username': 'novo_aluno',
    'password': 'senha_segura'
})
tokens = response.json()
access_token = tokens['access']

# 3. Listar Transações
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get(f'{BASE_URL}/transacoes/', headers=headers)
transacoes = response.json()

# 4. Criar Transação
data = {
    'categoria': 1,
    'conta': 1,
    'tipo': 'saida',
    'descricao': 'Almoço',
    'valor': '25.50',
    'data': '2024-01-20'
}
response = requests.post(f'{BASE_URL}/transacoes/', json=data, headers=headers)
```

---

# Testes

# Executar Todos os Testes

```bash
pytest
```

# Executar Testes com Cobertura

```bash
pytest --cov=core --cov-report=html
```

Relatório de cobertura será gerado em `htmlcov/index.html`

# Executar Teste Específico

```bash
pytest core/tests.py::TestUserRegistration::test_user_registration_success -v
```

# Estrutura de Testes

```
core/tests.py
├── TestUserRegistration (4 testes)
│   ├── Registro bem-sucedido
│   ├── Campos obrigatórios
│   ├── Username duplicado
│   └── Perfil criado automaticamente
├── TestJWTAuthentication (4 testes)
│   ├── Obter token
│   ├── Credenciais inválidas
│   ├── Acesso com token
│   └── Acesso sem token
├── TestCategoriaViewSet (4 testes)
├── TestContaViewSet (3 testes)
├── TestTransacaoViewSet (3 testes)
├── TestMetaFinanceiraViewSet (2 testes)
├── TestServicesTransacciones (2 testes)
└── TestValidacoes (3 testes)
```

**Total: 25 testes**

---

# Banco de Dados

# Migrações

```bash
# Ver status de migrações
python manage.py showmigrations

# Aplicar migrações
python manage.py migrate

# Criar nova migração
python manage.py makemigrations

# Reverter última migração
python manage.py migrate core 0003
```

# Criar Dados de Teste

```bash
python manage.py shell

from django.contrib.auth.models import User
from core.models import Categoria, Conta, Transacao, PerfilAluno
from decimal import Decimal
from datetime import date

# Criar usuário
user = User.objects.create_user(
    username='teste',
    email='teste@example.com',
    password='senha123'
)

# Criar categoria
categoria = Categoria.objects.create(
    usuario=user,
    nome='Alimentação',
    tipo_categoria='saida'
)

# Criar conta
conta = Conta.objects.create(
    usuario=user,
    nome='Conta Corrente',
    saldo_inicial=Decimal('1000.00')
)

# Criar transação
transacao = Transacao.objects.create(
    usuario=user,
    categoria=categoria,
    conta=conta,
    tipo='saida',
    descricao='Almoço',
    valor=Decimal('25.50'),
    data=date.today()
)
```

---

# Segurança

# Boas Práticas Implementadas

 **Variáveis de Ambiente** - Senhas/chaves não no código  
 **JWT Tokens** - Autenticação stateless e escalável  
 **CORS Restrito** - Apenas localhost por padrão  
 **Validação de Dados** - Serializers validam entrada  
 **Isolamento de Dados** - Permissões por usuário  
 **Transações Atômicas** - Integridade em operações críticas  
 **HTTPS Pronto** - Configurável via settings  

# Troubleshooting

# Erro: `ModuleNotFoundError: No module named 'django'`

```bash
# Solução: Ativar virtual environment
# Windows:
venv\Scripts\activate

# Depois instalar:
pip install -r requirements.txt
```

# Erro: `CORS error` no Frontend

```python
# Verificar CORS_ALLOWED_ORIGINS em settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://seu-dominio.com'
]

# Certificar que django-cors-headers está em INSTALLED_APPS
# e CorsMiddleware está no topo de MIDDLEWARE
```

# Erro: `Permissão negada` ao criar recurso

```python
# Verificar se usuario foi atribuído corretamente
# Em views.py, usar:
def perform_create(self, serializer):
    serializer.save(usuario=self.request.user)
```

# Erro: `ProgrammingError: table does not exist`

```bash
# Solução: Rodar migrações
python manage.py migrate
```

# Erro: `UNIQUE constraint failed`

```python
# Verificar validação de unicidade
# Exemplo em serializers.py:
def validate_nome(self, value):
    user = self.context['request'].user
    qs = Categoria.objects.filter(usuario=user, nome__iexact=value)
    if qs.exists():
        raise serializers.ValidationError("Já existe uma categoria com esse nome.")
    return value
```

---

# Suporte e Contribuição

# Reportar Bugs
```
GitHub Issues: https://github.com/seu-usuario/Backend_Controlae/issues
```

### Roadmap Futuro
- [ ] Gráficos de gastos
- [ ] Relatórios PDF
- [ ] Notificações de metas
- [ ] Integração com bancos reais
- [ ] Mobile app nativo
- [ ] Dashboard administrativo

---

# Autor

**Vinícius** - Desenvolvedor Backend  
*Projeto Final - Análise e Desenvolvimento de Sistemas (ADS)*

---

**Última atualização**: 2024-11-17  
**Versão**: 1.0.0  
**Status**: ✅ Production Ready
