/**
 * Configurações da API
 * Ajuste conforme seu ambiente (desenvolvimento, produção, etc)
 */

export const API_CONFIG = {
  /**
   * URL base da API do back-end
   * DESENVOLVIMENTO: http://localhost:3000
   * PRODUÇÃO: https://api.seu-dominio.com
   */
  baseUrl: 'http://localhost:8000/api', // Altere conforme seu ambiente

  /**
   * Endpoints disponíveis
   */
  endpoints: {
    // Endpoints do back-end Django/DRF (conforme `controlae/urls.py`)
    // Observação: a `baseUrl` já inclui o sufixo `/api`
    register: '/register/',
    token: '/token/',
    tokenRefresh: '/token/refresh/',
    perfil: '/usuarios/perfil',
    transacoes: '/transacoes',
    categorias: '/categorias',
    contas: '/contas',
    metas: '/metas',
    lembretes: '/lembretes',
    notificacoes: '/notificacoes',
    incentivosConclusao: '/incentivos/conclusao/',
    incentivosConclusaoLiberar: '/incentivos/conclusao/liberar/',
    incentivosEnem: '/incentivos/enem/',
    relatorioPdf: '/relatorio/pdf/',
    dashboard: '/dashboard/'
  },

  /**
   * Configurações de requisição
   */
  requisicao: {
    timeout: 30000, // 30 segundos
    tentativasErro: 3,
    delayTentativa: 1000 // 1 segundo
  },

  /**
   * Configurações de armazenamento
   */
  armazenamento: {
    tokenKey: 'auth_token',
    refreshTokenKey: 'refresh_token',
    usuarioKey: 'usuario_dados'
  }
};
