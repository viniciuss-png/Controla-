/**
 * Interface que representa os dados de registro de um novo usuário
 */
export interface RegistroCadastro {
  nome: string;
  email: string;
  senha: string;
  anoEscolar: number;
}

/**
 * Interface para a resposta da API após o cadastro
 */
export interface RespostaCadastro {
  sucesso: boolean;
  mensagem: string;
  dados?: {
    id: string;
    nome: string;
    email: string;
    anoEscolar: number;
    dataCriacao: string;
  };
  erro?: string;
}

/**
 * Interface para erros da API
 */
export interface ErroAPI {
  codigo: string;
  mensagem: string;
  detalhes?: any;
}
