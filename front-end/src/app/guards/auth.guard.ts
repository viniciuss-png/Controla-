import { Injectable } from '@angular/core';
import { Router, CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { API_CONFIG } from '../config/api.config';

/**
 * Guard que verifica se o usuário está autenticado
 * Se não estiver, redireciona para a página de login
 */
@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private authService: AuthService, private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): boolean {
    const token = localStorage.getItem(API_CONFIG.armazenamento.tokenKey);

    if (token) {
      // Usuário autenticado - permitir acesso
      return true;
    }

    // Sem token - redirecionar para login
    console.warn('Acesso negado: usuário não autenticado');
    this.router.navigate(['/entrar'], { queryParams: { returnUrl: state.url } });
    return false;
  }
}
