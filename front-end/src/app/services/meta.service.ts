import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../config/api.config';

export interface MetaFinanceira {
  id?: number;
  nome: string;
  valor_alvo: number;
  valor_atual?: number;
  data_alvo?: string;
  ativa: boolean;
  conta_vinculada?: number;
  conta_nome?: string;
}

@Injectable({
  providedIn: 'root'
})
export class MetaService {
  private apiUrl = API_CONFIG.baseUrl;
  private endpoint = API_CONFIG.endpoints.metas;

  constructor(private http: HttpClient) {}

  /**
   * Busca todas as metas do usuário autenticado
   */
  listarMetas(): Observable<MetaFinanceira[]> {
    return this.http.get<MetaFinanceira[]>(`${this.apiUrl}${this.endpoint}`);
  }

  /**
   * Busca uma meta por ID
   */
  obterMeta(id: number): Observable<MetaFinanceira> {
    return this.http.get<MetaFinanceira>(`${this.apiUrl}${this.endpoint}${id}/`);
  }

  /**
   * Cria uma nova meta financeira
   */
  criarMeta(meta: MetaFinanceira): Observable<MetaFinanceira> {
    return this.http.post<MetaFinanceira>(`${this.apiUrl}${this.endpoint}`, meta);
  }

  /**
   * Atualiza uma meta existente
   */
  atualizarMeta(id: number, meta: Partial<MetaFinanceira>): Observable<MetaFinanceira> {
    return this.http.put<MetaFinanceira>(`${this.apiUrl}${this.endpoint}${id}/`, meta);
  }

  /**
   * Deleta uma meta
   */
  deletarMeta(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${this.endpoint}${id}/`);
  }
}
