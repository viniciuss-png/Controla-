import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { HeaderComponent } from '../shared/header/header.component';
import { FooterComponent } from '../shared/footer/footer.component';
import { FormsModule } from '@angular/forms';
import { TransacoesService, Categoria, Conta, NovaTransacaoPayload, TransacaoItem } from '../../services/transacoes.service';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
 

@Component({
  selector: 'app-transacoes',
  standalone: true,
  imports: [CommonModule, RouterModule, HeaderComponent, FooterComponent, FormsModule],
  templateUrl: './transacoes.component.html',
  styleUrls: ['./transacoes.component.scss']
})
export class TransacoesComponent {
  private svc = inject(TransacoesService);
  private platformId = inject(PLATFORM_ID);
  private route = inject(ActivatedRoute);

  showModal = false;
  showToastSuccess = false;
  showToast = false; // manter para transação criada, não para categoria/conta
  toastMessage: string = '';
  showMsgEditCategoria = false;
  showMsgEditConta = false;
  showMsgDeleteCategoria = false;
  showMsgDeleteConta = false;
  showEditModal = false;
  editTarget: TransacaoItem | null = null;
  editForm: Partial<NovaTransacaoPayload> = {};
  // overlay confirmação de exclusão
  showDeleteModal = false;
  deleteTarget: TransacaoItem | null = null;

  // gerenciamento de categoria
  showEditCategoriaModal = false;
  showDeleteCategoriaModal = false;
  editCategoriaForm: { id: number | null; nome: string; tipo_categoria: 'entrada' | 'saida' } = { id: null, nome: '', tipo_categoria: 'saida' };

  // gerenciamento de conta
  showEditContaModal = false;
  showDeleteContaModal = false;
  editContaForm: { id: number | null; nome: string; saldo_inicial?: number } = { id: null, nome: '' };
  categorias: Categoria[] = [];
  contas: Conta[] = [];
  transacoes: TransacaoItem[] = [];
  transacoesFiltradas: TransacaoItem[] = [];
  historicoCarregado = false;
  loading = false;
  error: string | null = null;

  // filtros e busca
  filtroTipo: 'todas' | 'entrada' | 'saida' = 'todas';
  termoBusca = '';

  // toggles para criação inline
  showNovaCategoria = false;
  showNovaConta = false;

  // forms inline
  novaCategoria = {
    nome: '',
    tipo_categoria: 'saida' as 'entrada' | 'saida'
  };

  novaConta = {
    nome: '',
    saldo_inicial: 0
  };

  form: NovaTransacaoPayload = {
    tipo: 'saida',
    descricao: '',
    valor: 0,
    data: new Date().toISOString().slice(0, 10),
    parcelas: 1,
    vencimento: null,
    pago: false,
    categoria: 0,
    conta: 0,
  };

  ngOnInit() {
    // carregar histórico de transações ao entrar na página (apenas no browser)
    if (isPlatformBrowser(this.platformId)) {
      const dadosResolver = this.route.snapshot.data?.['transacoes'] as TransacaoItem[] | undefined;
      if (dadosResolver && Array.isArray(dadosResolver)) {
        this.transacoes = dadosResolver;
        this.historicoCarregado = true;
        this.aplicarFiltro();
      } else {
        this.carregarTransacoes();
      }
    }
  }

  private carregarTransacoes() {
    const token = localStorage.getItem('access_token');
    if (!token) { return; }
    this.svc.listarTransacoes().subscribe({
      next: (items) => { this.transacoes = items; this.historicoCarregado = true; this.aplicarFiltro(); },
      error: () => { this.historicoCarregado = true; /* silencioso para não poluir UI */ }
    });
  }

  

  openModal() {
    // apenas no browser
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.error = 'Você precisa estar logado para criar transações.';
      this.showModal = false;
      return;
    }

