# Exemplos de Payload - Testes da API

## ✅ Requests Válidas (Devem retornar sucesso)

### Exemplo 1: Cadastro Simples
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "SenhaForte123",
    "anoEscolar": 1
  }'
```

### Exemplo 2: Cadastro - Segundo Ano
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Santos",
    "email": "maria.santos@email.com",
    "senha": "Abc123def",
    "anoEscolar": 2
  }'
```

### Exemplo 3: Cadastro - Terceiro Ano
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Pedro Oliveira Costa",
    "email": "pedro.oliveira@email.com",
    "senha": "TesteSenha123",
    "anoEscolar": 3
  }'
```

### Exemplo 4: Cadastro - Email com Números
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Ana Ferreira",
    "email": "ana2005@gmail.com",
    "senha": "MinhaSenh@123",
    "anoEscolar": 1
  }'
```

## ❌ Requests Inválidas (Devem retornar erro 400)

### Erro 1: Email Duplicado
```bash
# Depois de cadastrar joao@example.com acima, tenta novamente
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva Outro",
    "email": "joao@example.com",
    "senha": "OutraSenha123",
    "anoEscolar": 2
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Email já cadastrado no sistema",
  "codigo": "EMAIL_DUPLICADO",
  "detalhes": {
    "campo": "email",
    "valor": "joao@example.com"
  }
}
```

### Erro 2: Email Inválido
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste Nome",
    "email": "email-invalido",
    "senha": "SenhaValida123",
    "anoEscolar": 1
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Formato de email inválido",
  "codigo": "EMAIL_INVALIDO",
  "detalhes": {
    "campo": "email",
    "valor": "email-invalido"
  }
}
```

### Erro 3: Senha Fraca (Sem Maiúscula)
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste Nome",
    "email": "teste@example.com",
    "senha": "senhafraca123",
    "anoEscolar": 1
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Senha não atende aos requisitos. Deve conter maiúscula, minúscula e número",
  "codigo": "SENHA_FRACA",
  "detalhes": {
    "campo": "senha",
    "requisitos": [
      "Mínimo 6 caracteres",
      "Pelo menos 1 letra maiúscula",
      "Pelo menos 1 letra minúscula",
      "Pelo menos 1 número"
    ]
  }
}
```

### Erro 4: Senha Muito Curta
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste Nome",
    "email": "teste@example.com",
    "senha": "Ab1",
    "anoEscolar": 1
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Senha deve ter no mínimo 6 caracteres",
  "codigo": "SENHA_FRACA",
  "detalhes": {
    "campo": "senha",
    "minimo": 6,
    "fornecido": 3
  }
}
```

### Erro 5: Nome Muito Curto
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Jo",
    "email": "teste@example.com",
    "senha": "SenhaValida123",
    "anoEscolar": 1
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Nome deve ter no mínimo 3 caracteres",
  "codigo": "NOME_INVALIDO",
  "detalhes": {
    "campo": "nome",
    "minimo": 3,
    "fornecido": 2
  }
}
```

### Erro 6: Nome com Números
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva 123",
    "email": "teste@example.com",
    "senha": "SenhaValida123",
    "anoEscolar": 1
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Nome deve conter apenas letras e espaços",
  "codigo": "NOME_INVALIDO"
}
```

### Erro 7: Ano Escolar Inválido
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste Nome",
    "email": "teste@example.com",
    "senha": "SenhaValida123",
    "anoEscolar": 4
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Ano escolar inválido. Deve ser 1, 2 ou 3",
  "codigo": "ANO_ESCOLAR_INVALIDO",
  "detalhes": {
    "campo": "anoEscolar",
    "valoresAceitos": [1, 2, 3],
    "fornecido": 4
  }
}
```

### Erro 8: Campos Faltando
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste Nome",
    "email": "teste@example.com"
  }'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Faltam campos obrigatórios",
  "codigo": "DADOS_INCOMPLETOS",
  "detalhes": {
    "camposFaltando": ["senha", "anoEscolar"]
  }
}
```

### Erro 9: Payload Vazio
```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Resposta esperada:**
```json
{
  "sucesso": false,
  "mensagem": "Faltam campos obrigatórios",
  "codigo": "DADOS_INCOMPLETOS",
  "detalhes": {
    "camposFaltando": ["nome", "email", "senha", "anoEscolar"]
  }
}
```

## 🟢 Response de Sucesso (200 OK)

```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso!",
  "dados": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nome": "João Silva",
    "email": "joao@example.com",
    "anoEscolar": 1,
    "dataCriacao": "2025-12-01T21:30:00.000Z"
  }
}
```

## 🔴 Response de Erro 500

```json
{
  "sucesso": false,
  "mensagem": "Erro ao processar cadastro",
  "codigo": "ERRO_SERVIDOR",
  "detalhes": {}
}
```

## 🧪 Teste com Postman/Insomnia

### 1. Configurar Ambiente
```json
{
  "name": "Controlaê Dev",
  "values": [
    {
      "key": "api_url",
      "value": "http://localhost:3000"
    },
    {
      "key": "email_teste",
      "value": "teste-{{$timestamp}}@example.com"
    }
  ]
}
```

### 2. Request com Variável
```
POST {{api_url}}/api/usuarios/cadastro
Content-Type: application/json

{
  "nome": "Teste {{$timestamp}}",
  "email": "{{email_teste}}",
  "senha": "SenhaTest123",
  "anoEscolar": 1
}
```

## 📊 Matriz de Testes

| Campo | Válido | Inválido |
|-------|--------|----------|
| **Nome** | "João Silva" | "Jo", "João123", "João@Silva" |
| **Email** | "joao@example.com" | "joao", "joao@", "@example.com", "joao@example" |
| **Senha** | "SenhaTest123" | "senha", "SENHA", "123456", "Abc1" |
| **Ano** | 1, 2, 3 | 0, 4, 5, null, undefined |

## 🚀 Teste de Carga (Apache Bench)

```bash
# Instalar Apache Bench (se não tiver)
# Windows: choco install apache-server
# Linux: sudo apt-get install apache2-utils

# Teste com 100 requests, 10 concorrentes
ab -n 100 -c 10 \
  -H "Content-Type: application/json" \
  -p payload.json \
  http://localhost:3000/api/usuarios/cadastro
```

**payload.json:**
```json
{
  "nome": "Teste",
  "email": "teste@example.com",
  "senha": "SenhaTest123",
  "anoEscolar": 1
}
```

---

**Dica:** Use timestamps nos emails para testar múltiplas vezes sem conflito de duplicidade.
