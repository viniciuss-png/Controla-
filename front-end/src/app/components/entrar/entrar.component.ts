import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransacoesService } from '../../services/transacoes.service';
import { Router, RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-entrar',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './entrar.component.html',
  styleUrls: ['./entrar.component.scss']
})
export class EntrarComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);
  private transacoes = inject(TransacoesService);

  loading = false;
  errorMsg = '';
  showContaOverlay = false;

  form = this.fb.group({
    username: ['', [Validators.required]],
    password: ['', [Validators.required]]
  });

  submit() {
    this.errorMsg = '';
    if (this.form.invalid) {
      window.alert('Informe usuário e senha válidos.');
      return;
    }
    this.loading = true;
    const { username, password } = this.form.value as { username: string; password: string };
    this.auth.login(username, password).subscribe({
      next: (tokens) => {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        this.loading = false;
        window.alert('Login realizado com sucesso!');
        this.router.navigateByUrl('/dashboard');
      },
      error: (err) => {
        const msg = err?.error?.detail || 'Credenciais inválidas.';
        window.alert(msg);
        this.loading = false;
      }
    });
  }

  onContaCadastrada(formValue: { nome: string }) {
    this.transacoes.criarConta({ nome: formValue.nome }).subscribe({
      next: () => {
        this.showContaOverlay = false;
        window.alert('Conta cadastrada com sucesso!');
        this.router.navigateByUrl('/dashboard');
      },
      error: () => {
        window.alert('Erro ao cadastrar conta.');
      }
    });
  }
}
