# Documentação da Estrutura de Cadastro

## Visão Geral

A estrutura foi criada seguindo os padrões do Angular 21 para envio seguro e validado de dados de cadastro para a API do back-end.

## Arquivos Criados

### 1. **Models** (`src/app/models/usuario.ts`)
Define as interfaces TypeScript para tipagem dos dados:

- `RegistroCadastro`: Dados que são enviados para o back-end
- `RespostaCadastro`: Formato esperado da resposta da API
- `ErroAPI`: Estrutura de erro padronizado

### 2. **Services**

#### 2.1 **AuthService** (`src/app/services/auth.service.ts`)
Responsável pela comunicação com a API:

- `cadastrarUsuario(dados: RegistroCadastro)`: Envia dados de cadastro
- Tratamento centralizado de erros HTTP
- Integração com localStorage para tokens

**Uso:**
```typescript
this.authService.cadastrarUsuario(dados).subscribe({
  next: (resposta) => { /* Sucesso */ },
  error: (erro) => { /* Erro */ }
});
```

#### 2.2 **ValidacaoService** (`src/app/services/validacao.service.ts`)
Validações de campos do formulário:

- `validarEmail()`: Valida formato de email
- `validarNome()`: Valida nome (3+ caracteres, apenas letras)
- `validarSenha()`: Valida força da senha
- `validarConfirmacaoSenha()`: Verifica se senhas conferem
- `validarAnoEscolar()`: Valida ano escolar selecionado

**Usa o padrão `ResultadoValidacao`:**
```typescript
{
  valido: boolean;
  erro?: string; // Mensagem de erro se inválido
}
```

### 3. **Interceptor** (`src/app/interceptors/http-config.interceptor.ts`)
Middleware para todas as requisições HTTP:

- Adiciona `Content-Type: application/json`
- Injeta token de autenticação automaticamente
- Trata erros globalmente (401, 403, 5xx)

### 4. **Componente Atualizado** (`src/app/cadastrar/cadastrar.component.ts`)
Componente standalone com:

- Formulário reativo com `FormBuilder`
- Validações em tempo real
- Comunicação com `AuthService`
- Gerenciamento de estado (enviando, erros, sucesso)
- Limpeza de memory leaks com `takeUntil`

### 5. **Template Atualizado** (`src/app/cadastrar/cadastrar.component.html`)
Interface com:

- Binding reativo do formulário
- Exibição dinâmica de erros de validação
- Mensagens de sucesso e erro
- Estado do botão (desabilitado durante envio)

### 6. **Estilos Aprimorados** (`src/app/cadastrar/cadastrar.component.css`)
Adicionados estilos para:

- Campos com erro (borda vermelha, fundo rosa)
- Mensagens de validação em tempo real
- Alertas de sucesso (verde) e erro (vermelho)
- Animações suaves

### 7. **Configuração** (`src/app/config/api.config.ts`)
Centraliza configurações:

- URL base da API
- Endpoints disponíveis
- Timeouts e tentativas de erro
- Chaves de localStorage

## Fluxo de Dados

```
Usuário preenche formulário
         ↓
Validação em tempo real (ValidacaoService)
         ↓
Usuário clica em "Enviar"
         ↓
Validação final do formulário (FormBuilder)
         ↓
Requisição HTTP POST (AuthService)
         ↓
Interceptor adiciona headers e token
         ↓
Back-end processa cadastro
         ↓
Resposta recebida
         ↓
Se sucesso: Mensagem + Redirecionamento para login
Se erro: Mensagem de erro exibida
```

## Dados Enviados para o Back-end

```json
POST /api/usuarios/cadastro
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "Senha123",
  "anoEscolar": 1
}
```

## Resposta Esperada do Back-end

**Sucesso (200):**
```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso!",
  "dados": {
    "id": "user-id-123",
    "nome": "João Silva",
    "email": "joao@email.com",
    "anoEscolar": 1,
    "dataCriacao": "2025-12-01T10:30:00Z"
  }
}
```

**Erro (400/500):**
```json
{
  "sucesso": false,
  "mensagem": "Email já cadastrado",
  "codigo": "EMAIL_DUPLICADO",
  "detalhes": {...}
}
```

## Configuração Necessária

### 1. Atualizar o `app.config.ts`
Adicionar `HttpClientModule` ao array de providers:

```typescript
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpConfigInterceptor } from './interceptors/http-config.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    // ... outros providers
    HttpClientModule,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: HttpConfigInterceptor,
      multi: true
    }
  ]
};
```

### 2. Variáveis de Ambiente
Criar arquivo `.env` (ou ajustar `environment.ts`):

```
NG_APP_API_URL=http://localhost:3000/api
```

### 3. Importe necessários no Componente

O componente já importa:
- `ReactiveFormsModule` para formulário reativo
- `CommonModule` para diretivas como `*ngIf`
- `RouterModule` para navegação

## Requisitos do Back-end

A API deve ter o endpoint:

```
POST /api/usuarios/cadastro
```

Que valida:
- Email único
- Senha com força mínima
- Nome válido
- Ano escolar entre 1-3

## Boas Práticas Implementadas

✅ **Tipagem forte** com TypeScript
✅ **Validação client-side** com reatividade
✅ **Tratamento de erros** centralizado
✅ **Limpeza de recursos** (OnDestroy)
✅ **Formulário reativo** (não template-driven)
✅ **Separação de responsabilidades** (Services)
✅ **Componente standalone**
✅ **Interceptor HTTP** para middleware
✅ **Mensagens de feedback** ao usuário
✅ **Estado de carregamento** durante requisição

## Próximos Passos

1. **Implementar no back-end** o endpoint `/api/usuarios/cadastro`
2. **Configurar CORS** se front e back estão em domínios diferentes
3. **Testar** o fluxo completo
4. **Adicionar** testes unitários com Jasmine/Vitest
5. **Implementar** confirmação de email (opcional)
6. **Adicionar** rate limiting para evitar spam
