import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-cadastrar',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './cadastrar.component.html',
  styleUrls: ['./cadastrar.component.scss']
})
export class CadastrarComponent {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);

  loading = false;
  errorMsg = '';
  successMsg = '';

  private showAlert(type: 'erro' | 'sucesso', msg: string) {
    if (msg) {
      window.alert(msg);
      if (type === 'erro') this.errorMsg = '';
      if (type === 'sucesso') this.successMsg = '';
    }
  }

  form = this.fb.group({
    username: ['', [Validators.required]],
    email: ['', [Validators.required]],
    password: ['', [Validators.required]],
    confirmPassword: ['', [Validators.required]],
    serie_em: [1, [Validators.required]]
  }, { validators: this.passwordsMatchValidator });

  private passwordsMatchValidator(group: AbstractControl): ValidationErrors | null {
    const password = group.get('password')?.value;
    const confirm = group.get('confirmPassword')?.value;
    if (password && confirm && password !== confirm) {
      return { passwordMismatch: true };
    }
    return null;
  }

  submit() {
    this.errorMsg = '';
    this.successMsg = '';
    if (this.form.invalid) {
      const msg = this.form.errors?.['passwordMismatch']
        ? 'As senhas não conferem.'
        : 'Preencha os campos corretamente.';
      this.errorMsg = msg;
      this.showAlert('erro', msg);
      return;
    }
    this.loading = true;
    const payload = this.form.value as any;
    // Remover o campo de confirmação antes de enviar
    delete payload.confirmPassword;
    this.auth.register(payload).subscribe({
      next: () => {
        this.successMsg = 'Cadastro realizado com sucesso!';
        this.loading = false;
        this.showAlert('sucesso', this.successMsg);
        setTimeout(() => this.router.navigateByUrl('/entrar'), 1200);
      },
      error: (err) => {
        let msg = 'Falha ao cadastrar.';
        if (err?.error) {
          if (typeof err.error === 'string') {
            msg = err.error;
          } else if (err.error.detail) {
            msg = err.error.detail;
          } else if (err.error.message) {
            msg = err.error.message;
          } else {
            try {
              msg = JSON.stringify(err.error);
            } catch {}
          }
        }
        this.errorMsg = msg;
        this.loading = false;
        this.showAlert('erro', msg);
      }
    });
  }
}
