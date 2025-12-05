import { inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { of } from 'rxjs';
import { TransacoesService, TransacaoItem } from './transacoes.service';

export const transacoesResolver: ResolveFn<TransacaoItem[]> = () => {
  const platformId = inject(PLATFORM_ID);
  const svc = inject(TransacoesService);
  if (!isPlatformBrowser(platformId)) {
    return of([]);
  }
  const token = localStorage.getItem('access_token');
  if (!token) {
    return of([]);
  }
  return svc.listarTransacoes();
};
