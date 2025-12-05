import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { catchError, switchMap, throwError } from 'rxjs';

const API_BASE = 'http://localhost:8000/api';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const platformId = inject(PLATFORM_ID);
  const token = isPlatformBrowser(platformId) ? localStorage.getItem('access_token') : null;
  const http = inject(HttpClient);

  const authReq = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authReq).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401) {
        const refresh = isPlatformBrowser(platformId) ? localStorage.getItem('refresh_token') : null;
        if (!refresh) {
          return throwError(() => err);
        }
        // tenta renovar e repetir a requisição original
        return http.post<{ access: string }>(`${API_BASE}/token/refresh/`, { refresh }).pipe(
          switchMap(({ access }) => {
            if (isPlatformBrowser(platformId)) {
              localStorage.setItem('access_token', access);
            }
            const retried = req.clone({ setHeaders: { Authorization: `Bearer ${access}` } });
            return next(retried);
          }),
          catchError((refreshErr) => {
            // refresh falhou: limpa tokens e falha a requisição original
            if (isPlatformBrowser(platformId)) {
              localStorage.removeItem('access_token');
              localStorage.removeItem('refresh_token');
            }
            return throwError(() => refreshErr);
          })
        );
      }
      return throwError(() => err);
    })
  );
};
