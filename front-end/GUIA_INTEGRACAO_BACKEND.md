# Guia de Integração - Back-end

## Resumo

O componente de cadastro do front-end espera um endpoint POST que recebe dados de usuário e retorna uma resposta estruturada.

## Endpoint Obrigatório

### POST `/api/usuarios/cadastro`

**Headers Esperados:**
```
Content-Type: application/json
```

**Corpo da Requisição (RegistroCadastro):**
```json
{
  "nome": "João Silva",
  "email": "joao.silva@email.com",
  "senha": "SenhaForte123",
  "anoEscolar": 1
}
```

**Validações Server-side Recomendadas:**

1. **Email**
   - Deve ser único no banco de dados
   - Validar formato de email
   - Converter para lowercase antes de salvar

2. **Senha**
   - Mínimo 6 caracteres
   - Hash com bcrypt ou argon2 antes de salvar
   - Nunca armazenar em texto plano

3. **Nome**
   - Mínimo 3 caracteres
   - Máximo 255 caracteres
   - Trim whitespace

4. **Ano Escolar**
   - Validar se está entre 1-3
   - Armazenar como integer

**Resposta de Sucesso (200 OK):**
```json
{
  "sucesso": true,
  "mensagem": "Cadastro realizado com sucesso!",
  "dados": {
    "id": "user-id-gerado-uuid",
    "nome": "João Silva",
    "email": "joao.silva@email.com",
    "anoEscolar": 1,
    "dataCriacao": "2025-12-01T10:30:00Z"
  }
}
```

**Resposta de Erro (400 Bad Request):**
```json
{
  "sucesso": false,
  "mensagem": "Email já cadastrado no sistema",
  "codigo": "EMAIL_DUPLICADO",
  "detalhes": {
    "campo": "email",
    "valor": "joao.silva@email.com"
  }
}
```

**Resposta de Erro Servidor (500):**
```json
{
  "sucesso": false,
  "mensagem": "Erro interno ao processar cadastro",
  "codigo": "ERRO_SERVIDOR",
  "detalhes": {}
}
```

## Códigos de Erro Esperados

| Código | Status HTTP | Mensagem |
|--------|-------------|----------|
| EMAIL_DUPLICADO | 400 | Email já cadastrado |
| EMAIL_INVALIDO | 400 | Formato de email inválido |
| SENHA_FRACA | 400 | Senha não atende aos requisitos |
| NOME_INVALIDO | 400 | Nome inválido ou muito curto |
| ANO_ESCOLAR_INVALIDO | 400 | Ano escolar inválido |
| DADOS_INCOMPLETOS | 400 | Faltam campos obrigatórios |
| ERRO_SERVIDOR | 500 | Erro ao processar solicitação |

## Exemplo de Implementação (Node.js/Express)

```typescript
import express from 'express';
import bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';

const router = express.Router();

router.post('/usuarios/cadastro', async (req, res) => {
  try {
    const { nome, email, senha, anoEscolar } = req.body;

    // Validações
    if (!nome || !email || !senha || !anoEscolar) {
      return res.status(400).json({
        sucesso: false,
        mensagem: 'Faltam campos obrigatórios',
        codigo: 'DADOS_INCOMPLETOS'
      });
    }

    // Verificar se email já existe
    const usuarioExistente = await Usuario.findOne({ email: email.toLowerCase() });
    if (usuarioExistente) {
      return res.status(400).json({
        sucesso: false,
        mensagem: 'Email já cadastrado no sistema',
        codigo: 'EMAIL_DUPLICADO',
        detalhes: { campo: 'email', valor: email }
      });
    }

    // Hash da senha
    const senhaHash = await bcrypt.hash(senha, 10);

    // Criar novo usuário
    const novoUsuario = await Usuario.create({
      id: uuidv4(),
      nome: nome.trim(),
      email: email.toLowerCase().trim(),
      senha: senhaHash,
      anoEscolar: parseInt(anoEscolar),
      dataCriacao: new Date().toISOString()
    });

    return res.status(200).json({
      sucesso: true,
      mensagem: 'Cadastro realizado com sucesso!',
      dados: {
        id: novoUsuario.id,
        nome: novoUsuario.nome,
        email: novoUsuario.email,
        anoEscolar: novoUsuario.anoEscolar,
        dataCriacao: novoUsuario.dataCriacao
      }
    });
  } catch (erro) {
    console.error('Erro ao cadastrar usuário:', erro);
    return res.status(500).json({
      sucesso: false,
      mensagem: 'Erro ao processar cadastro',
      codigo: 'ERRO_SERVIDOR',
      detalhes: process.env.NODE_ENV === 'development' ? erro.message : {}
    });
  }
});

export default router;
```

