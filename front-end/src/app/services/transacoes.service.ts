import { inject, Injectable } from '@angular/core';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { map } from 'rxjs';

export interface Categoria {
  id: number;
  nome: string;
  tipo_categoria: 'entrada' | 'saida';
}

export interface Conta {
  id: number;
  nome: string;
}

export interface NovaTransacaoPayload {
  tipo: 'entrada' | 'saida';
  descricao: string;
  valor: number;
  data: string; // YYYY-MM-DD
  parcelas: number;
  vencimento?: string | null; // YYYY-MM-DD
  pago: boolean;
  categoria: number; // id
  conta: number; // id
}

export interface TransacaoItem {
  id: number;
  tipo: 'entrada' | 'saida';
  descricao: string;
  valor: number;
  data: string; // YYYY-MM-DD
  parcelas: number;
  vencimento?: string | null;
  pago: boolean;
  categoria: number;
  categoria_nome: string;
  tipo_categoria: 'entrada' | 'saida';
  conta: number;
  conta_nome: string;
}

export interface LembretePayload {
  titulo: string;
  descricao?: string;
  data_lembrete?: string | null; // YYYY-MM-DD
  dias_antes?: number; // >= 0
  recorrencia: 'nenhuma' | 'diaria' | 'semanal' | 'mensal' | 'anual';
  transacao?: number | null; // id
  ativo?: boolean;
}

@Injectable({ providedIn: 'root' })
export class TransacoesService {
  private http = inject(HttpClient);
  private baseUrl = 'http://localhost:8000/api';
  private platformId = inject(PLATFORM_ID);

  private authHeaders(): HttpHeaders {
    const token = isPlatformBrowser(this.platformId) ? localStorage.getItem('access_token') : null;
    return new HttpHeaders(token ? { Authorization: `Bearer ${token}` } : {});
  }

  listarCategorias() {
    return this.http.get<Categoria[]>(`${this.baseUrl}/categorias/`, { headers: this.authHeaders() });
  }

  listarContas() {
    return this.http.get<Conta[]>(`${this.baseUrl}/contas/`, { headers: this.authHeaders() });
  }

  criarTransacao(payload: NovaTransacaoPayload) {
    return this.http.post(`${this.baseUrl}/transacoes/`, payload, { headers: this.authHeaders() });
  }

  listarTransacoes() {
    return this.http.get<any>(`${this.baseUrl}/transacoes/`, { headers: this.authHeaders() }).pipe(
      map((res) => Array.isArray(res) ? res : (res?.results ?? [])),
      map((items: any[]) => items.map((i) => ({
        ...i,
        // garantir número para pipe de número
        valor: typeof i.valor === 'string' ? Number(i.valor) : i.valor,
        // garantir data ISO parseável pelo Angular DatePipe
        data: (typeof i.data === 'string' && i.data.length === 10) ? `${i.data}T00:00:00` : i.data,
      }) as TransacaoItem))
    );
  }

  atualizarTransacao(id: number, payload: Partial<NovaTransacaoPayload>) {
    return this.http.put(`${this.baseUrl}/transacoes/${id}/`, payload, { headers: this.authHeaders() });
  }

  apagarTransacao(id: number) {
    return this.http.delete(`${this.baseUrl}/transacoes/${id}/`, { headers: this.authHeaders() });
  }

  gerarRelatorioPDF(opts?: { from_date?: string; to_date?: string }) {
    let params = new HttpParams();
    if (opts?.from_date) params = params.set('from_date', opts.from_date);
    if (opts?.to_date) params = params.set('to_date', opts.to_date);
    return this.http.get(`${this.baseUrl}/relatorio/pdf/`, {
      headers: this.authHeaders(),
      params,
      responseType: 'blob'
    });
  }

  criarCategoria(body: { nome: string; tipo_categoria: 'entrada' | 'saida' }) {
    return this.http.post<Categoria>(`${this.baseUrl}/categorias/`, body, { headers: this.authHeaders() });
  }

  criarConta(body: { nome: string; saldo_inicial?: number }) {
    return this.http.post<Conta>(`${this.baseUrl}/contas/`, body, { headers: this.authHeaders() });
  }

  atualizarCategoria(id: number, body: { nome: string; tipo_categoria: 'entrada' | 'saida' }) {
    return this.http.put<Categoria>(`${this.baseUrl}/categorias/${id}/`, body, { headers: this.authHeaders() });
  }

  apagarCategoria(id: number) {
    return this.http.delete(`${this.baseUrl}/categorias/${id}/`, { headers: this.authHeaders() });
  }

  atualizarConta(id: number, body: { nome: string; saldo_inicial?: number }) {
    return this.http.put<Conta>(`${this.baseUrl}/contas/${id}/`, body, { headers: this.authHeaders() });
  }

  apagarConta(id: number) {
    return this.http.delete(`${this.baseUrl}/contas/${id}/`, { headers: this.authHeaders() });
  }

  // Lembretes
  criarLembrete(body: LembretePayload) {
    return this.http.post(`${this.baseUrl}/lembretes/`, body, { headers: this.authHeaders() });
  }
  listarLembretes() {
    return this.http.get<any>(`${this.baseUrl}/lembretes/`, { headers: this.authHeaders() }).pipe(
      map((res) => Array.isArray(res) ? res : (res?.results ?? []))
    );
  }
  atualizarLembrete(id: number, body: Partial<LembretePayload>) {
    return this.http.put(`${this.baseUrl}/lembretes/${id}/`, body, { headers: this.authHeaders() });
  }
  apagarLembrete(id: number) {
    return this.http.delete(`${this.baseUrl}/lembretes/${id}/`, { headers: this.authHeaders() });
  }
}
