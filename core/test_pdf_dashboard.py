import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import Conta, Categoria, Transacao, MetaFinanceira, Incentivo
from .services import gerar_relatorio_financeiro_pdf, obter_dados_dashboard


@pytest.mark.django_db
class TestRelatorioFinanceiroPDF:
    
    def test_gerar_pdf_sem_filtro_de_data(self):
        user = User.objects.create_user(username='testuser', password='pass123', email='test@test.com')
        conta = Conta.objects.create(usuario=user, nome='Conta Principal', saldo_inicial=1000, saldo_atual=1000)
        categoria = Categoria.objects.create(usuario=user, nome='Alimentação', tipo_categoria='saida')
        
        Transacao.objects.create(
            usuario=user,
            conta=conta,
            categoria=categoria,
            tipo='saida',
            valor=Decimal('50.00'),
            descricao='Compras',
            pago=True,
            data=timezone.localdate()
        )
        
        pdf_buffer = gerar_relatorio_financeiro_pdf(user)
        
        assert pdf_buffer is not None
        assert pdf_buffer.getbuffer().nbytes > 0
    
    def test_gerar_pdf_com_filtro_de_data(self):
        user = User.objects.create_user(username='testuser2', password='pass123', email='test2@test.com')
        conta = Conta.objects.create(usuario=user, nome='Conta Principal', saldo_inicial=1000, saldo_atual=1000)
        categoria = Categoria.objects.create(usuario=user, nome='Alimentação', tipo_categoria='saida')
        
        hoje = timezone.localdate()
        semana_passada = hoje - timedelta(days=7)
        
        Transacao.objects.create(
            usuario=user,
            conta=conta,
            categoria=categoria,
            tipo='saida',
            valor=Decimal('50.00'),
            descricao='Compras',
            pago=True,
            data=hoje
        )
        
        pdf_buffer = gerar_relatorio_financeiro_pdf(
            user,
            from_date=semana_passada,
            to_date=hoje
        )
        
        assert pdf_buffer is not None
        assert pdf_buffer.getbuffer().nbytes > 0
    
    def test_pdf_com_multiplas_categorias_e_contas(self):
        user = User.objects.create_user(username='testuser3', password='pass123', email='test3@test.com')
        
        conta1 = Conta.objects.create(usuario=user, nome='Corrente', saldo_inicial=1000, saldo_atual=500)
        conta2 = Conta.objects.create(usuario=user, nome='Poupança', saldo_inicial=5000, saldo_atual=5500)
        cat_alimentacao = Categoria.objects.create(usuario=user, nome='Alimentação', tipo_categoria='saida')
        cat_transporte = Categoria.objects.create(usuario=user, nome='Transporte', tipo_categoria='saida')
        cat_salario = Categoria.objects.create(usuario=user, nome='Salário', tipo_categoria='entrada')
        
        Transacao.objects.create(usuario=user, conta=conta1, categoria=cat_alimentacao, tipo='saida',
                                valor=Decimal('100.00'), descricao='Supermercado', pago=True, data=timezone.localdate())
        Transacao.objects.create(usuario=user, conta=conta1, categoria=cat_transporte, tipo='saida',
                                valor=Decimal('50.00'), descricao='Ônibus', pago=True, data=timezone.localdate())
        Transacao.objects.create(usuario=user, conta=conta2, categoria=cat_salario, tipo='entrada',
                                valor=Decimal('2000.00'), descricao='Salário', pago=True, data=timezone.localdate())
        
        pdf_buffer = gerar_relatorio_financeiro_pdf(user)
        
        assert pdf_buffer is not None
        assert pdf_buffer.getbuffer().nbytes > 0


