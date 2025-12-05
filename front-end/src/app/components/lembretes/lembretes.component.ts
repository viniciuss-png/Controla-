import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { HeaderComponent } from '../shared/header/header.component';
import { FooterComponent } from '../shared/footer/footer.component';
import { FormsModule } from '@angular/forms';
import { TransacoesService, LembretePayload, TransacaoItem } from '../../services/transacoes.service';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-lembretes',
  standalone: true,
  imports: [CommonModule, RouterModule, HeaderComponent, FooterComponent, FormsModule],
  templateUrl: './lembretes.component.html',
  styleUrls: ['./lembretes.component.scss']
})
export class LembretesComponent {
  private svc = inject(TransacoesService);
  private platformId = inject(PLATFORM_ID);
  private route = inject(ActivatedRoute);

  showNovoLembrete = false;
  loading = false;
  error: string | null = null;

  transacoes: TransacaoItem[] = [];
  lembretes: any[] = [];
  today = new Date();
  private transMap = new Map<number, TransacaoItem>();
  private doneSet = new Set<number>();

  // Controle de visibilidade de valores
  showValores = false;

  toggleMostrarValores() {
    this.showValores = !this.showValores;
  }

  form: LembretePayload = {
    titulo: '',
    data_lembrete: null,
    dias_antes: 0,
    recorrencia: 'nenhuma',
    transacao: null,
    ativo: true,
  };

  openNovoLembrete() {
    this.error = null;
    this.showNovoLembrete = true;
    this.loading = true;
    if (!isPlatformBrowser(this.platformId)) { this.loading = false; return; }
    this.svc.listarTransacoes().subscribe({
      next: (ts) => { this.transacoes = ts; },
      complete: () => { this.loading = false; }
    });
  }

  closeNovoLembrete() {
    this.showNovoLembrete = false;
    this.form = { titulo: '', data_lembrete: null, dias_antes: 0, recorrencia: 'nenhuma', transacao: null, ativo: true };
  }

