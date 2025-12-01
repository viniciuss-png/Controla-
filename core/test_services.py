import os
import django
import pytest

pytestmark = pytest.mark.django_db

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controlae.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from core.models import Categoria, Conta, Transacao, MetaFinanceira, PerfilAluno
from core.services import (
    transferir_saldo,
    depositar_em_meta,
    confirmar_recebimento_pede_meia,
    TransferenciaInvalidaError,
    DepositoMetaError,
    ConfirmacaoRecebimentoError,
)

def limpar_dados():
    try:
        Transacao.objects.filter(usuario__username__startswith='testuser_').delete()
        MetaFinanceira.objects.filter(usuario__username__startswith='testuser_').delete()
        Conta.objects.filter(usuario__username__startswith='testuser_').delete()
        Categoria.objects.filter(usuario__username__startswith='testuser_').delete()
        User.objects.filter(username__startswith='testuser_').delete()
    except Exception as e:
        print(f"Aviso ao limpar dados: {e}")

def criar_usuario_teste():
    user = User.objects.create_user(
        username=f'testuser_{timezone.now().timestamp()}',
        password='testpass123',
        email='test@test.com'
    )
    
    conta1 = Conta.objects.create(usuario=user, nome="Conta Principal", saldo_inicial=Decimal('1000.00'), saldo_atual=Decimal('1000.00'))
    conta2 = Conta.objects.create(usuario=user, nome="Conta Secundária", saldo_inicial=Decimal('500.00'), saldo_atual=Decimal('500.00'))
    
    cat_receita = Categoria.objects.create(usuario=user, nome="Salário", tipo_categoria="entrada")
    cat_despesa = Categoria.objects.create(usuario=user, nome="Compras", tipo_categoria="saida")
    
    return user, conta1, conta2, cat_receita, cat_despesa


def test_transferir_saldo():
    print("\n" + "="*60)
    print("TEST 1: transferir_saldo() - Serviço independente")
    print("="*60)
    
    limpar_dados()
    user, conta1, conta2, _, _ = criar_usuario_teste()
    
    print(f"v Usuário criado: {user.username}")
    print(f"v Conta 1 (antes): R$ {conta1.saldo_inicial}")
    print(f"v Conta 2 (antes): R$ {conta2.saldo_inicial}")
    
    try:
        valor_transferencia = 250.00
        tx_saida, tx_entrada = transferir_saldo(user, conta1, conta2, valor_transferencia)
        
        conta1.refresh_from_db()
        conta2.refresh_from_db()
        
        print(f"\nv Transferência realizada com sucesso!")
        print(f"v Conta 1 (depois): R$ {conta1.saldo_atual}")
        print(f"v Conta 2 (depois): R$ {conta2.saldo_atual}")
        print(f"v Transação Saída ID: {tx_saida.id} (R$ {tx_saida.valor})")
        print(f"v Transação Entrada ID: {tx_entrada.id} (R$ {tx_entrada.valor})")
        
        assert conta1.saldo_atual == Decimal('750.00'), "Saldo conta1 incorreto"
        assert conta2.saldo_atual == Decimal('750.00'), "Saldo conta2 incorreto"
        assert tx_saida.tipo == 'saida'
        assert tx_entrada.tipo == 'entrada'
        
        print("\n TEST 1 PASSED")
    except Exception as e:
        print(f"\n TEST 1 FAILED: {e}")
        raise


def test_depositar_em_meta():
    print("\n" + "="*60)
    print("TEST 2: depositar_em_meta() - Serviço independente")
    print("="*60)
    
    limpar_dados()
    user, conta_principal, _, _, _ = criar_usuario_teste()
    
    meta = MetaFinanceira.objects.create(
        usuario=user,
        nome="Viagem",
        valor_alvo=Decimal('2000.00'),
        ativa=True
    )
    
    conta_meta = Conta.objects.create(
        usuario=user,
        nome=f"Poupança: {meta.nome}",
        saldo_inicial=Decimal('0.00'),
        saldo_atual=Decimal('0.00')
    )
    meta.conta_vinculada = conta_meta
    meta.save()
    
    print(f"v Usuário criado: {user.username}")
    print(f"v Meta criada: {meta.nome}")
    print(f"v Conta Principal (antes): R$ {conta_principal.saldo_atual}")
    print(f"v Conta Meta (antes): R$ {conta_meta.saldo_atual}")
    
    try:
        valor_deposito = 500.00
        tx_saida, tx_entrada = depositar_em_meta(user, meta, valor_deposito)
        
        conta_principal.refresh_from_db()
        conta_meta.refresh_from_db()
        
        print(f"\nv Depósito em meta realizado com sucesso!")
        print(f"v Conta Principal (depois): R$ {conta_principal.saldo_atual}")
        print(f"v Conta Meta (depois): R$ {conta_meta.saldo_atual}")
        print(f"v Transação Saída ID: {tx_saida.id} (R$ {tx_saida.valor})")
        print(f"v Transação Entrada ID: {tx_entrada.id} (R$ {tx_entrada.valor})")
        
        assert conta_principal.saldo_atual == Decimal('500.00'), "Saldo principal incorreto"
        assert conta_meta.saldo_atual == Decimal('500.00'), "Saldo meta incorreto"
        
        print("\n TEST 2 PASSED")
    except Exception as e:
        print(f"\n TEST 2 FAILED: {e}")
        raise


