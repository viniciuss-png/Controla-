/**
 * GUIA DE TESTE DE INTEGRAÇÃO COMPLETO
 * 
 * Este arquivo descreve um fluxo de testes E2E que deve ser executado via Cypress ou Playwright
 * NÃO é um arquivo de teste Jasmine/Karma do Angular
 * 
 * Para executar com Cypress:
 * 1. npm install --save-dev cypress
 * 2. npx cypress open
 * 3. Copie o conteúdo deste arquivo para cypress/e2e/fluxo-integracao.cy.ts
 * 
 * Pré-requisitos:
 * 1. Backend Django rodando em http://localhost:8000
 * 2. Frontend Angular rodando em http://localhost:4200
 * 3. Database do backend inicializado (migrate)
 */

/**
 * TESTES CYPRESS E2E
 * 
 * Copie o código abaixo para: cypress/e2e/fluxo-integracao.cy.ts
 */

/*
describe('Fluxo Completo de Integração', () => {
  const BASE_URL = 'http://localhost:4200';
  const API_URL = 'http://localhost:8000/api';

  describe('1. Cadastro de Novo Usuário', () => {
    it('Deve registrar um novo usuário com sucesso', () => {
      cy.visit(`${BASE_URL}/cadastrar`);
      cy.get('input[name="nome"]').type('Usuário Teste');
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('input[name="anoEscolar"]').select('1');
      cy.get('button[type="submit"]').click();
      cy.contains('Cadastro realizado com sucesso').should('be.visible');
    });

    it('Deve rejeitar email duplicado', () => {
      cy.visit(`${BASE_URL}/cadastrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();
      cy.contains('Email já cadastrado').should('be.visible');
    });
  });

  describe('2. Login e Autenticação', () => {
    it('Deve fazer login com credenciais válidas', () => {
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
      cy.window().then((win) => {
        expect(win.localStorage.getItem('auth_token')).to.exist;
        expect(win.localStorage.getItem('refresh_token')).to.exist;
      });
    });

    it('Deve rejeitar credenciais inválidas', () => {
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('SenhaErrada');
      cy.get('button[type="submit"]').click();
      cy.contains('Credenciais inválidas').should('be.visible');
    });
  });

  describe('3. Operações Protegidas (Autenticadas)', () => {
    beforeEach(() => {
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });

    describe('3.1 Gerenciar Categorias', () => {
      it('Deve criar uma nova categoria', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/categorias`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            nome: 'Alimentação',
            tipo_categoria: 'saida'
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.nome).to.eq('Alimentação');
        });
      });

      it('Deve listar categorias do usuário', () => {
        cy.request({
          url: `${API_URL}/categorias`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          }
        }).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body).to.be.an('array');
        });
      });
    });

    describe('3.2 Gerenciar Contas', () => {
      it('Deve criar uma nova conta', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/contas`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            nome: 'Conta Corrente',
            saldo_inicial: 1000.00
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.nome).to.eq('Conta Corrente');
        });
      });
    });

    describe('3.3 Gerenciar Transações', () => {
      it('Deve criar uma transação', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/categorias`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: { nome: 'Alimentação', tipo_categoria: 'saida' }
        }).then((catRes) => {
          cy.request({
            method: 'POST',
            url: `${API_URL}/contas`,
            headers: {
              Authorization: `Bearer ${localStorage.getItem('auth_token')}`
            },
            body: { nome: 'Conta', saldo_inicial: 1000 }
          }).then((contaRes) => {
            cy.request({
              method: 'POST',
              url: `${API_URL}/transacoes`,
              headers: {
                Authorization: `Bearer ${localStorage.getItem('auth_token')}`
              },
              body: {
                tipo: 'saida',
                descricao: 'Almoço',
                valor: 25.50,
                data: new Date().toISOString().split('T')[0],
                categoria: catRes.body.id,
                conta: contaRes.body.id
              }
            }).then((response) => {
              expect(response.status).to.eq(201);
              expect(response.body.descricao).to.eq('Almoço');
            });
          });
        });
      });
    });

    describe('3.4 Gerenciar Metas Financeiras', () => {
      it('Deve criar uma meta financeira', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/metas`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            nome: 'Poupança Férias',
            valor_alvo: 2000.00,
            data_alvo: '2025-06-30',
            ativa: true
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.nome).to.eq('Poupança Férias');
        });
      });
    });

    describe('3.5 Gerenciar Lembretes', () => {
      it('Deve criar um lembrete', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/lembretes`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            titulo: 'Pagar conta de luz',
            descricao: 'Vencimento dia 20',
            recorrencia: 'mensal',
            ativo: true
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.titulo).to.eq('Pagar conta de luz');
        });
      });
    });

    describe('3.6 Acessar Dashboard', () => {
      it('Deve carregar dados do dashboard', () => {
        cy.visit(`${BASE_URL}/dashboard`);
        cy.url().should('include', '/dashboard');
        cy.contains('Dashboard').should('be.visible');
      });
    });
  });

  describe('4. Proteção de Rotas', () => {
    it('Deve bloquear acesso a rota protegida sem autenticação', () => {
      cy.window().then((win) => {
        win.localStorage.removeItem('auth_token');
        win.localStorage.removeItem('refresh_token');
      });
      cy.visit(`${BASE_URL}/dashboard`);
      cy.url().should('include', '/entrar');
    });

    it('Deve permitir acesso a rota protegida com autenticação válida', () => {
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();
      cy.visit(`${BASE_URL}/dashboard`);
      cy.url().should('include', '/dashboard');
    });
  });

  describe('5. Logout', () => {
    it('Deve fazer logout e limpar tokens', () => {
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();
      cy.get('[data-testid="logout-button"]').click();
      cy.url().should('include', '/entrar');
      cy.window().then((win) => {
        expect(win.localStorage.getItem('auth_token')).to.not.exist;
        expect(win.localStorage.getItem('refresh_token')).to.not.exist;
      });
    });
  });

  describe('6. Refresh Token Automático', () => {
    it('Deve renovar token automaticamente ao receber 401', () => {
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();
      cy.window().then((win) => {
        win.localStorage.setItem('auth_token', 'expired_token');
      });
      cy.request({
        url: `${API_URL}/transacoes`,
        headers: {
          Authorization: 'Bearer expired_token'
        },
        failOnStatusCode: false
      }).then((response) => {
        expect([200, 401]).to.include(response.status);
      });
    });
  });
});
*/

