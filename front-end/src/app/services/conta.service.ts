import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ContaPayload {
  nome: string;
  saldo_inicial?: number;
}

@Injectable({ providedIn: 'root' })
export class ContaService {
  private http = inject(HttpClient);
  private baseUrl = 'http://localhost:8000/api/contas/';

  criarConta(payload: ContaPayload): Observable<any> {
    return this.http.post(this.baseUrl, payload);
  }
}
