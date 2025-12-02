import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../config/api.config';

export interface Notificacao {
  id?: number;
  texto: string;
  lido?: boolean;
  criado_em?: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificacaoService {
  private apiUrl = API_CONFIG.baseUrl;
  private endpoint = API_CONFIG.endpoints.notificacoes;

  constructor(private http: HttpClient) {}

  /**
   * Busca todas as notificações do usuário autenticado
   */
  listarNotificacoes(): Observable<Notificacao[]> {
    return this.http.get<Notificacao[]>(`${this.apiUrl}${this.endpoint}`);
  }

  /**
   * Busca uma notificação por ID
   */
  obterNotificacao(id: number): Observable<Notificacao> {
    return this.http.get<Notificacao>(`${this.apiUrl}${this.endpoint}${id}/`);
  }

  /**
   * Marca uma notificação como lida
   */
  marcarComoLida(id: number): Observable<Notificacao> {
    return this.http.patch<Notificacao>(`${this.apiUrl}${this.endpoint}${id}/`, { lido: true });
  }

  /**
   * Deleta uma notificação
   */
  deletarNotificacao(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${this.endpoint}${id}/`);
  }
}