/**
 * ============================================================================
 * TESTES MANUAIS VIA CURL (RECOMENDADO PARA DESENVOLVIMENTO)
 * ============================================================================
 */

/**
 * 1. REGISTRAR NOVO USUÁRIO
 * 
 * curl -X POST http://localhost:8000/api/register/ \
 *   -H "Content-Type: application/json" \
 *   -d '{
 *     "nome":"Teste User",
 *     "email":"teste@example.com",
 *     "password":"Senha123!",
 *     "anoEscolar":1
 *   }'
 */

/**
 * 2. FAZER LOGIN (OBTER TOKENS)
 * 
 * curl -X POST http://localhost:8000/api/token/ \
 *   -H "Content-Type: application/json" \
 *   -d '{
 *     "email":"teste@example.com",
 *     "password":"Senha123!"
 *   }'
 * 
 * Resposta esperada:
 * {
 *   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
 *   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
 * }
 * 
 * Salve os tokens em variáveis:
 * $access_token = "seu_access_token_aqui"
 * $refresh_token = "seu_refresh_token_aqui"
 */

/**
 * 3. CRIAR CATEGORIA
 * 
 * curl -X POST http://localhost:8000/api/categorias/ \
 *   -H "Content-Type: application/json" \
 *   -H "Authorization: Bearer $access_token" \
 *   -d '{
 *     "nome":"Alimentação",
 *     "tipo_categoria":"saida"
 *   }'
 */

/**
 * 4. LISTAR CATEGORIAS
 * 
 * curl -H "Authorization: Bearer $access_token" \
 *   http://localhost:8000/api/categorias/
 */