@pytest.mark.django_db
class TestDashboardData:
    
    def test_obter_dados_dashboard_estrutura(self):
        user = User.objects.create_user(username='dashboard_user', password='pass123', email='dash@test.com')
        conta = Conta.objects.create(usuario=user, nome='Conta Test', saldo_inicial=1000, saldo_atual=800)
        categoria = Categoria.objects.create(usuario=user, nome='Test Cat', tipo_categoria='saida')
        
        Transacao.objects.create(
            usuario=user, conta=conta, categoria=categoria, tipo='saida',
            valor=Decimal('200.00'), descricao='Test', pago=True, data=timezone.localdate()
        )
        
        data = obter_dados_dashboard(user)
        
        assert 'resumo' in data
        assert 'graficos' in data
        assert 'incentivos' in data
        assert 'contas' in data
        assert 'metas' in data
        assert 'transacoes_recentes' in data
        assert 'total_entradas' in data['resumo']
        assert 'total_saidas' in data['resumo']
        assert 'saldo_liquido' in data['resumo']
        assert 'pede_meia_recebido' in data['resumo']
        assert 'pede_meia_pendente' in data['resumo']
        assert 'gastos_categoria' in data['graficos']
        assert 'entradas_categoria' in data['graficos']
        assert 'conclusao' in data['incentivos']
        assert 'enem' in data['incentivos']
    
    def test_dashboard_com_incentivos(self):
        user = User.objects.create_user(username='incentivo_user', password='pass123', email='inc@test.com')
        conta = Conta.objects.create(usuario=user, nome='Conta Incentivos', saldo_inicial=0, saldo_atual=1200)
        
        Incentivo.objects.create(
            usuario=user, tipo='conclusao', ano=2024, valor=Decimal('1000.00'),
            conta=conta, liberado=True
        )
        Incentivo.objects.create(
            usuario=user, tipo='enem', ano=2024, valor=Decimal('200.00'),
            conta=conta, liberado=True
        )
        
        data = obter_dados_dashboard(user)
        
        assert len(data['incentivos']['conclusao']) == 1
        assert len(data['incentivos']['enem']) == 1
        assert data['incentivos']['conclusao'][0]['liberado'] == True
        assert data['incentivos']['enem'][0]['valor'] == 200.0
    
    def test_dashboard_com_filtro_de_data(self):
        user = User.objects.create_user(username='data_user', password='pass123', email='data@test.com')
        conta = Conta.objects.create(usuario=user, nome='Conta Data', saldo_inicial=1000, saldo_atual=500)
        categoria = Categoria.objects.create(usuario=user, nome='Cat Data', tipo_categoria='saida')
        
        hoje = timezone.localdate()
        semana_passada = hoje - timedelta(days=7)
        mes_passado = hoje - timedelta(days=30)
        
        Transacao.objects.create(
            usuario=user, conta=conta, categoria=categoria, tipo='saida',
            valor=Decimal('100.00'), descricao='Antiga', pago=True, data=mes_passado
        )
        
        Transacao.objects.create(
            usuario=user, conta=conta, categoria=categoria, tipo='saida',
            valor=Decimal('200.00'), descricao='Recente', pago=True, data=hoje
        )
        
        data_filtrada = obter_dados_dashboard(user, from_date=semana_passada, to_date=hoje)
        
        assert data_filtrada['resumo']['total_saidas'] == 200.0
    
    def test_dashboard_com_metas_financeiras(self):
        user = User.objects.create_user(username='meta_user', password='pass123', email='meta@test.com')
        conta = Conta.objects.create(usuario=user, nome='Conta Meta', saldo_inicial=1000, saldo_atual=1500)
        
        MetaFinanceira.objects.create(
            usuario=user,
            nome='Meta de Férias',
            valor_alvo=Decimal('5000.00'),
            conta_vinculada=conta,
            data_alvo=timezone.localdate() + timedelta(days=180),
            ativa=True
        )
        
        data = obter_dados_dashboard(user)
        
        assert len(data['metas']) >= 1
        assert data['metas'][0]['valor_alvo'] == 5000.0
    
    def test_dashboard_conversao_decimals_para_float(self):
        user = User.objects.create_user(username='decimal_user', password='pass123', email='dec@test.com')
        conta = Conta.objects.create(usuario=user, nome='Conta Decimal', saldo_inicial=1000.50, saldo_atual=1500.75)
        
        data = obter_dados_dashboard(user)
        
        assert isinstance(data['resumo']['total_entradas'], (int, float))
        assert isinstance(data['resumo']['total_saidas'], (int, float))
        assert isinstance(data['resumo']['saldo_liquido'], (int, float))
        
        for conta_data in data['contas']:
            assert isinstance(conta_data['saldo_inicial'], (int, float))
            assert isinstance(conta_data['saldo_atual'], (int, float))
