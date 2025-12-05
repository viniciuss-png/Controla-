import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HeaderComponent } from '../shared/header/header.component';
import { FooterComponent } from '../shared/footer/footer.component';
import { FormsModule } from '@angular/forms';
import { TransacoesService, Categoria, Conta } from '../../services/transacoes.service';
import { PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-gastos-fixos',
  standalone: true,
  imports: [CommonModule, RouterModule, HeaderComponent, FooterComponent, FormsModule],
  templateUrl: './gastos-fixos.component.html',
  styleUrls: ['./gastos-fixos.component.scss']
})
export class GastosFixosComponent {
  private svc = inject(TransacoesService);
  private platformId = inject(PLATFORM_ID);

  showNovoGastoModal = false;
  loading = false;
  error: string | null = null;

  categorias: Categoria[] = [];
  contas: Conta[] = [];

  novoGasto = {
    descricao: '',
    valor: 0,
    dia_vencimento: 1,
    categoria: 0,
    conta: 0,
  };

  openNovoGastoFixo() {
    this.error = null;
    this.showNovoGastoModal = true;
    this.loading = true;
    // Carregar selects aproveitando serviço de transações
    this.svc.listarCategorias().subscribe({ next: (cats) => this.categorias = cats });
    this.svc.listarContas().subscribe({ next: (cts) => this.contas = cts, complete: () => this.loading = false });
  }

  closeNovoGastoFixo() {
    this.showNovoGastoModal = false;
    this.novoGasto = { descricao: '', valor: 0, dia_vencimento: 1, categoria: 0, conta: 0 };
  }

  salvarGastoFixo() {
    this.error = null;
    if (!this.novoGasto.descricao || !this.novoGasto.valor || !this.novoGasto.dia_vencimento || !this.novoGasto.categoria || !this.novoGasto.conta) {
      this.error = 'Preencha todos os campos obrigatórios.';
      return;
    }
    // TODO: Integrar com endpoint de gastos fixos (backend)
    this.loading = true;
    // Simular sucesso e recarregar igual transações
    setTimeout(() => {
      this.loading = false;
      this.showNovoGastoModal = false;
      if (isPlatformBrowser(this.platformId)) {
        setTimeout(() => window.location.reload(), 800);
      }
    }, 600);
  }
}