    this.showModal = true;
    this.error = null;
    this.loading = true;
    // Carregar categorias e contas em paralelo
    this.svc.listarCategorias().subscribe({
      next: (cats) => { this.categorias = cats; },
      error: () => { this.error = 'Falha ao carregar categorias'; }
    });
    this.svc.listarContas().subscribe({
      next: (cts) => { this.contas = cts; },
      error: () => { this.error = 'Falha ao carregar contas'; },
      complete: () => { this.loading = false; }
    });
  }

  closeModal() {
    this.showModal = false;
    this.resetOverlayForm();
  }

  salvarTransacao() {
    this.error = null;
    if (!this.form.descricao || !this.form.valor || !this.form.data || !this.form.categoria || !this.form.conta) {
      this.error = 'Preencha todos os campos obrigatórios.';
      return;
    }
    this.loading = true;
    this.svc.criarTransacao(this.form).subscribe({
      next: () => {
        this.loading = false;
        // Fecha o overlay e mostra toast
        this.closeModal();
        this.showToastSuccess = true;
        this.toastMessage = 'Transação criada com sucesso';
        this.showToast = true;
        this.error = null;
        // Recarrega a página após breve delay
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => { window.location.reload(); }, 1200);
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || 'Erro ao criar transação.';
      }
    });
  }

  setFiltro(tipo: 'todas' | 'entrada' | 'saida') {
    this.filtroTipo = tipo;
    this.aplicarFiltro();
  }

  onBuscaChange(value: string) {
    this.termoBusca = value;
    this.aplicarFiltro();
  }

  private aplicarFiltro() {
    const termo = this.termoBusca.trim().toLowerCase();
    this.transacoesFiltradas = this.transacoes.filter(t => {
      const tipoOk = this.filtroTipo === 'todas' ? true : t.tipo === this.filtroTipo;
      const buscaOk = !termo
        ? true
        : (
            (t.descricao?.toLowerCase().includes(termo)) ||
            (t.categoria_nome?.toLowerCase().includes(termo)) ||
            (t.conta_nome?.toLowerCase().includes(termo))
          );
      return tipoOk && buscaOk;
    });
  }

  exportarPDF() {
    this.loading = true;
    this.svc.gerarRelatorioPDF().subscribe({
      next: (blob) => {
        this.loading = false;
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_financeiro_${new Date().toISOString().slice(0,10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      },
      error: () => {
        this.loading = false;
        this.error = 'Falha ao gerar relatório PDF.';
      }
    });
  }

  // ações por transação
  abrirEditar(t: TransacaoItem) {
    this.editTarget = t;
    this.editForm = {
      tipo: t.tipo,
      descricao: t.descricao,
      valor: t.valor,
      data: typeof t.data === 'string' ? t.data.slice(0, 10) : new Date(t.data).toISOString().slice(0, 10),
      parcelas: t.parcelas,
      vencimento: t.vencimento ? (typeof t.vencimento === 'string' ? t.vencimento.slice(0, 10) : null) : null,
      pago: t.pago,
      categoria: t.categoria,
      conta: t.conta,
    };
    // garantir que selects tenham opções atuais
    if (!this.categorias.length) {
      this.svc.listarCategorias().subscribe({ next: (cats) => this.categorias = cats });
    }
    if (!this.contas.length) {
      this.svc.listarContas().subscribe({ next: (cts) => this.contas = cts });
    }
    this.showEditModal = true;
  }

  cancelarEdicao() {
    this.showEditModal = false;
    this.editTarget = null;
    this.editForm = {};
  }

  salvarEdicao() {
    if (!this.editTarget?.id) return;
    this.loading = true;
    this.svc.atualizarTransacao(this.editTarget.id, this.editForm).subscribe({
      next: () => {
        this.loading = false;
        this.showEditModal = false;
        // recarrega página para refletir mudanças, conforme solicitado
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => window.location.reload(), 800);
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || 'Erro ao atualizar transação.';
      }
    });
  }

  apagar(t: TransacaoItem) {
    this.deleteTarget = t;
    this.showDeleteModal = true;
  }

  confirmarApagar() {
    if (!this.deleteTarget) return;
    this.loading = true;
    this.svc.apagarTransacao(this.deleteTarget.id).subscribe({
      next: () => {
        this.loading = false;
        this.showDeleteModal = false;
        this.deleteTarget = null;
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => window.location.reload(), 500);
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = err?.error?.detail || 'Erro ao apagar transação.';
      }
    });
  }

  cancelarApagar() {
    this.showDeleteModal = false;
    this.deleteTarget = null;
  }

  // Categoria - abrir/editar/excluir
  abrirEditarCategoria() {
    // garante dados carregados
    if (!this.categorias.length) {
      this.svc.listarCategorias().subscribe({ next: (cats) => this.categorias = cats });
    }
    const cat = this.categorias.find(c => c.id === this.form.categoria) || this.categorias[0];
    if (!cat) { this.error = 'Nenhuma categoria encontrada. Crie uma primeiro.'; return; }
    this.editCategoriaForm = { id: cat.id, nome: cat.nome, tipo_categoria: cat.tipo_categoria };
    this.showEditCategoriaModal = true;
  }

  salvarEdicaoCategoria() {
    const id = this.editCategoriaForm.id; if (!id) return;
    this.loading = true;
    this.svc.atualizarCategoria(id, { nome: this.editCategoriaForm.nome, tipo_categoria: this.editCategoriaForm.tipo_categoria }).subscribe({
      next: (updated) => {
        this.loading = false;
        // fechar overlay e recarregar página, igual transações
        this.showEditCategoriaModal = false;
        this.categorias = this.categorias.map(c => c.id === updated.id ? updated : c);
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => window.location.reload(), 800);
        }
        // mantém seleção caso id seja o mesmo
      },
      error: (err) => { this.loading = false; this.error = err?.error?.detail || 'Erro ao editar categoria.'; }
    });
  }

  abrirExcluirCategoria() {
    // garante dados carregados
    if (!this.categorias.length) {
      this.svc.listarCategorias().subscribe({ next: (cats) => {
        this.categorias = cats;
        const first = this.categorias[0];
        if (!first) { this.error = 'Nenhuma categoria encontrada. Crie uma primeiro.'; return; }
        this.editCategoriaForm = { id: first.id, nome: first.nome, tipo_categoria: first.tipo_categoria };
        this.showDeleteCategoriaModal = true;
      }});
      return;
    }
    const selected = this.categorias.find(c => c.id === this.form.categoria) || this.categorias[0];
    if (!selected) { this.error = 'Nenhuma categoria encontrada. Crie uma primeiro.'; return; }
    this.editCategoriaForm = { id: selected.id, nome: selected.nome, tipo_categoria: selected.tipo_categoria };
    this.showDeleteCategoriaModal = true;
  }

  confirmarExcluirCategoria() {
    const id = this.editCategoriaForm.id; if (!id) return;
    this.loading = true;
    this.svc.apagarCategoria(id).subscribe({
      next: () => {
        this.loading = false;
        // fechar overlay e recarregar página, igual transações
        this.showDeleteCategoriaModal = false;
        this.categorias = this.categorias.filter(c => c.id !== id);
        if (this.form.categoria === id) this.form.categoria = 0;
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => window.location.reload(), 800);
        }
      },
      error: (err) => { this.loading = false; this.error = err?.error?.detail || 'Erro ao excluir categoria.'; }
    });
  }

  cancelarExcluirCategoria() { this.showDeleteCategoriaModal = false; }

  // Conta - abrir/editar/excluir
  abrirEditarConta() {
    if (!this.contas.length) {
      this.svc.listarContas().subscribe({ next: (cts) => this.contas = cts });
    }
    const conta = this.contas.find(c => c.id === this.form.conta) || this.contas[0];
    if (!conta) { this.error = 'Nenhuma conta encontrada. Crie uma primeiro.'; return; }
    this.editContaForm = { id: conta.id, nome: conta.nome };
    this.showEditContaModal = true;
  }

  salvarEdicaoConta() {
    const id = this.editContaForm.id; if (!id) return;
    this.loading = true;
    this.svc.atualizarConta(id, { nome: this.editContaForm.nome, saldo_inicial: this.editContaForm.saldo_inicial }).subscribe({
      next: (updated) => {
        this.loading = false;
        // fechar overlay e recarregar página, igual transações
        this.showEditContaModal = false;
        this.contas = this.contas.map(c => c.id === (updated as any).id ? (updated as any) : c);
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => window.location.reload(), 800);
        }
      },
      error: (err) => { this.loading = false; this.error = err?.error?.detail || 'Erro ao editar conta.'; }
    });
  }

  abrirExcluirConta() {
    if (!this.contas.length) {
      this.svc.listarContas().subscribe({ next: (cts) => {
        this.contas = cts;
        const first = this.contas[0];
        if (!first) { this.error = 'Nenhuma conta encontrada. Crie uma primeiro.'; return; }
        this.editContaForm = { id: first.id, nome: first.nome };
        this.showDeleteContaModal = true;
      }});
      return;
    }
    const selected = this.contas.find(c => c.id === this.form.conta) || this.contas[0];
    if (!selected) { this.error = 'Nenhuma conta encontrada. Crie uma primeiro.'; return; }
    this.editContaForm = { id: selected.id, nome: selected.nome };
    this.showDeleteContaModal = true;
  }

  confirmarExcluirConta() {
    const id = this.editContaForm.id; if (!id) return;
    this.loading = true;
    this.svc.apagarConta(id).subscribe({
      next: () => {
        this.loading = false;
        // fechar overlay e recarregar página, igual transações
        this.showDeleteContaModal = false;
        this.contas = this.contas.filter(c => c.id !== id);
        if (this.form.conta === id) this.form.conta = 0;
        if (isPlatformBrowser(this.platformId)) {
          setTimeout(() => window.location.reload(), 800);
        }
      },
      error: (err) => { this.loading = false; this.error = err?.error?.detail || 'Erro ao excluir conta.'; }
    });
  }

  cancelarExcluirConta() { this.showDeleteContaModal = false; }

  // Atualiza formulário de edição ao escolher item no select
  onSelectEditCategoria(id: number) {
    const cat = this.categorias?.find(c => c.id === Number(id));
    this.editCategoriaForm = {
      id: Number(id),
      nome: cat?.nome || '',
      tipo_categoria: (cat?.tipo_categoria as 'entrada' | 'saida') || 'saida',
    };
  }

  onSelectEditConta(id: number) {
    const conta = this.contas?.find(c => c.id === Number(id));
    this.editContaForm = {
      id: Number(id),
      nome: conta?.nome || '',
      saldo_inicial: (conta as any)?.saldo_inicial,
    } as { id: number | null; nome: string; saldo_inicial?: number };
  }

  toggleNovaCategoria() {
    this.showNovaCategoria = !this.showNovaCategoria;
    // sempre resetar ao abrir/fechar
    this.novaCategoria = { nome: '', tipo_categoria: 'saida' };
  }

  toggleNovaConta() {
    this.showNovaConta = !this.showNovaConta;
    // sempre resetar ao abrir/fechar
    this.novaConta = { nome: '', saldo_inicial: 0 };
  }

  criarCategoriaInline() {
    if (!this.novaCategoria.nome) {
      this.error = 'Informe o nome da categoria.';
      return;
    }
    this.loading = true;
    this.svc.criarCategoria(this.novaCategoria).subscribe({
      next: (cat) => {
        // adiciona à lista e reseta inline para permitir escolher ou criar outra
        this.categorias = [...this.categorias, cat];
        this.novaCategoria = { nome: '', tipo_categoria: 'saida' };
        this.showNovaCategoria = false;
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.error?.nome?.[0] || err?.error?.detail || 'Erro ao criar categoria.';
        this.loading = false;
      }
    });
  }

  criarContaInline() {
    if (!this.novaConta.nome) {
      this.error = 'Informe o nome da conta.';
      return;
    }
    this.loading = true;
    this.svc.criarConta(this.novaConta).subscribe({
      next: (conta) => {
        // adiciona à lista e reseta inline para permitir escolher ou criar outra
        this.contas = [...this.contas, conta];
        this.novaConta = { nome: '', saldo_inicial: 0 };
        this.showNovaConta = false;
        this.loading = false;
      },
      error: (err) => {
        this.error = err?.error?.nome?.[0] || err?.error?.detail || 'Erro ao criar conta.';
        this.loading = false;
      }
    });
  }

  private resetOverlayForm() {
    this.form = {
      tipo: 'saida',
      descricao: '',
      valor: 0,
      data: new Date().toISOString().slice(0, 10),
      parcelas: 1,
      vencimento: null,
      pago: false,
      categoria: 0,
      conta: 0,
    };
    // também garantir inline fechado e limpo
    this.showNovaCategoria = false;
    this.novaCategoria = { nome: '', tipo_categoria: 'saida' };
    this.showNovaConta = false;
    this.novaConta = { nome: '', saldo_inicial: 0 };
  }
}
