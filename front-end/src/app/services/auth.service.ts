import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  serie_em: number;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private baseUrl = 'http://localhost:8000/api';

  register(payload: RegisterPayload) {
    return this.http.post(`${this.baseUrl}/register/`, payload);
  }

  login(username: string, password: string) {
    return this.http.post<TokenResponse>(`${this.baseUrl}/token/`, { username, password });
  }
}
