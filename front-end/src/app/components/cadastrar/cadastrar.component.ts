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

  form = this.fb.group({
    username: ['', [Validators.required, Validators.minLength(3)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
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
      this.errorMsg = this.form.errors?.['passwordMismatch']
        ? 'As senhas não conferem.'
        : 'Preencha os campos corretamente.';
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
        setTimeout(() => this.router.navigateByUrl('/entrar'), 1200);
      },
      error: (err) => {
        this.errorMsg = err?.error?.detail || 'Falha ao cadastrar.';
        this.loading = false;
      }
    });
  }
}
