import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../config/api.config';

export interface Lembrete {
  id?: number;
  titulo: string;
  descricao?: string;
  data_lembrete?: string;
  dias_antes?: number;
  recorrencia?: 'nenhuma' | 'diaria' | 'semanal' | 'mensal' | 'anual';
  ativo: boolean;
  transacao?: number;
  criado_em?: string;
  ultimo_disparo?: string;
}

@Injectable({
  providedIn: 'root'
})
export class LembreteService {
  private apiUrl = API_CONFIG.baseUrl;
  private endpoint = API_CONFIG.endpoints.lembretes;

  constructor(private http: HttpClient) {}

  /**
   * Busca todos os lembretes do usuário autenticado
   */
  listarLembretes(): Observable<Lembrete[]> {
    return this.http.get<Lembrete[]>(`${this.apiUrl}${this.endpoint}`);
  }

  /**
   * Busca um lembrete por ID
   */
  obterLembrete(id: number): Observable<Lembrete> {
    return this.http.get<Lembrete>(`${this.apiUrl}${this.endpoint}${id}/`);
  }

  /**
   * Cria um novo lembrete
   */
  criarLembrete(lembrete: Lembrete): Observable<Lembrete> {
    return this.http.post<Lembrete>(`${this.apiUrl}${this.endpoint}`, lembrete);
  }

  /**
   * Atualiza um lembrete existente
   */
  atualizarLembrete(id: number, lembrete: Partial<Lembrete>): Observable<Lembrete> {
    return this.http.put<Lembrete>(`${this.apiUrl}${this.endpoint}${id}/`, lembrete);
  }

  /**
   * Deleta um lembrete
   */
  deletarLembrete(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${this.endpoint}${id}/`);
  }
}
