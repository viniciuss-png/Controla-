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

export interface ResumoFinanceiro {
  saldo_liquido: number;
  total_entradas: number;
  total_saidas: number;
  pede_meia_recebido: number; // soma total recebida do Pé-de-Meia (pago=true)
  parcelas_pendentes: Array<{ data: string; valor: number; descricao: string }>;
  saldos_por_conta: Array<{ id: number; nome: string; saldo_atual: number }>;
  gastos_por_categoria?: Array<{ categoria__nome: string; total: number }>; // opcional
}

export interface DashboardData {
  resumo: {
    total_entradas: number;
    total_saidas: number;
    saldo_liquido: number;
    pede_meia_recebido: number;
    pede_meia_pendente: number;
  };
  graficos: {
    gastos_categoria: Array<{ categoria__nome: string; total: number }>;
    entradas_categoria: Array<{ categoria__nome: string; total: number }>;
  };
  incentivos: {
    conclusao: Array<{ id: number; ano: number; valor: number; liberado: boolean; criado_em: string }>;
    enem: Array<{ id: number; ano: number; valor: number; liberado: boolean; criado_em: string }>;
    pede_meia?: { id: number; data: string; descricao: string; valor: number; pago: boolean; categoria__nome: string } | null;
  };
  contas: Array<{ id: number; nome: string; saldo_inicial: number; saldo_atual: number }>;
  metas: Array<{ id: number; nome: string; valor_alvo: number; data_alvo: string; ativa: boolean }>;
  transacoes_recentes: Array<{ id: number; data: string; tipo: string; descricao: string; valor: number; categoria__nome: string; pago: boolean }>;
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

  // Dashboard / Pé-de-Meia
  getResumoFinanceiro(params?: { from_date?: string; to_date?: string }) {
    let httpParams = new HttpParams();
    if (params?.from_date) httpParams = httpParams.set('from_date', params.from_date);
    if (params?.to_date) httpParams = httpParams.set('to_date', params.to_date);
    return this.http.get<ResumoFinanceiro>(`${this.baseUrl}/transacoes/resumo_financeiro/`, {
      headers: this.authHeaders(),
      params: httpParams,
    });
  }

  // Dashboard consolidado
  getDashboardData(params?: { from_date?: string; to_date?: string }) {
    let httpParams = new HttpParams();
    if (params?.from_date) httpParams = httpParams.set('from_date', params.from_date);
    if (params?.to_date) httpParams = httpParams.set('to_date', params.to_date);
    return this.http.get<DashboardData>(`${this.baseUrl}/dashboard/`, {
      headers: this.authHeaders(),
      params: httpParams,
    });
  }

  confirmarRecebimento(body?: { mes?: number; ano?: number }) {
    const payload: any = {};
    if (body?.mes) payload.mes = body.mes;
    if (body?.ano) payload.ano = body.ano;
    return this.http.post<{ detail: string; transacao_id: number; valor: number }>(
      `${this.baseUrl}/transacoes/confirmar_recebimento/`,
      payload,
      { headers: this.authHeaders() }
    );
  }

  // Incentivos: conclusão (liberar)
  liberarIncentivoConclusao(incentivo_id: number) {
    return this.http.post<{ id: number; transacao_id: number; valor: number }>(
      `${this.baseUrl}/incentivos/conclusao/liberar/`,
      { incentivo_id },
      { headers: this.authHeaders() }
    );
  }

  // Incentivos: criação de conclusão
  criarIncentivoConclusao(conta_id?: number) {
    const body: any = {};
    // Adiciona o ano atual do sistema
    body.ano = new Date().getFullYear();
    if (typeof conta_id === 'number') body.conta_id = conta_id;
    return this.http.post<{ id: number; valor: number; liberado: boolean }>(
      `${this.baseUrl}/incentivos/conclusao/`,
      body,
      { headers: this.authHeaders() }
    );
  }

  // Incentivos: criação do ENEM
  criarIncentivoEnem(ano: number, conta_id?: number) {
    const body: any = { ano };
    if (typeof conta_id === 'number') body.conta_id = conta_id;
    return this.http.post<{ id: number; transacao_id: number; valor: number }>(
      `${this.baseUrl}/incentivos/enem/`,
      body,
      { headers: this.authHeaders() }
    );
  }

  // Incentivos: criar parcela mensal pendente (Pé-de-Meia)
  criarParcelaPedeMeia(mes: number, ano: number, valor: number, conta_id?: number, categoria?: string) {
    const body: any = { mes, ano, valor };
    if (typeof conta_id === 'number') body.conta_id = conta_id;
    if (typeof categoria === 'string') body.categoria = categoria;
    return this.http.post<{ transacao_id: number; valor: number; data: string }>(
      `${this.baseUrl}/incentivos/parcela/`,
      body,
      { headers: this.authHeaders() }
    );
  }
}