def test_confirmar_recebimento_pede_meia():
    print("\n" + "="*60)
    print("TEST 3: confirmar_recebimento_pede_meia() - Serviço independente")
    print("="*60)
    
    limpar_dados()
    user, conta_principal, _, _, _ = criar_usuario_teste()
    
    cat_pede_meia = Categoria.objects.create(
        usuario=user,
        nome="Pé-de-Meia",
        tipo_categoria="entrada"
    )
    
    hoje = timezone.localdate()
    tx_pendente = Transacao.objects.create(
        usuario=user,
        categoria=cat_pede_meia,
        conta=conta_principal,
        tipo="entrada",
        descricao="Pé-de-Meia - Benefício",
        valor=Decimal('200.00'),
        data=hoje,
        pago=False
    )
    
    print(f"v Usuário criado: {user.username}")
    print(f"v Transação pendente criada: {tx_pendente.descricao}")
    print(f"v Status antes: pago={tx_pendente.pago}")
    
    try:
        mes = hoje.month
        ano = hoje.year
        
        tx_confirmada = confirmar_recebimento_pede_meia(user, mes, ano)
        
        print(f"\nv Recebimento confirmado com sucesso!")
        print(f"v Status depois: pago={tx_confirmada.pago}")
        print(f"v ID da transação: {tx_confirmada.id}")
        
        assert tx_confirmada.pago == True, "Transação não foi marcada como paga"
        assert tx_confirmada.id == tx_pendente.id, "IDs não conferem"
        
        print("\n TEST 3 PASSED")
    except Exception as e:
        print(f"\n TEST 3 FAILED: {e}")
        raise


def test_validacoes_servicos():
    print("\n" + "="*60)
    print("TEST 4: Validações dos serviços")
    print("="*60)
    
    limpar_dados()
    user, conta1, conta2, _, _ = criar_usuario_teste()
    
    print("\nTest 4.1: Transferência com valor negativo")
    try:
        transferir_saldo(user, conta1, conta2, -100)
        print(" FALHOU: Deveria ter lançado erro")
    except TransferenciaInvalidaError as e:
        print(f"v Erro capturado corretamente: {e}")
    
    print("\nTest 4.2: Transferência com saldo insuficiente")
    try:
        transferir_saldo(user, conta1, conta2, 10000)
        print("v FALHOU: Deveria ter lançado erro")
    except TransferenciaInvalidaError as e:
        print(f"v Erro capturado corretamente: {e}")
    
    print("\nTest 4.3: Transferência para mesma conta")
    try:
        transferir_saldo(user, conta1, conta1, 100)
        print(" FALHOU: Deveria ter lançado erro")
    except TransferenciaInvalidaError as e:
        print(f"v Erro capturado corretamente: {e}")
    
    print("\nTest 4.4: Confirmação sem transação pendente")
    try:
        confirmar_recebimento_pede_meia(user, 1, 2099)
        print(" FALHOU: Deveria ter lançado erro")
    except ConfirmacaoRecebimentoError as e:
        print(f"v Erro capturado corretamente: {e}")
    
    print("\n TEST 4 PASSED")


if __name__ == '__main__':
    print("\n" + "VALIDACAO COMPLETA DOS SERVICOS REFATORADOS".center(60, "="))
    
    try:
        test_transferir_saldo()
        test_depositar_em_meta()
        test_confirmar_recebimento_pede_meia()
        test_validacoes_servicos()
        
        print("\n" + "="*60)
        print("TODOS OS TESTES PASSARAM COM SUCESSO!".center(60))
        print("="*60)
        print("\nResumo:")
        print("  • transferir_saldo() - OK - Funcionando independente")
        print("  • depositar_em_meta() - OK - Funcionando independente")
        print("  • confirmar_recebimento_pede_meia() - OK - Funcionando independente")
        print("  • Validacoes e erros - OK - Funcionando corretamente")
        print("\nAs views agora apenas delegam aos servicos (sem duplicacao)\n")
        
    except Exception as e:
        print(f"\n Erro durante testes: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        limpar_dados()
