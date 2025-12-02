import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { TransacaoService, Transacao } from './transacao.service';
import { CategoriaService } from './categoria.service';
import { ContaService } from './conta.service';

describe('Serviços de API (Transação, Categoria, Conta)', () => {
  let transacaoService: TransacaoService;
  let categoriaService: CategoriaService;
  let contaService: ContaService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [TransacaoService, CategoriaService, ContaService]
    });

    transacaoService = TestBed.inject(TransacaoService);
    categoriaService = TestBed.inject(CategoriaService);
    contaService = TestBed.inject(ContaService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  describe('TransacaoService', () => {
    it('should be created', () => {
      expect(transacaoService).toBeTruthy();
    });

    it('deve listar transações', () => {
      const mockTransacoes: Transacao[] = [
        {
          id: 1,
          tipo: 'saida',
          descricao: 'Almoço',
          valor: 25.50,
          data: '2025-12-01',
          categoria: 1,
          conta: 1
        },
        {
          id: 2,
          tipo: 'entrada',
          descricao: 'Salário',
          valor: 2000.00,
          data: '2025-12-01',
          categoria: 2,
          conta: 1
        }
      ];

      transacaoService.listarTransacoes().subscribe((transacoes) => {
        expect(transacoes.length).toBe(2);
        expect(transacoes).toEqual(mockTransacoes);
      });

      const req = httpMock.expectOne('http://localhost:8000/api/transacoes');
      expect(req.request.method).toBe('GET');
      req.flush(mockTransacoes);
    });

    it('deve criar uma transação', () => {
      const novaTransacao: Transacao = {
        tipo: 'saida',
        descricao: 'Compras',
        valor: 150.00,
        data: '2025-12-01',
        categoria: 1,
        conta: 1
      };

      transacaoService.criarTransacao(novaTransacao).subscribe((transacao) => {
        expect(transacao.descricao).toBe('Compras');
      });

      const req = httpMock.expectOne('http://localhost:8000/api/transacoes');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(novaTransacao);
      req.flush({ id: 3, ...novaTransacao });
    });
  });

  describe('CategoriaService', () => {
    it('should be created', () => {
      expect(categoriaService).toBeTruthy();
    });

    it('deve listar categorias', () => {
      const mockCategorias = [
        { id: 1, nome: 'Alimentação', tipo_categoria: 'saida' },
        { id: 2, nome: 'Transporte', tipo_categoria: 'saida' }
      ];

      categoriaService.listarCategorias().subscribe((categorias) => {
        expect(categorias.length).toBe(2);
        expect(categorias[0].nome).toBe('Alimentação');
      });

      const req = httpMock.expectOne('http://localhost:8000/api/categorias');
      expect(req.request.method).toBe('GET');
      req.flush(mockCategorias);
    });

    it('deve criar uma categoria', () => {
      const novaCategoria = { nome: 'Saúde', tipo_categoria: 'saida' as const };

      categoriaService.criarCategoria(novaCategoria).subscribe((categoria) => {
        expect(categoria.nome).toBe('Saúde');
      });

      const req = httpMock.expectOne('http://localhost:8000/api/categorias');
      expect(req.request.method).toBe('POST');
      req.flush({ id: 3, ...novaCategoria });
    });
  });

  describe('ContaService', () => {
    it('should be created', () => {
      expect(contaService).toBeTruthy();
    });

    it('deve listar contas', () => {
      const mockContas = [
        { id: 1, nome: 'Conta Corrente', saldo_inicial: 1000.00, saldo_atual: 1500.00 },
        { id: 2, nome: 'Conta Poupança', saldo_inicial: 5000.00, saldo_atual: 5250.00 }
      ];

      contaService.listarContas().subscribe((contas) => {
        expect(contas.length).toBe(2);
        expect(contas[0].nome).toBe('Conta Corrente');
      });

      const req = httpMock.expectOne('http://localhost:8000/api/contas');
      expect(req.request.method).toBe('GET');
      req.flush(mockContas);
    });

    it('deve criar uma conta', () => {
      const novaConta = { nome: 'Conta Investimento', saldo_inicial: 10000.00 };

      contaService.criarConta(novaConta).subscribe((conta) => {
        expect(conta.nome).toBe('Conta Investimento');
      });

      const req = httpMock.expectOne('http://localhost:8000/api/contas');
      expect(req.request.method).toBe('POST');
      req.flush({ id: 3, ...novaConta });
    });
  });
});
