import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../config/api.config';

export interface Conta {
  id?: number;
  nome: string;
  saldo_inicial: number;
  saldo_atual?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ContaService {
  private apiUrl = API_CONFIG.baseUrl;
  private endpoint = API_CONFIG.endpoints.contas;

  constructor(private http: HttpClient) {}

  /**
   * Busca todas as contas do usuário autenticado
   */
  listarContas(): Observable<Conta[]> {
    return this.http.get<Conta[]>(`${this.apiUrl}${this.endpoint}`);
  }

  /**
   * Busca uma conta por ID
   */
  obterConta(id: number): Observable<Conta> {
    return this.http.get<Conta>(`${this.apiUrl}${this.endpoint}${id}/`);
  }

  /**
   * Cria uma nova conta
   */
  criarConta(conta: Conta): Observable<Conta> {
    return this.http.post<Conta>(`${this.apiUrl}${this.endpoint}`, conta);
  }

  /**
   * Atualiza uma conta existente
   */
  atualizarConta(id: number, conta: Partial<Conta>): Observable<Conta> {
    return this.http.put<Conta>(`${this.apiUrl}${this.endpoint}${id}/`, conta);
  }

  /**
   * Deleta uma conta
   */
  deletarConta(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${this.endpoint}${id}/`);
  }
}
