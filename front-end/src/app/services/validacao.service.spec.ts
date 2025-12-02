import { TestBed } from '@angular/core/testing';
import { ValidacaoService, ResultadoValidacao } from './validacao.service';

describe('ValidacaoService', () => {
  let service: ValidacaoService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ValidacaoService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('validarEmail', () => {
    it('deve validar email correto', () => {
      const resultado = service.validarEmail('joao@example.com');
      expect(resultado.valido).toBe(true);
    });

    it('deve rejeitar email sem @', () => {
      const resultado = service.validarEmail('joaoemail.com');
      expect(resultado.valido).toBe(false);
    });

    it('deve rejeitar email vazio', () => {
      const resultado = service.validarEmail('');
      expect(resultado.valido).toBe(false);
    });
  });

  describe('validarNome', () => {
    it('deve validar nome com 3 ou mais caracteres', () => {
      const resultado = service.validarNome('João Silva');
      expect(resultado.valido).toBe(true);
    });

    it('deve rejeitar nome com menos de 3 caracteres', () => {
      const resultado = service.validarNome('Jo');
      expect(resultado.valido).toBe(false);
    });

    it('deve rejeitar nome vazio', () => {
      const resultado = service.validarNome('');
      expect(resultado.valido).toBe(false);
    });

    it('deve rejeitar nome com números', () => {
      const resultado = service.validarNome('João123');
      expect(resultado.valido).toBe(false);
    });
  });

  describe('validarSenha', () => {
    it('deve validar senha com letras maiúsculas, minúsculas e números', () => {
      const resultado = service.validarSenha('Senha123');
      expect(resultado.valido).toBe(true);
    });

    it('deve rejeitar senha com menos de 6 caracteres', () => {
      const resultado = service.validarSenha('Abc12');
      expect(resultado.valido).toBe(false);
    });

    it('deve rejeitar senha sem maiúscula', () => {
      const resultado = service.validarSenha('senha123');
      expect(resultado.valido).toBe(false);
    });

    it('deve rejeitar senha sem minúscula', () => {
      const resultado = service.validarSenha('SENHA123');
      expect(resultado.valido).toBe(false);
    });

    it('deve rejeitar senha sem número', () => {
      const resultado = service.validarSenha('SenhaAbc');
      expect(resultado.valido).toBe(false);
    });
  });

  describe('validarConfirmacaoSenha', () => {
    it('deve validar senhas iguais', () => {
      const resultado = service.validarConfirmacaoSenha('Senha123', 'Senha123');
      expect(resultado.valido).toBe(true);
    });

    it('deve rejeitar senhas diferentes', () => {
      const resultado = service.validarConfirmacaoSenha('Senha123', 'Senha456');
      expect(resultado.valido).toBe(false);
    });
  });

  describe('validarAnoEscolar', () => {
    it('deve validar ano escolar 1', () => {
      expect(service.validarAnoEscolar(1).valido).toBe(true);
    });

    it('deve validar ano escolar 2', () => {
      expect(service.validarAnoEscolar(2).valido).toBe(true);
    });

    it('deve validar ano escolar 3', () => {
      expect(service.validarAnoEscolar(3).valido).toBe(true);
    });

    it('deve rejeitar ano escolar 4', () => {
      expect(service.validarAnoEscolar(4).valido).toBe(false);
    });

    it('deve rejeitar ano escolar 0', () => {
      expect(service.validarAnoEscolar(0).valido).toBe(false);
    });
  });
});
