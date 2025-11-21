# 📱 Guia de Setup para o Frontend - Controla€

## Olá, Developer Frontend! 👋

Este documento te guia pelo setup para consumir a API do Controla€.

---

## 🚀 Pré-requisitos

- Node.js 16+ instalado
- npm ou yarn
- Conhecimento básico de JavaScript/TypeScript
- A API rodando em `http://localhost:8000`

---

## 📋 Começar o Frontend

### 1. URL Base da API

```javascript
const API_URL = 'http://localhost:8000/api';
```

### 2. CORS Já Está Configurado ✅

O backend já permite requisições de:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (Vue)

**Você não precisa fazer nada!** Já pode fazer requisições normalmente.

---

## 🔐 Autenticação JWT

### Fluxo de Autenticação

1. **Usuário se registra**
   ```javascript
   POST /api/register/
   {
     "username": "aluno_teste",
     "password": "senha123",
     "serie_em": 1
   }
   ```

2. **Usuário faz login**
   ```javascript
   POST /api/token/
   {
     "username": "aluno_teste",
     "password": "senha123"
   }
   ```
   
   Resposta:
   ```json
   {
     "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```

3. **Guardar tokens**
   ```javascript
   localStorage.setItem('access_token', data.access);
   localStorage.setItem('refresh_token', data.refresh);
   ```

4. **Usar token em requisições**
   ```javascript
   const token = localStorage.getItem('access_token');
   
   fetch('http://localhost:8000/api/categorias/', {
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     }
   });
   ```

5. **Renovar token quando expirar**
   ```javascript
   POST /api/token/refresh/
   {
     "refresh": "seu_refresh_token"
   }
   ```

---

## 📚 Endpoints Disponíveis

### Autenticação
- `POST /api/register/` - Registrar novo usuário
- `POST /api/token/` - Login
- `POST /api/token/refresh/` - Renovar token

### Categorias
- `GET /api/categorias/` - Listar todas
- `POST /api/categorias/` - Criar nova
- `PATCH /api/categorias/{id}/` - Editar
- `DELETE /api/categorias/{id}/` - Deletar

### Contas
- `GET /api/contas/` - Listar todas
- `POST /api/contas/` - Criar nova
- `PATCH /api/contas/{id}/` - Editar
- `DELETE /api/contas/{id}/` - Deletar
- `POST /api/contas/transferir/` - Transferir entre contas

### Transações
- `GET /api/transacoes/` - Listar todas
- `POST /api/transacoes/` - Criar nova
- `PATCH /api/transacoes/{id}/` - Editar
- `DELETE /api/transacoes/{id}/` - Deletar
- `GET /api/transacoes/resumo_financeiro/` - Ver resumo
- `POST /api/transacoes/confirmar_recebimento/` - Confirmar Pé-de-Meia

### Metas Financeiras
- `GET /api/metas/` - Listar todas
- `POST /api/metas/` - Criar nova
- `PATCH /api/metas/{id}/` - Editar
- `DELETE /api/metas/{id}/` - Deletar
- `GET /api/metas/{id}/progresso/` - Ver progresso
- `POST /api/metas/{id}/depositar/` - Depositar na meta

---

## 💡 Exemplos de Requisições

### Registrar Usuário

```javascript
async function registerUser() {
  const response = await fetch('http://localhost:8000/api/register/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'joao_silva',
      password: 'senha_segura123',
      serie_em: 1  // 1, 2 ou 3
    })
  });
  
  return await response.json();
}
```

### Fazer Login

```javascript
async function login() {
  const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'joao_silva',
      password: 'senha_segura123'
    })
  });
  
  const data = await response.json();
  
  // Guardar tokens
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  
  return data;
}
```

### Listar Categorias

```javascript
async function getCategorias() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/categorias/', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
}
```

### Criar Categoria

```javascript
async function createCategoria(nome, tipo) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/categorias/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      nome: nome,
      tipo_categoria: tipo  // 'entrada' ou 'saida'
    })
  });
  
  return await response.json();
}
```