## Exemplo em Python/Flask

```python
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api')

@usuarios_bp.route('/usuarios/cadastro', methods=['POST'])
def cadastro():
    try:
        dados = request.get_json()
        
        # Extrair dados
        nome = dados.get('nome', '').strip()
        email = dados.get('email', '').strip().lower()
        senha = dados.get('senha', '')
        anoEscolar = dados.get('anoEscolar')
        
        # Validações
        if not all([nome, email, senha, anoEscolar]):
            return jsonify({
                'sucesso': False,
                'mensagem': 'Faltam campos obrigatórios',
                'codigo': 'DADOS_INCOMPLETOS'
            }), 400
        
        # Verificar email existente
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return jsonify({
                'sucesso': False,
                'mensagem': 'Email já cadastrado no sistema',
                'codigo': 'EMAIL_DUPLICADO',
                'detalhes': {'campo': 'email', 'valor': email}
            }), 400
        
        # Criar novo usuário
        novo_usuario = Usuario(
            id=str(uuid.uuid4()),
            nome=nome,
            email=email,
            senha=generate_password_hash(senha),
            anoEscolar=int(anoEscolar),
            dataCriacao=datetime.utcnow().isoformat()
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Cadastro realizado com sucesso!',
            'dados': {
                'id': novo_usuario.id,
                'nome': novo_usuario.nome,
                'email': novo_usuario.email,
                'anoEscolar': novo_usuario.anoEscolar,
                'dataCriacao': novo_usuario.dataCriacao
            }
        }), 200
        
    except Exception as e:
        print(f'Erro ao cadastrar usuário: {str(e)}')
        return jsonify({
            'sucesso': False,
            'mensagem': 'Erro ao processar cadastro',
            'codigo': 'ERRO_SERVIDOR',
            'detalhes': {}
        }), 500
```

## Configuração CORS

Se o front-end está em domínio diferente do back-end, configure CORS:

**Express:**
```typescript
import cors from 'cors';

app.use(cors({
  origin: 'http://localhost:4200', // URL do front-end em desenvolvimento
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

**Flask:**
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": "http://localhost:4200",
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Segurança - Checklist

- [ ] Validar TODOS os campos no servidor (nunca confiar apenas no cliente)
- [ ] Hash de senha com algoritmo seguro (bcrypt, argon2)
- [ ] Rate limiting no endpoint de cadastro (prevent brute force)
- [ ] Validar comprimento máximo de campos
- [ ] Sanitizar entradas (XSS prevention)
- [ ] Usar HTTPS em produção
- [ ] CORS bem configurado
- [ ] Logs de tentativas de cadastro falhadas
- [ ] Confirmação de email (recomendado)
- [ ] Proteção contra SQL injection (usar ORM ou prepared statements)

## Testes

Use o `curl` ou Postman para testar:

```bash
curl -X POST http://localhost:3000/api/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "Senha123",
    "anoEscolar": 1
  }'
```

## Status de Produção

Antes de colocar em produção, certifique-se de:

1. ✅ Endpoint implementado e testado
2. ✅ Validações servidor-side completas
3. ✅ Tratamento de erros consistente
4. ✅ Logs adequados
5. ✅ CORS configurado
6. ✅ Rate limiting ativo
7. ✅ HTTPS habilitado
8. ✅ Confirmação de email implementada
9. ✅ Backup automático do banco de dados
10. ✅ Monitoramento de erros ativo