  salvarLembrete() {
    const titulo = this.form.titulo?.trim();
    const recorr = this.form.recorrencia;
    // só é possível concluir com transação selecionada
    if (!titulo || !recorr || !this.form.transacao) {
      this.error = 'Informe título, recorrência e selecione uma transação.';
      return;
    }
    // garantir formato YYYY-MM-DD
    const dataFmt = this.form.data_lembrete ? String(this.form.data_lembrete).slice(0,10) : null;
    // normalizar tipos: dias_antes inteiro >=0, transacao número ou undefined, ativo boolean
    const dias = (this.form.dias_antes ?? 0);
    const diasInt = Number.isFinite(dias as number) ? Math.max(0, Math.floor(dias as number)) : 0;
    const transId = this.form.transacao;
    const transacaoNorm = typeof transId === 'string' ? (transId === 'null' ? undefined : Number(transId)) : (typeof transId === 'number' ? transId : undefined);
    const ativoNorm = typeof this.form.ativo === 'string' ? this.form.ativo === 'true' : !!this.form.ativo;

    const payload: LembretePayload = {
      titulo,
      descricao: this.form.descricao,
      data_lembrete: dataFmt,
      dias_antes: diasInt,
      recorrencia: recorr,
      transacao: transacaoNorm,
      ativo: ativoNorm,
    };
    this.loading = true;
    this.svc.criarLembrete(payload).subscribe({
      next: () => {
        this.loading = false;
        this.showNovoLembrete = false;
        // Atualiza a página após adicionar lembrete
        location.reload();
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || err?.message || 'Erro ao criar lembrete.';
      }
    });
  }

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.restoreDone();
      const dadosResolver = this.route.snapshot.data?.['lembretes'] as any[] | undefined;
      if (dadosResolver && Array.isArray(dadosResolver)) {
        this.lembretes = dadosResolver;
        this.svc.listarTransacoes().subscribe({
          next: (ts) => { this.transacoes = ts; this.transMap = new Map(ts.map(t => [t.id, t])); },
          error: (err) => { this.error = err?.error?.detail || 'Erro ao carregar transações.'; }
        });
      } else {
        this.carregarLembretes();
      }
    }
  }

  private carregarLembretes() {
    // Apenas no browser e com token
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.error = 'Você precisa estar logado para ver seus lembretes.';
      return;
    }
    this.svc.listarLembretes().subscribe({
      next: (list) => {
        this.lembretes = list ?? [];
        this.svc.listarTransacoes().subscribe({
          next: (ts) => {
            this.transacoes = ts;
            this.transMap = new Map(ts.map(t => [t.id, t]));
          },
          error: (err) => {
            this.error = err?.error?.detail || 'Erro ao carregar transações.';
          }
        });
      },
      error: (err) => {
        if (err?.status === 401) {
          this.error = 'Sessão expirada ou não autenticada. Faça login para continuar.';
        } else {
          this.error = err?.error?.detail || 'Erro ao carregar lembretes.';
        }
      }
    });
  }

  isVencido(l: any): boolean {
    const d = this.getVencimentoDate(l);
    if (!d) return false;
    // compara apenas data (sem horário)
    const iso = (dt: Date) => new Date(dt.getFullYear(), dt.getMonth(), dt.getDate());
    return iso(d).getTime() < iso(this.today).getTime();
  }

  private getVincTrans(l: any): TransacaoItem | undefined {
    // aceitar id como number ou string e normalizar
    const rawId = l?.transacao;
    const id = typeof rawId === 'number' ? rawId : (typeof rawId === 'string' ? Number(rawId) : undefined);
    if (!id || Number.isNaN(id)) return undefined;
    return this.transMap.get(id);
  }
  getDescricaoTransacao(l: any): string {
    const t = this.getVincTrans(l);
    return t?.descricao ?? (l?.descricao ?? '-');
  }
  getVencimentoDate(l: any): Date | null {
    const t = this.getVincTrans(l);
    if (t?.vencimento) {
      const vstr = typeof t.vencimento === 'string' ? t.vencimento : String(t.vencimento);
      try { return new Date(vstr); } catch { /* ignore */ }
    }
    if (l?.data_lembrete) {
      const dstr = typeof l.data_lembrete === 'string' ? l.data_lembrete : String(l.data_lembrete);
      try { return new Date(dstr); } catch { return null; }
    }
    return null;
  }
  getVencimentoStr(l: any): string {
    const d = this.getVencimentoDate(l);
    if (!d) return '';
    const dd = d.getDate().toString().padStart(2, '0');
    const mm = (d.getMonth() + 1).toString().padStart(2, '0');
    const yyyy = d.getFullYear();
    return `${dd}/${mm}/${yyyy}`;
  }
  getValor(l: any): number | null {
    const t = this.getVincTrans(l);
    if (!t) return null;
    const val = typeof t.valor === 'string' ? Number(t.valor) : t.valor;
    return Number.isFinite(val as number) ? val : null;
  }

  getTotalPendente(): number {
    const total = this.lembretes.reduce((acc, l) => {
      if (this.isDone(l)) return acc;
      const v = this.getValor(l);
      return acc + (v ?? 0);
    }, 0);
    return Math.round((total + Number.EPSILON) * 100) / 100;
  }

  getQtdPendente(): number {
    return this.lembretes.filter(l => !this.isDone(l)).length;
  }

  isDone(l: any): boolean {
    return this.doneSet.has(l.id);
  }
  toggleDone(l: any) {
    if (this.isDone(l)) {
      this.doneSet.delete(l.id);
    } else {
      this.doneSet.add(l.id);
    }
    this.persistDone();
  }
  private persistDone() {
    if (!isPlatformBrowser(this.platformId)) return;
    try { localStorage.setItem('lembretes_done', JSON.stringify(Array.from(this.doneSet))); } catch {}
  }
  private restoreDone() {
    if (!isPlatformBrowser(this.platformId)) return;
    try {
      const raw = localStorage.getItem('lembretes_done');
      if (raw) { const arr: number[] = JSON.parse(raw); this.doneSet = new Set(arr); }
    } catch {}
  }

  // Editar
  showEditModal = false;
  editForm: LembretePayload & { id?: number } = { titulo: '', recorrencia: 'nenhuma', ativo: true };
  abrirEditar(lemb: any) {
    this.editForm = {
      id: lemb.id,
      titulo: lemb.titulo,
      descricao: lemb.descricao,
      data_lembrete: lemb.data_lembrete ? String(lemb.data_lembrete).slice(0,10) : null,
      dias_antes: lemb.dias_antes ?? 0,
      recorrencia: lemb.recorrencia,
      transacao: lemb.transacao ?? null,
      ativo: !!lemb.ativo,
    };
    this.showEditModal = true;
  }
  cancelarEdicao() { this.showEditModal = false; this.editForm = { titulo: '', recorrencia: 'nenhuma', ativo: true }; }
  salvarEdicao() {
    if (!this.editForm.id) return;
    const payload: Partial<LembretePayload> = {
      titulo: this.editForm.titulo?.trim(),
      descricao: this.editForm.descricao,
      data_lembrete: this.editForm.data_lembrete ? String(this.editForm.data_lembrete).slice(0,10) : null,
      dias_antes: Math.max(0, Math.floor(this.editForm.dias_antes ?? 0)),
      recorrencia: this.editForm.recorrencia,
      transacao: this.editForm.transacao ?? undefined,
      ativo: !!this.editForm.ativo,
    };
    this.loading = true;
    this.svc.atualizarLembrete(this.editForm.id, payload).subscribe({
      next: () => { this.loading = false; this.showEditModal = false; location.reload(); },
      error: (err) => { this.loading = false; this.error = err?.error?.detail || 'Erro ao editar lembrete.'; }
    });
  }

  // Excluir
  showDeleteModal = false;
  deleteTargetId: number | null = null;
  abrirExcluir(lemb: any) { this.deleteTargetId = lemb.id; this.showDeleteModal = true; }
  cancelarExcluir() { this.deleteTargetId = null; this.showDeleteModal = false; }
  confirmarExcluir() {
    if (!this.deleteTargetId) return;
    this.loading = true;
    this.svc.apagarLembrete(this.deleteTargetId).subscribe({
      next: () => { this.loading = false; this.showDeleteModal = false; this.deleteTargetId = null; location.reload(); },
      error: (err) => { this.loading = false; this.error = err?.error?.detail || 'Erro ao excluir lembrete.'; }
    });
  }
}
