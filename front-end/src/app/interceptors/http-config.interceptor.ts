import { Injectable, Injector } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';
import { catchError, filter, take, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

/**
 * Interceptor HTTP que realiza tratamento centralizado de requisições e erros
 * Adiciona headers padrão, gerencia tokens JWT e trata erros de forma consistente
 */
@Injectable()
export class HttpConfigInterceptor implements HttpInterceptor {
  // Flag para controlar refresh de token simultâneos
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<any> = new BehaviorSubject<any>(null);

  constructor(private injector: Injector) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Adicionar header de Content-Type se não existir
    if (!request.headers.has('Content-Type')) {
      request = request.clone({
        setHeaders: {
          'Content-Type': 'application/json'
        }
      });
    }

    // Adicionar token de autenticação se existir no localStorage
    const token = localStorage.getItem('auth_token');
    // Não anexar token nas rotas de obtenção de token/registro
    const urlLower = request.url.toLowerCase();
    const isAuthEndpoint = urlLower.includes('/api/token') || 
                          urlLower.includes('/api/register') || 
                          urlLower.includes('/token') || 
                          urlLower.includes('/register');
    if (token && !isAuthEndpoint) {
      request = request.clone({
        setHeaders: {
          'Authorization': `Bearer ${token}`
        }
      });
    }

    return next.handle(request).pipe(
      catchError((erro: HttpErrorResponse) => {
        // Tratamento centralizado de erros HTTP
        console.error('Erro HTTP:', erro);

        if (erro.status === 401) {
          // Erro de autenticação - tentar renovar token
          return this.handle401Error(request, next);
        } else if (erro.status === 403) {
          console.error('Acesso proibido');
        } else if (erro.status >= 500) {
          console.error('Erro interno do servidor');
        }

        return throwError(() => erro);
      })
    );
  }

  /**
   * Trata erro 401 tentando renovar o token
   */
  private handle401Error(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      this.refreshTokenSubject.next(null);

      // Obter AuthService via Injector (evita dependência circular)
      const authService = this.injector.get(AuthService);

      return authService.renovarToken().pipe(
        switchMap((response: any) => {
          this.isRefreshing = false;
          this.refreshTokenSubject.next(response.access);

          // Repetir a requisição original com novo token
          const newToken = localStorage.getItem('auth_token');
          const newRequest = request.clone({
            setHeaders: {
              'Authorization': `Bearer ${newToken}`
            }
          });
          return next.handle(newRequest);
        }),
        catchError((err) => {
          this.isRefreshing = false;
          // Falha ao renovar - fazer logout
          localStorage.removeItem('auth_token');
          localStorage.removeItem('refresh_token');
          console.error('Falha ao renovar token - usuário desconectado');
          return throwError(() => err);
        })
      );
    } else {
      // Aguardar renovação de token estar completa
      return this.refreshTokenSubject.pipe(
        filter(token => token != null),
        take(1),
        switchMap(() => {
          const newToken = localStorage.getItem('auth_token');
          const newRequest = request.clone({
            setHeaders: {
              'Authorization': `Bearer ${newToken}`
            }
          });
          return next.handle(newRequest);
        })
      );
    }
  }
}
