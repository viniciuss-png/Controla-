import { inject } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { PLATFORM_ID } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { of } from 'rxjs';
import { TransacoesService, DashboardData } from './transacoes.service';

export const dashboardResolver: ResolveFn<DashboardData | null> = () => {
  const platformId = inject(PLATFORM_ID);
  const svc = inject(TransacoesService);
  if (!isPlatformBrowser(platformId)) {
    return of(null);
  }
  const token = localStorage.getItem('access_token');
  if (!token) {
    return of(null);
  }
  return svc.getDashboardData();
};