### Criar Transação

```javascript
async function createTransacao(dados) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/transacoes/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      tipo: 'saida',  // 'entrada' ou 'saida'
      descricao: 'Compra na padaria',
      valor: 25.50,
      data: '2025-11-16',
      categoria: 1,  // ID da categoria
      conta: 1,      // ID da conta
      pago: true,
      parcelas: 1,
      vencimento: null
    })
  });
  
  return await response.json();
}
```

### Transferir Entre Contas

```javascript
async function transferirEntre Contas(conta_origem_id, conta_destino_id, valor) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/contas/transferir/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      conta_origem_id: conta_origem_id,
      conta_destino_id: conta_destino_id,
      valor: valor
    })
  });
  
  return await response.json();
}
```

### Ver Resumo Financeiro

```javascript
async function getResumoFinanceiro(fromDate, toDate) {
  const token = localStorage.getItem('access_token');
  
  let url = 'http://localhost:8000/api/transacoes/resumo_financeiro/';
  
  if (fromDate && toDate) {
    url += `?from_date=${fromDate}&to_date=${toDate}`;
  }
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

### Criar Meta Financeira

```javascript
async function createMeta(nome, valor_alvo, data_alvo) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/metas/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      nome: nome,
      valor_alvo: valor_alvo,
      data_alvo: data_alvo  // pode ser null
    })
  });
  
  return await response.json();
}
```

### Ver Progresso de Meta

```javascript
async function getProgressoMeta(metaId) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/api/metas/${metaId}/progresso/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}
```

---

## 🛠️ Setup com Axios (Recomendado)

Se preferir usar Axios, crie um arquivo `api.js`:

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor para adicionar token automaticamente
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para renovar token se expirar
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://localhost:8000/api/token/refresh/', {
          refresh: refreshToken
        });
        
        localStorage.setItem('access_token', response.data.access);
        api.defaults.headers.common.Authorization = `Bearer ${response.data.access}`;
        
        return api(originalRequest);
      } catch (err) {
        // Redirecionar para login
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

Depois use assim:

```javascript
import api from './api';

// Listar categorias
const categorias = await api.get('/categorias/');

// Criar categoria
await api.post('/categorias/', {
  nome: 'Mesada',
  tipo_categoria: 'entrada'
});

// Editar
await api.patch('/categorias/1/', {
  nome: 'Mesada Semanal'
});

// Deletar
await api.delete('/categorias/1/');
```

---

## ⚠️ Erros Comuns

### 401 Unauthorized
- **Causa:** Token expirado ou não enviado
- **Solução:** Faça login novamente

### 403 Forbidden
- **Causa:** Tentando acessar recurso de outro usuário
- **Solução:** Cada usuário só vê seus dados

### 400 Bad Request
- **Causa:** Dados inválidos
- **Solução:** Verifique o formato dos dados

### 404 Not Found
- **Causa:** Recurso não existe
- **Solução:** Verifique o ID

---

## 🧪 Testando a API

### Com cURL

```bash
# Registrar
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"teste","password":"senha123","serie_em":1}'

# Login
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"teste","password":"senha123"}'

# Listar categorias
curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/api/categorias/
```

### Com Postman

1. Criar um ambiente com variável:
   - `token` = access token do login

2. Usar `{{token}}` em `Authorization: Bearer {{token}}`

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique se a API está rodando: `http://localhost:8000/api/`
2. Confira o status code e mensagem de erro
3. Verifique se o token está no localStorage
4. Contate o Vinicius (backend dev) 😄

---

## ✅ Checklist para Começar

- [ ] API rodando em `http://localhost:8000`
- [ ] Endpoints testados
- [ ] CORS funcionando (sem erros de blocking)
- [ ] Autenticação JWT implementada
- [ ] Tokens sendo guardados no localStorage
- [ ] Requisições com `Authorization: Bearer` sendo enviadas
- [ ] Frontend pronto para consumir!

---

**Boa sorte com o frontend! 🚀**
