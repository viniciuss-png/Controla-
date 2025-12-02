import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router, ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { ErroAPI } from '../models/usuario';

@Component({
  selector: 'app-entrar',
  standalone: true,
  templateUrl: './entrar.component.html',
  styleUrls: ['./entrar.component.css'],
  imports: [CommonModule, FormsModule, RouterModule]
})
export class EntrarComponent implements OnInit, OnDestroy {
  /**
   * Dados do formulário de login
   */
  email: string = '';
  senha: string = '';

  /**
   * Indica se o formulário está sendo enviado
   */
  enviando: boolean = false;

  /**
   * Mensagem de sucesso a ser exibida
   */
  mensagemSucesso: string = '';

  /**
   * Mensagem de erro a ser exibida
   */
  mensagemErro: string = '';

  /**
   * Subject para gerenciar observables e evitar memory leaks
   */
  private destroy$ = new Subject<void>();
  private timeoutLimpeza: any;

  /**
   * URL para retornar após login (se fornecida)
   */
  private returnUrl: string = '/dashboard';

  constructor(
    private authService: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    // Obter URL de retorno dos query params
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';

    // Se já estiver autenticado, redirecionar
    if (this.authService.estaAutenticado()) {
      this.router.navigate([this.returnUrl]);
    }
  }

  /**
   * Envia o formulário de login
   */
  enviarFormulario(): void {
    // Limpar mensagens anteriores
    this.mensagemSucesso = '';
    this.mensagemErro = '';

    // Validar campos
    if (!this.email.trim() || !this.senha.trim()) {
      this.mensagemErro = 'Por favor, preencha email e senha';
      this.agendarLimpezaMensagens();
      return;
    }

    // Enviar login
    this.realizarLogin();
  }

  /**
   * Realiza o login na API
   */
  private realizarLogin(): void {
    this.enviando = true;

    this.authService.login(this.email.trim().toLowerCase(), this.senha)
      .pipe(
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (resposta) => {
          this.enviando = false;

          if (resposta?.access) {
            this.mensagemSucesso = 'Login realizado com sucesso! Redirecionando...';
            this.agendarLimpezaMensagens();

            // Limpar formulário
            this.email = '';
            this.senha = '';

            // Redirecionar para dashboard após 1 segundo
            setTimeout(() => {
              this.router.navigate([this.returnUrl]);
            }, 1000);
          } else {
            this.mensagemErro = 'Erro ao fazer login. Tente novamente.';
            this.agendarLimpezaMensagens();
          }
        },
        error: (erro: ErroAPI) => {
          this.enviando = false;
          
          // Tratar erro específico de credenciais
          if (erro.codigo === 'ERRO_SERVIDOR' && erro.detalhes?.detail?.includes('No active account')) {
            this.mensagemErro = 'Email ou senha inválidos';
          } else {
            this.mensagemErro = erro.mensagem || 'Erro ao conectar com o servidor';
          }
          
          this.agendarLimpezaMensagens();
          console.error('Erro no login:', erro);
        }
      });
  }

  /**
   * Limpa as mensagens após 5 segundos
   */
  private agendarLimpezaMensagens(): void {
    // Cancelar timeout anterior se existir
    if (this.timeoutLimpeza) {
      clearTimeout(this.timeoutLimpeza);
    }

    // Agendar limpeza de mensagens após 5 segundos
    this.timeoutLimpeza = setTimeout(() => {
      this.mensagemSucesso = '';
      this.mensagemErro = '';
    }, 5000);
  }

  ngOnDestroy(): void {
    // Limpar timeout se existir
    if (this.timeoutLimpeza) {
      clearTimeout(this.timeoutLimpeza);
    }
    this.destroy$.next();
    this.destroy$.complete();
  }
}