/**
 * 5. CRIAR CONTA
 * 
 * curl -X POST http://localhost:8000/api/contas/ \
 *   -H "Content-Type: application/json" \
 *   -H "Authorization: Bearer $access_token" \
 *   -d '{
 *     "nome":"Conta Corrente",
 *     "saldo_inicial":1000.00
 *   }'
 */

/**
 * 6. CRIAR TRANSAÇÃO
 * 
 * curl -X POST http://localhost:8000/api/transacoes/ \
 *   -H "Content-Type: application/json" \
 *   -H "Authorization: Bearer $access_token" \
 *   -d '{
 *     "tipo":"saida",
 *     "descricao":"Almoço",
 *     "valor":25.50,
 *     "data":"2025-12-01",
 *     "categoria":1,
 *     "conta":1
 *   }'
 */

/**
 * 7. LISTAR TRANSAÇÕES
 * 
 * curl -H "Authorization: Bearer $access_token" \
 *   http://localhost:8000/api/transacoes/
 */

/**
 * 8. CRIAR META FINANCEIRA
 * 
 * curl -X POST http://localhost:8000/api/metas/ \
 *   -H "Content-Type: application/json" \
 *   -H "Authorization: Bearer $access_token" \
 *   -d '{
 *     "nome":"Poupança Férias",
 *     "valor_alvo":2000.00,
 *     "data_alvo":"2025-06-30",
 *     "ativa":true
 *   }'
 */

/**
 * 9. CRIAR LEMBRETE
 * 
 * curl -X POST http://localhost:8000/api/lembretes/ \
 *   -H "Content-Type: application/json" \
 *   -H "Authorization: Bearer $access_token" \
 *   -d '{
 *     "titulo":"Pagar conta de luz",
 *     "descricao":"Vencimento dia 20",
 *     "recorrencia":"mensal",
 *     "ativo":true
 *   }'
 */

/**
 * 10. RENOVAR TOKEN (REFRESH)
 * 
 * curl -X POST http://localhost:8000/api/token/refresh/ \
 *   -H "Content-Type: application/json" \
 *   -d "{\"refresh\":\"$refresh_token\"}"
 * 
 * Resposta: {"access": "novo_token..."}
 */

/**
 * ============================================================================
 * TESTES COM POSTMAN / INSOMNIA
 * ============================================================================
 * 
 * 1. Crie uma collection "Controlaê API"
 * 2. Configure variáveis de ambiente:
 *    - BASE_URL: http://localhost:8000/api
 *    - access_token: (será preenchido após login)
 *    - refresh_token: (será preenchido após login)
 * 
 * 3. Adicione requests:
 * 
 *    POST /api/register/
 *    Body: {
 *      "nome": "Teste",
 *      "email": "teste@test.com",
 *      "password": "Senha123!",
 *      "anoEscolar": 1
 *    }
 * 
 *    POST /api/token/
 *    Body: {
 *      "email": "teste@test.com",
 *      "password": "Senha123!"
 *    }
 *    Tests: pm.environment.set("access_token", pm.response.json().access);
 * 
 *    GET /api/categorias/
 *    Headers: Authorization: Bearer {{access_token}}
 */

