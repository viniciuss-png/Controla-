import { Injectable } from '@angular/core';

/**
 * Interface para resultado de validação
 */
export interface ResultadoValidacao {
  valido: boolean;
  erro?: string;
}

/**
 * Serviço responsável pelas validações de formulário
 */
@Injectable({
  providedIn: 'root'
})
export class ValidacaoService {

  /**
   * Valida um email
   * @param email Email a ser validado
   * @returns Resultado da validação
   */
  validarEmail(email: string): ResultadoValidacao {
    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!email) {
      return {
        valido: false,
        erro: 'Email é obrigatório'
      };
    }

    if (!regexEmail.test(email)) {
      return {
        valido: false,
        erro: 'Email inválido'
      };
    }

    return { valido: true };
  }

  /**
   * Valida o nome
   * @param nome Nome a ser validado
   * @returns Resultado da validação
   */
  validarNome(nome: string): ResultadoValidacao {
    if (!nome) {
      return {
        valido: false,
        erro: 'Nome é obrigatório'
      };
    }

    if (nome.trim().length < 3) {
      return {
        valido: false,
        erro: 'Nome deve ter no mínimo 3 caracteres'
      };
    }

    if (!/^[a-záàâãéèêíïóôõöúçñ\s]+$/i.test(nome)) {
      return {
        valido: false,
        erro: 'Nome deve conter apenas letras e espaços'
      };
    }

    return { valido: true };
  }

  /**
   * Valida a senha
   * @param senha Senha a ser validada
   * @returns Resultado da validação
   */
  validarSenha(senha: string): ResultadoValidacao {
    if (!senha) {
      return {
        valido: false,
        erro: 'Senha é obrigatória'
      };
    }

    if (senha.length < 6) {
      return {
        valido: false,
        erro: 'Senha deve ter no mínimo 6 caracteres'
      };
    }

    // Verifica se tem pelo menos uma letra maiúscula, uma minúscula e um número
    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{6,}$/.test(senha)) {
      return {
        valido: false,
        erro: 'Senha deve conter maiúscula, minúscula e número'
      };
    }

    return { valido: true };
  }

  /**
   * Valida se as senhas conferem
   * @param senha Senha
   * @param confirmarSenha Confirmação da senha
   * @returns Resultado da validação
   */
  validarConfirmacaoSenha(senha: string, confirmarSenha: string): ResultadoValidacao {
    if (senha !== confirmarSenha) {
      return {
        valido: false,
        erro: 'As senhas não conferem'
      };
    }

    return { valido: true };
  }

  /**
   * Valida o ano escolar
   * @param ano Ano escolar
   * @returns Resultado da validação
   */
  validarAnoEscolar(ano: number): ResultadoValidacao {
    if (!ano || ![1, 2, 3].includes(ano)) {
      return {
        valido: false,
        erro: 'Selecione um ano escolar válido'
      };
    }

    return { valido: true };
  }
}
