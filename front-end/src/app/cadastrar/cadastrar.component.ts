import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { ValidacaoService } from '../services/validacao.service';
import { RegistroCadastro, ErroAPI } from '../models/usuario';

@Component({
  selector: 'app-cadastrar',
  standalone: true,
  templateUrl: './cadastrar.component.html',
  styleUrls: ['./cadastrar.component.css'],
  imports: [CommonModule, ReactiveFormsModule, RouterModule]
})
export class CadastrarComponent implements OnInit, OnDestroy {
  /**
   * FormGroup para o formulário de cadastro com validações reativas
   */
  formularioCadastro: FormGroup;

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
   * Campos do formulário para validação individual
   */
  errosValidacao: {
    [key: string]: string;
  } = {};

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private validacaoService: ValidacaoService,
    private router: Router
  ) {
    this.formularioCadastro = this.criarFormulario();
  }

  ngOnInit(): void {
    // Nenhuma inicialização necessária
  }

  /**
   * Cria o formulário com validações
   */
  private criarFormulario(): FormGroup {
    return this.formBuilder.group({
      anoEscolar: [1, [Validators.required, Validators.min(1), Validators.max(3)]],
      nome: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      senha: ['', [Validators.required, Validators.minLength(6)]],
      confirmarSenha: ['', [Validators.required]]
    }, {
      validators: this.senhasConferemValidator
    });
  }

  /**
   * Validador customizado para verificar se as senhas conferem
   */
  private senhasConferemValidator(group: FormGroup): { [key: string]: any } | null {
    const senha = group.get('senha')?.value;
    const confirmarSenha = group.get('confirmarSenha')?.value;

    if (senha && confirmarSenha && senha !== confirmarSenha) {
      return { senhasNaoConferem: true };
    }

    return null;
  }

  /**
   * Submete o formulário para envio
   */
  enviarFormulario(): void {
    // Limpar mensagens anteriores
    this.mensagemSucesso = '';
    this.mensagemErro = '';
    this.errosValidacao = {};

    // Validar formulário
    if (!this.formularioCadastro.valid) {
      this.validarCamposFormulario();
      this.mensagemErro = 'Por favor, corrija os erros no formulário';
      return;
    }

    // Extrair valores
    const dados = this.formularioCadastro.value;
    const registroCadastro: RegistroCadastro = {
      nome: dados.nome.trim(),
      email: dados.email.trim().toLowerCase(),
      senha: dados.senha,
      anoEscolar: parseInt(dados.anoEscolar, 10)
    };

    // Enviar dados
    this.enviarCadastro(registroCadastro);
  }

  /**
   * Envia os dados de cadastro para a API
   */
  private enviarCadastro(dados: RegistroCadastro): void {
    this.enviando = true;

    this.authService.cadastrarUsuario(dados)
      .pipe(
        takeUntil(this.destroy$)
      )
      .subscribe({
        next: (resposta) => {
          this.enviando = false;

          if (resposta.sucesso) {
            this.mensagemSucesso = resposta.mensagem || 'Cadastro realizado com sucesso!';
            this.agendarLimpezaMensagens();
            
            // Limpar formulário
            this.formularioCadastro.reset({
              anoEscolar: 1,
              nome: '',
              email: '',
              senha: '',
              confirmarSenha: ''
            });

            // Redirecionar para login após 2 segundos
            setTimeout(() => {
              this.router.navigate(['/entrar']);
            }, 2000);
          } else {
            this.mensagemErro = resposta.mensagem || 'Erro ao realizar cadastro';
            this.agendarLimpezaMensagens();
          }
        },
        error: (erro: ErroAPI) => {
          this.enviando = false;
          this.mensagemErro = erro.mensagem || 'Erro ao conectar com o servidor';
          this.agendarLimpezaMensagens();
          console.error('Erro no cadastro:', erro);
        }
      });
  }

  /**
   * Valida cada campo do formulário individualmente
   */
  private validarCamposFormulario(): void {
    const campos = ['nome', 'email', 'senha', 'confirmarSenha', 'anoEscolar'];

    campos.forEach(campo => {
      const controle = this.formularioCadastro.get(campo);

      if (controle && controle.invalid) {
        if (campo === 'nome') {
          const validacao = this.validacaoService.validarNome(controle.value);
          this.errosValidacao[campo] = validacao.erro || 'Nome inválido';
        } else if (campo === 'email') {
          const validacao = this.validacaoService.validarEmail(controle.value);
          this.errosValidacao[campo] = validacao.erro || 'Email inválido';
        } else if (campo === 'senha') {
          const validacao = this.validacaoService.validarSenha(controle.value);
          this.errosValidacao[campo] = validacao.erro || 'Senha inválida';
        } else if (campo === 'confirmarSenha') {
          const validacao = this.validacaoService.validarConfirmacaoSenha(
            this.formularioCadastro.get('senha')?.value,
            controle.value
          );
          this.errosValidacao[campo] = validacao.erro || 'Confirmação de senha inválida';
        } else if (campo === 'anoEscolar') {
          const validacao = this.validacaoService.validarAnoEscolar(controle.value);
          this.errosValidacao[campo] = validacao.erro || 'Ano escolar inválido';
        }
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

  /**
   * Retorna o erro de validação de um campo
   */
  obterErroValidacao(campo: string): string {
    return this.errosValidacao[campo] || '';
  }

  /**
   * Verifica se um campo tem erro
   */
  temErroValidacao(campo: string): boolean {
    return !!this.errosValidacao[campo];
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
