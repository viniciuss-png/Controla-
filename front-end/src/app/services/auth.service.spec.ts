import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuthService } from './auth.service';
import { RegistroCadastro, RespostaCadastro } from '../models/usuario';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('cadastrarUsuario', () => {
    it('deve enviar dados de cadastro e retornar resposta de sucesso', () => {
      const dadosCadastro: RegistroCadastro = {
        nome: 'João Silva',
        email: 'joao@example.com',
        senha: 'Senha123',
        anoEscolar: 1
      };

      const respostaMock: RespostaCadastro = {
        sucesso: true,
        mensagem: 'Cadastro realizado com sucesso!',
        dados: {
          id: '123',
          nome: 'João Silva',
          email: 'joao@example.com',
          anoEscolar: 1,
          dataCriacao: new Date().toISOString()
        }
      };

      service.cadastrarUsuario(dadosCadastro).subscribe(resposta => {
        expect(resposta.sucesso).toBe(true);
        expect(resposta.dados?.email).toBe('joao@example.com');
      });

      const req = httpMock.expectOne('http://localhost:8000/api/register/');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(dadosCadastro);

      req.flush(respostaMock);
    });

    it('deve tratar erro de email duplicado', () => {
      const dadosCadastro: RegistroCadastro = {
        nome: 'João Silva',
        email: 'joao@example.com',
        senha: 'Senha123',
        anoEscolar: 1
      };

      const erroMock = {
        codigo: 'EMAIL_DUPLICADO',
        mensagem: 'Email já cadastrado'
      };

      service.cadastrarUsuario(dadosCadastro).subscribe(
        () => {
          throw new Error('deveria ter falhado');
        },
        (erro) => {
          expect(erro.codigo).toBe('EMAIL_DUPLICADO');
        }
      );

      const req = httpMock.expectOne('http://localhost:8000/api/register/');
      req.flush(erroMock, { status: 400, statusText: 'Bad Request' });
    });
  });
});
