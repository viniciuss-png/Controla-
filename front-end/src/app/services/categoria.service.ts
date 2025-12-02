import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_CONFIG } from '../config/api.config';

export interface Categoria {
  id?: number;
  nome: string;
  tipo_categoria: 'entrada' | 'saida';
}

@Injectable({
  providedIn: 'root'
})
export class CategoriaService {
  private apiUrl = API_CONFIG.baseUrl;
  private endpoint = API_CONFIG.endpoints.categorias;

  constructor(private http: HttpClient) {}

  /**
   * Busca todas as categorias do usuário autenticado
   */
  listarCategorias(): Observable<Categoria[]> {
    return this.http.get<Categoria[]>(`${this.apiUrl}${this.endpoint}`);
  }

  /**
   * Busca uma categoria por ID
   */
  obterCategoria(id: number): Observable<Categoria> {
    return this.http.get<Categoria>(`${this.apiUrl}${this.endpoint}${id}/`);
  }

  /**
   * Cria uma nova categoria
   */
  criarCategoria(categoria: Categoria): Observable<Categoria> {
    return this.http.post<Categoria>(`${this.apiUrl}${this.endpoint}`, categoria);
  }

  /**
   * Atualiza uma categoria existente
   */
  atualizarCategoria(id: number, categoria: Partial<Categoria>): Observable<Categoria> {
    return this.http.put<Categoria>(`${this.apiUrl}${this.endpoint}${id}/`, categoria);
  }

  /**
   * Deleta uma categoria
   */
  deletarCategoria(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}${this.endpoint}${id}/`);
  }
}
