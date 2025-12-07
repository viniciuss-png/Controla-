import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { HeaderComponent } from '../shared/header/header.component';
import { FooterComponent } from '../shared/footer/footer.component';
import { TransacoesService, ResumoFinanceiro, DashboardData } from '../../services/transacoes.service';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, HeaderComponent, FooterComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {
      // Modal de cadastro de conta

  showContaModal = false;
  loadingConta = false;
  errorConta: string | null = null;
  novaConta = { nome: '', saldo_inicial: 0 };

  openContaModal() {
    if (!isPlatformBrowser(this.platformId)) return;
    this.showContaModal = true;
    this.errorConta = null;
    this.novaConta = { nome: '', saldo_inicial: 0 };
  }

  closeContaModal() {
    this.showContaModal = false;
    this.novaConta = { nome: '', saldo_inicial: 0 };
    this.errorConta = null;
  }

      salvarConta() {
        if (!this.novaConta.nome) {
          this.errorConta = 'Preencha o nome da conta.';
          return;
        }
        this.loadingConta = true;
        this.errorConta = null;
        this.svc.criarConta(this.novaConta).subscribe({
          next: () => {
            this.loadingConta = false;
            this.closeContaModal();
            window.alert('Conta criada com sucesso!');
            if (isPlatformBrowser(this.platformId)) {
              setTimeout(() => { window.location.reload(); }, 1200);
            }
          },
          error: (err) => {
            this.loadingConta = false;
            this.errorConta = err?.error?.detail || 'Erro ao criar conta.';
          }
        });
      }
    liberarIncentivoConclusao(incentivo_id: number) {
      if (!isPlatformBrowser(this.platformId)) return;
      this.loading = true;
      this.error = null;
      this.svc.liberarIncentivoConclusao(incentivo_id).subscribe({
        next: (res: any) => {
          this.loading = false;
          this.carregarResumo();
          window.alert('Incentivo de conclusão liberado com sucesso!');
        },
        error: (err: any) => {
          this.loading = false;
          window.alert(err?.error?.detail || 'Erro ao liberar incentivo de conclusão.');
        }
      });
    }
  private svc = inject(TransacoesService);
  private platformId = inject(PLATFORM_ID);
  private route = inject(ActivatedRoute);


  totalBeneficioRecebido: number = 0;
  loading: boolean = false;
  loadingBeneficio: boolean = true;
  error: string | null = null;
  proximaDisponibilidadeStr: string | null = null;
  disponivelAgora: boolean = false;
  totalEntradas: number = 0;
  totalSaidas: number = 0;
  saldoLiquido: number = 0;
  entradasCategoria: Array<{ categoria__nome: string; total: number }> = [];
  gastosCategoria: Array<{ categoria__nome: string; total: number }> = [];
  transacoesRecentes: Array<{ id: number; data: string; tipo: string; descricao: string; valor: number; categoria__nome: string; pago: boolean }> = [];
  incentivosConclusao: Array<{ id: number; ano: number; valor: number; liberado: boolean; criado_em: string }> = [];
  incentivosEnem: Array<{ id: number; ano: number; valor: number; liberado: boolean; criado_em: string }> = [];
  anoConclusao: number | null = null;
  contaIdConclusao: number | null = null;
  anoEnem: number | null = null;
  contaIdEnem: number | null = null;

  ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;
    this.route.data.subscribe(({ dashboard }) => {
      const dash = dashboard as DashboardData | null;
      if (dash) {
        this.totalEntradas = Number(dash?.resumo?.total_entradas || 0);
        this.totalSaidas = Number(dash?.resumo?.total_saidas || 0);
        this.saldoLiquido = Number(dash?.resumo?.saldo_liquido || 0);
        this.totalBeneficioRecebido = Number(dash?.resumo?.pede_meia_recebido || 0);
        this.loadingBeneficio = false;
        this.entradasCategoria = (dash?.graficos?.entradas_categoria || []).map((x: any) => ({
          categoria__nome: x.categoria__nome,
          total: Number(x.total || 0)
        }));
        this.gastosCategoria = (dash?.graficos?.gastos_categoria || []).map((x: any) => ({
          categoria__nome: x.categoria__nome,
          total: Number(x.total || 0)
        }));
        this.transacoesRecentes = (dash?.transacoes_recentes || [])
          .slice(0, 3)
          .map((t: any) => ({
            id: t.id,
            data: typeof t.data === 'string' && t.data.length === 10 ? `${t.data}T00:00:00` : t.data,
            tipo: t.tipo,
            descricao: t.descricao,
            valor: Number(t.valor || 0),
            categoria__nome: t.categoria__nome,
            pago: !!t.pago,
          }));
        this.incentivosConclusao = dash?.incentivos?.conclusao || [];
        this.incentivosEnem = dash?.incentivos?.enem || [];
      }
      this.carregarResumo();
    });
  }


  carregarResumo() {
    // Implemente aqui a lógica para atualizar o dashboard, se necessário.
    // Se não for necessário, deixe vazio para evitar erro de compilação.
  }

  confirmarParcelaMesAtual() {
    if (!isPlatformBrowser(this.platformId)) return;
    this.loading = true;
    this.error = null;
    // Criar parcela pendente e confirmar no mesmo fluxo
    const agora = new Date();
    const mes = Number(agora.getMonth() + 1);
    const ano = Number(agora.getFullYear());
    const valor = 200; // valor fixo da parcela mensal
    this.svc.criarParcelaPedeMeia(mes, ano, valor, undefined, 'Pé de Meia').subscribe({
      next: () => {
        this.svc.confirmarRecebimento({ mes, ano }).subscribe({
          next: () => {
            this.carregarResumo();
            window.alert('Parcela mensal criada e confirmada com sucesso!');
            window.location.reload();
          },
          error: (err) => {
            this.loading = false;
            const msg = err?.error?.detail || err?.message || 'Erro ao confirmar parcela mensal.';
            window.alert(msg);
          }
        });
      },
      error: (err) => {
        this.loading = false;
        const msg = (err?.error && (err.error.detail || err.error.message)) || err?.message || 'Erro ao criar parcela mensal.';
        window.alert(msg);
      }
    });
  }

  criarELiberarIncentivoConclusao() {
    if (!isPlatformBrowser(this.platformId)) return;
    this.loading = true;
    this.error = null;
      // Chama apenas as APIs de conclusão, enviando só o necessário
    this.svc.criarIncentivoConclusao(this.contaIdConclusao ?? undefined).subscribe({
      next: (res: any) => {
        const incentivoId = res.id;
        this.svc.liberarIncentivoConclusao(incentivoId).subscribe({
          next: () => {
            this.loading = false;
            this.carregarResumo();
            window.alert('Incentivo de conclusão criado e liberado com sucesso!');
            window.location.reload();
          },
          error: (err: any) => {
            this.loading = false;
            window.alert(err?.error?.detail || 'Erro ao liberar incentivo de conclusão.');
          }
        });
      },
      error: (err: any) => {
        this.loading = false;
        window.alert(err?.error?.detail || 'Erro ao criar incentivo de conclusão.');
      }
    });
  }

  criarIncentivoEnem() {
    if (!isPlatformBrowser(this.platformId)) return;
    this.loading = true;
    this.error = null;
    const anoAtual = new Date().getFullYear();
    this.svc.criarIncentivoEnem(anoAtual, this.contaIdEnem ?? undefined).subscribe({
      next: () => {
        this.loading = false;
        this.carregarResumo();
        window.alert('Incentivo ENEM criado e liberado com sucesso!');
        window.location.reload();
      },
      error: (err: any) => {
        this.loading = false;
        window.alert(err?.error?.detail || 'Erro ao criar incentivo do ENEM.');
      }
    });
  }
  fecharErro() {
    this.error = null;
  }
}
