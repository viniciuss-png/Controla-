import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../config/api.config';

export interface Transacao {
  id?: number;
  tipo: 'entrada' | 'saida';
  descricao: string;
  valor: number;
  data: string;
  parcelas?: number;
  vencimento?: string;
  pago?: boolean;
  categoria: number;
  conta: number;
  categoria_nome?: string;
  conta_nome?: string;
  tipo_categoria?: string;
}

@Injectable({
  providedIn: 'root'
})
export class TransacaoService {
  private apiUrl = API_CONFIG.baseUrl;
  private endpoint = API_CONFIG.endpoints.transacoes;

  constructor(private http: HttpClient) {}

  /**
   * Busca todas as transações do usuário autenticado
   */
  listarTransacoes(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}${this.endpoint}`);
  }

  /**
   * Busca uma transação por ID
   */
  obterTransacao(id: number): Observable<Transacao> {
    return this.http.get<Transacao>(`${this.apiUrl}${this.endpoint}${id}/`);
  }

  /**
   * Cria uma nova transação
   */
  criarTransacao(transacao: Transacao): Observable<Transacao> {
    return this.http.post<Transacao>(`${this.apiUrl}${this.endpoint}`, transacao);
  }

  /**
   * Atualiza uma transação existente
   */
  atualizarTransacao(id: number, transacao: Partial<Transacao>): Observable<Transacao> {
    return this.http.put<Transacao>(`${this.apiUrl}${this.endpoint}${id}/`, transacao);
  }

  /**
   * Atualiza parcialmente uma transação
   */
  atualizarParcial(id: number, transacao: Partial<Transacao>): Observable<Transacao> {
    return this.http.patch<Transacao>(`${this.apiUrl}${this.endpoint}${id}/`, transacao);
  }

  /**
   * Deleta uma transação
   */
  deletarTransacao(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${this.endpoint}${id}/`);
  }
}