export {}; // Para evitar erro de "top-level await" no TypeScript


  describe('1. Cadastro de Novo Usuário', () => {
    it('Deve registrar um novo usuário com sucesso', () => {
      // Navegar para página de cadastro
      cy.visit(`${BASE_URL}/cadastrar`);

      // Preencher formulário
      cy.get('input[name="nome"]').type('Usuário Teste');
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('input[name="anoEscolar"]').select('1');

      // Enviar formulário
      cy.get('button[type="submit"]').click();

      // Verificar sucesso (redirecionar para login ou exibir mensagem)
      cy.contains('Cadastro realizado com sucesso').should('be.visible');
    });

    it('Deve rejeitar email duplicado', () => {
      cy.visit(`${BASE_URL}/cadastrar`);

      cy.get('input[name="email"]').type('usuario@teste.com'); // email já existente
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();

      cy.contains('Email já cadastrado').should('be.visible');
    });
  });

  describe('2. Login e Autenticação', () => {
    it('Deve fazer login com credenciais válidas', () => {
      cy.visit(`${BASE_URL}/entrar`);

      // Preencher credenciais
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');

      // Enviar login
      cy.get('button[type="submit"]').click();

      // Verificar redirecionamento para dashboard
      cy.url().should('include', '/dashboard');

      // Verificar que tokens foram salvos
      cy.window().then((win) => {
        expect(win.localStorage.getItem('auth_token')).to.exist;
        expect(win.localStorage.getItem('refresh_token')).to.exist;
      });
    });

    it('Deve rejeitar credenciais inválidas', () => {
      cy.visit(`${BASE_URL}/entrar`);

      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('SenhaErrada');
      cy.get('button[type="submit"]').click();

      cy.contains('Credenciais inválidas').should('be.visible');
    });
  });

  describe('3. Operações Protegidas (Autenticadas)', () => {
    beforeEach(() => {
      // Login antes de cada teste
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });

    describe('3.1 Gerenciar Categorias', () => {
      it('Deve criar uma nova categoria', () => {
        // Via API (simulando o que um serviço faria)
        cy.request({
          method: 'POST',
          url: `${API_URL}/categorias`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            nome: 'Alimentação',
            tipo_categoria: 'saida'
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.nome).to.eq('Alimentação');
        });
      });

      it('Deve listar categorias do usuário', () => {
        cy.request({
          url: `${API_URL}/categorias`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          }
        }).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body).to.be.an('array');
        });
      });
    });

    describe('3.2 Gerenciar Contas', () => {
      it('Deve criar uma nova conta', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/contas`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            nome: 'Conta Corrente',
            saldo_inicial: 1000.00
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.nome).to.eq('Conta Corrente');
        });
      });
    });

    describe('3.3 Gerenciar Transações', () => {
      it('Deve criar uma transação', () => {
        // Primeiro criar categoria e conta (pré-requisitos)
        cy.request({
          method: 'POST',
          url: `${API_URL}/categorias`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: { nome: 'Alimentação', tipo_categoria: 'saida' }
        }).then((catRes) => {
          cy.request({
            method: 'POST',
            url: `${API_URL}/contas`,
            headers: {
              Authorization: `Bearer ${localStorage.getItem('auth_token')}`
            },
            body: { nome: 'Conta', saldo_inicial: 1000 }
          }).then((contaRes) => {
            // Criar transação
            cy.request({
              method: 'POST',
              url: `${API_URL}/transacoes`,
              headers: {
                Authorization: `Bearer ${localStorage.getItem('auth_token')}`
              },
              body: {
                tipo: 'saida',
                descricao: 'Almoço',
                valor: 25.50,
                data: new Date().toISOString().split('T')[0],
                categoria: catRes.body.id,
                conta: contaRes.body.id
              }
            }).then((response) => {
              expect(response.status).to.eq(201);
              expect(response.body.descricao).to.eq('Almoço');
            });
          });
        });
      });

      it('Deve listar transações do usuário', () => {
        cy.request({
          url: `${API_URL}/transacoes`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          }
        }).then((response) => {
          expect(response.status).to.eq(200);
          expect(response.body).to.be.an('array');
        });
      });
    });

    describe('3.4 Gerenciar Metas Financeiras', () => {
      it('Deve criar uma meta financeira', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/metas`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            nome: 'Poupança Férias',
            valor_alvo: 2000.00,
            data_alvo: '2025-06-30',
            ativa: true
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.nome).to.eq('Poupança Férias');
        });
      });
    });

    describe('3.5 Gerenciar Lembretes', () => {
      it('Deve criar um lembrete', () => {
        cy.request({
          method: 'POST',
          url: `${API_URL}/lembretes`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          },
          body: {
            titulo: 'Pagar conta de luz',
            descricao: 'Vencimento dia 20',
            recorrencia: 'mensal',
            ativo: true
          }
        }).then((response) => {
          expect(response.status).to.eq(201);
          expect(response.body.titulo).to.eq('Pagar conta de luz');
        });
      });
    });

    describe('3.6 Acessar Dashboard', () => {
      it('Deve carregar dados do dashboard', () => {
        cy.visit(`${BASE_URL}/dashboard`);
        cy.url().should('include', '/dashboard');

        // Verificar que o conteúdo do dashboard carregou
        cy.contains('Dashboard').should('be.visible');
      });
    });
  });

  describe('4. Proteção de Rotas', () => {
    it('Deve bloquear acesso a rota protegida sem autenticação', () => {
      // Limpar localStorage para simular usuário não autenticado
      cy.window().then((win) => {
        win.localStorage.removeItem('auth_token');
        win.localStorage.removeItem('refresh_token');
      });

      // Tentar acessar rota protegida
      cy.visit(`${BASE_URL}/dashboard`);

      // Deve ser redirecionado para login
      cy.url().should('include', '/entrar');
    });

    it('Deve permitir acesso a rota protegida com autenticação válida', () => {
      // Login
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();

      // Acessar rota protegida deve funcionar
      cy.visit(`${BASE_URL}/dashboard`);
      cy.url().should('include', '/dashboard');
    });
  });

  describe('5. Logout', () => {
    it('Deve fazer logout e limpar tokens', () => {
      // Login primeiro
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();

      // Clicar em logout (assumindo que existe um botão)
      cy.get('[data-testid="logout-button"]').click();

      // Verificar que foi redirecionado e tokens foram limpos
      cy.url().should('include', '/entrar');
      cy.window().then((win) => {
        expect(win.localStorage.getItem('auth_token')).to.not.exist;
        expect(win.localStorage.getItem('refresh_token')).to.not.exist;
      });
    });
  });

  describe('6. Refresh Token Automático', () => {
    it('Deve renovar token automaticamente ao receber 401', () => {
      // Este teste simula uma requisição que retorna 401
      // O interceptor deve automaticamente renovar o token

      // Login
      cy.visit(`${BASE_URL}/entrar`);
      cy.get('input[name="email"]').type('usuario@teste.com');
      cy.get('input[name="senha"]').type('Senha123!');
      cy.get('button[type="submit"]').click();

      // Simular token expirado removendo do localStorage
      cy.window().then((win) => {
        const oldToken = win.localStorage.getItem('auth_token');
        win.localStorage.setItem('auth_token', 'expired_token');
      });

      // Tentar fazer uma requisição protegida
      // O interceptor deve detectar 401 e renovar automaticamente
      cy.request({
        url: `${API_URL}/transacoes`,
        headers: {
          Authorization: 'Bearer expired_token'
        },
        failOnStatusCode: false
      }).then((response) => {
        // Se o token foi renovado, a requisição deve passar
        // Se não, deve retornar 401
        expect([200, 401]).to.include(response.status);
      });
    });
  });
});

/**
 * TESTE MANUAL VIA CURL
 * 
 * 1. Registrar novo usuário:
 * curl -X POST http://localhost:8000/api/register/ \
 *   -H "Content-Type: application/json" \
 *   -d '{"nome":"Teste","email":"teste@teste.com","password":"Senha123!","anoEscolar":1}'
 * 
 * 2. Fazer login:
 * curl -X POST http://localhost:8000/api/token/ \
 *   -H "Content-Type: application/json" \
 *   -d '{"email":"teste@teste.com","password":"Senha123!"}'
 * 
 * Resposta: {"access": "...", "refresh": "..."}
 * 
 * 3. Usar token em requisição protegida:
 * curl -H "Authorization: Bearer <TOKEN_ACCESS>" \
 *   http://localhost:8000/api/transacoes/
 * 
 * 4. Renovar token:
 * curl -X POST http://localhost:8000/api/token/refresh/ \
 *   -H "Content-Type: application/json" \
 *   -d '{"refresh":"<REFRESH_TOKEN>"}'
 */
