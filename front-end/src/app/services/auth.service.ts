import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { RegistroCadastro, RespostaCadastro, ErroAPI } from '../models/usuario';
import { API_CONFIG } from '../config/api.config';

/**
 * Serviço responsável pela autenticação e cadastro de usuários
 * Comunica com a API do back-end
 */
@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Usa a configuração centralizada
  private apiUrl = API_CONFIG.baseUrl;

  // endpoints para fácil uso
  private endpoints = API_CONFIG.endpoints;

  constructor(private http: HttpClient) {}

  /**
   * Realiza o cadastro de um novo usuário
   * @param dados Dados do cadastro contendo nome, email, senha e anoEscolar
   * @returns Observable com a resposta da API
   */
  cadastrarUsuario(dados: RegistroCadastro): Observable<RespostaCadastro> {
    return this.http.post<RespostaCadastro>(`${this.apiUrl}${this.endpoints.register}`, dados).pipe(
      map(resposta => {
        // Se houver um token na resposta, armazena no localStorage
        if (resposta.dados) {
          console.log('Cadastro realizado com sucesso');
        }
        return resposta;
      }),
      catchError(this.tratarErro)
    );
  }

  /**
   * Realiza login usando JWT (obtem access/refresh)
   * @param email
   * @param senha
   */
  login(email: string, senha: string): Observable<any> {
    const payload = { email: email, password: senha };
    return this.http.post<any>(`${this.apiUrl}${this.endpoints.token}`, payload).pipe(
      map(res => {
        // espera-se { access: '...', refresh: '...' }
        if (res?.access) {
          localStorage.setItem(API_CONFIG.armazenamento.tokenKey, res.access);
        }
        if (res?.refresh) {
          localStorage.setItem(API_CONFIG.armazenamento.refreshTokenKey, res.refresh);
        }
        return res;
      }),
      catchError(this.tratarErro)
    );
  }

  /**
   * Renova o access token usando o refresh token
   */
  renovarToken(): Observable<any> {
    const refresh = localStorage.getItem(API_CONFIG.armazenamento.refreshTokenKey);
    if (!refresh) {
      return throwError(() => ({ mensagem: 'Sem refresh token disponível' }));
    }

    return this.http.post<any>(`${this.apiUrl}${this.endpoints.tokenRefresh}`, { refresh }).pipe(
      map(res => {
        if (res?.access) {
          localStorage.setItem(API_CONFIG.armazenamento.tokenKey, res.access);
        }
        return res;
      }),
      catchError(this.tratarErro)
    );
  }

  /**
   * Realiza logout removendo tokens do localStorage
   */
  logout(): void {
    localStorage.removeItem(API_CONFIG.armazenamento.tokenKey);
    localStorage.removeItem(API_CONFIG.armazenamento.refreshTokenKey);
    localStorage.removeItem(API_CONFIG.armazenamento.usuarioKey);
    console.log('Usuário desconectado com sucesso');
  }

  /**
   * Verifica se usuário está autenticado
   */
  estaAutenticado(): boolean {
    return !!localStorage.getItem(API_CONFIG.armazenamento.tokenKey);
  }

  /**
   * Trata erros de requisições HTTP
   * @param erro Erro capturado da requisição
   * @returns Observable com o erro tratado
   */
  private tratarErro(erro: HttpErrorResponse) {
    let erroAPI: ErroAPI;

    if (erro.error instanceof ErrorEvent) {
      // Erro do cliente/rede
      erroAPI = {
        codigo: 'ERRO_CLIENTE',
        mensagem: `Erro de rede: ${erro.error.message}`,
        detalhes: erro.error
      };
    } else {
      // Erro do servidor
      erroAPI = {
        codigo: erro.error?.codigo || 'ERRO_SERVIDOR',
        mensagem: erro.error?.mensagem || `Erro do servidor: ${erro.status} - ${erro.statusText}`,
        detalhes: erro.error
      };
    }

    console.error('Erro na API:', erroAPI);
    return throwError(() => erroAPI);
  }
}
