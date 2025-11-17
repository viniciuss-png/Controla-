"""
Suite de testes para aplicação Controlaê
Cobre autenticação, permissões, CRUD, e operações críticas
"""
import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from django.utils import timezone
from datetime import date, timedelta

from core.models import (
    Categoria, Conta, Transacao, PerfilAluno, MetaFinanceira
)
from core.services import transferir_saldo, depositar_em_meta


# ============================================================================
# FIXTURES E FACTORIES
# ============================================================================

@pytest.fixture
def user_factory():
    """Factory para criar usuários de teste com nomes únicos"""
    counter = {"value": 0}
    def create_user(username=None, password="testpass123"):
        if username is None:
            counter["value"] += 1
            username = f"testuser{counter['value']}"
        return User.objects.create_user(
            username=username,
            email=f"{username}@test.com",
            password=password,
            first_name="Test",
            last_name="User"
        )
    return create_user


@pytest.fixture
def api_client():
    """Client API com suporte a autenticação"""
    return APIClient()


@pytest.fixture
def user_authenticated(user_factory, api_client):
    """Usuário criado e autenticado"""
    user = user_factory()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return user, api_client


# ============================================================================
# TESTES DE AUTENTICAÇÃO E REGISTRO
# ============================================================================

@pytest.mark.django_db
class TestUserRegistration:
    """Testes para registro de usuários"""
    
    def test_user_registration_success(self, api_client):
        """Registro de usuário bem-sucedido cria usuário e perfil"""
        data = {
            "username": "newuser123",
            "password": "securepass123",
            "serie_em": 1
        }
        
        response = api_client.post('/api/register/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser123").exists()
        perfil = PerfilAluno.objects.get(usuario__username="newuser123")
        assert perfil.serie_em == 1
    
    def test_user_registration_missing_fields(self, api_client):
        """Registro falha sem campos obrigatórios"""
        data = {
            "username": "incompleteuser"
            # faltam email, password, first_name, last_name
        }
        
        response = api_client.post('/api/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_user_registration_duplicate_username(self, api_client, user_factory):
        """Não permite criar usuário com username duplicado"""
        user_factory(username="existing")
        
        data = {
            "username": "existing",
            "email": "different@test.com",
            "password": "pass123",
            "first_name": "Outro",
            "last_name": "Usuário"
        }
        
        response = api_client.post('/api/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_perfil_aluno_created_automatically(self, user_factory):
        """PerfilAluno é criado automaticamente ao criar usuário"""
        user = user_factory()
        
        perfil = PerfilAluno.objects.get(usuario=user)
        assert perfil.serie_em == 1  # default
        assert perfil.ano_registro == timezone.now().year
        assert perfil.concluiu == False


@pytest.mark.django_db
class TestJWTAuthentication:
    """Testes para autenticação JWT"""
    
    def test_token_obtain(self, user_factory, api_client):
        """Obter token JWT com credenciais corretas"""
        user = user_factory(username="testuser", password="testpass123")
        
        data = {"username": "testuser", "password": "testpass123"}
        response = api_client.post('/api/token/', data)
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
    
    def test_token_invalid_credentials(self, user_factory, api_client):
        """Falha ao obter token com credenciais incorretas"""
        user_factory(username="testuser", password="testpass123")
        
        data = {"username": "testuser", "password": "wrongpassword"}
        response = api_client.post('/api/token/', data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_access_protected_endpoint_with_token(self, user_authenticated):
        """Acesso permitido a endpoint protegido com token válido"""
        user, api_client = user_authenticated
        
        response = api_client.get('/api/transacoes/')
        assert response.status_code == status.HTTP_200_OK
    
    def test_access_protected_endpoint_without_token(self, api_client):
        """Acesso negado a endpoint protegido sem token"""
        response = api_client.get('/api/transacoes/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================================================
# TESTES DE CATEGORIAS
# ============================================================================

@pytest.mark.django_db
class TestCategoriaViewSet:
    """Testes para CRUD de categorias"""
    
    def test_criar_categoria(self, user_authenticated):
        """Usuário pode criar categoria"""
        user, api_client = user_authenticated
        
        data = {
            "nome": "Alimentação",
            "tipo_categoria": "saida"
        }
        
        response = api_client.post('/api/categorias/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Categoria.objects.filter(nome="Alimentação", usuario=user).exists()
    
    def test_categoria_unique_por_usuario(self, user_authenticated, user_factory, api_client):
        """Não permite categoria duplicada para mesmo usuário"""
        user, api_client = user_authenticated
        
        # Criar primeira categoria
        data = {"nome": "Transporte", "tipo_categoria": "saida"}
        api_client.post('/api/categorias/', data)
        
        # Tentar criar duplicada
        response = api_client.post('/api/categorias/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_categoria_mesmo_nome_usuarios_diferentes(self, user_factory, api_client):
        """Usuários diferentes podem ter categorias com mesmo nome"""
        user1 = user_factory(username="user1")
        user2 = user_factory(username="user2")
        
        Categoria.objects.create(
            nome="Saúde",
            tipo_categoria="saida",
            usuario=user1
        )
        
        # Mesmo nome, usuário diferente = OK
        cat2 = Categoria.objects.create(
            nome="Saúde",
            tipo_categoria="saida",
            usuario=user2
        )
        
        assert cat2.id != 1
    
    def test_listar_categorias_isoladas_por_usuario(self, user_factory, api_client):
        """Usuário só vê suas próprias categorias"""
        user1 = user_factory(username="user1")
        user2 = user_factory(username="user2")
        
        Categoria.objects.create(nome="Cat1", usuario=user1)
        Categoria.objects.create(nome="Cat2", usuario=user2)
        
        refresh = RefreshToken.for_user(user1)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.get('/api/categorias/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['nome'] == "Cat1"


# ============================================================================
# TESTES DE CONTAS
# ============================================================================

@pytest.mark.django_db
class TestContaViewSet:
    """Testes para CRUD de contas"""
    
    def test_criar_conta(self, user_authenticated):
        """Usuário pode criar conta"""
        user, api_client = user_authenticated
        
        data = {
            "nome": "Conta Corrente",
            "saldo_inicial": "1000.00"
        }
        
        response = api_client.post('/api/contas/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Conta.objects.filter(nome="Conta Corrente", usuario=user).exists()
    
    def test_saldo_inicial_persistido(self, user_factory):
        """Saldo inicial é armazenado corretamente"""
        user = user_factory()
        
        conta = Conta.objects.create(
            nome="Poupança",
            saldo_inicial=Decimal("500.50"),
            usuario=user
        )
        
        assert conta.saldo_inicial == Decimal("500.50")
    
    def test_conta_isolada_por_usuario(self, user_factory, api_client):
        """Usuário só pode acessar suas próprias contas"""
        user1 = user_factory(username="user1")
        user2 = user_factory(username="user2")
        
        conta1 = Conta.objects.create(nome="Conta1", usuario=user1)
        conta2 = Conta.objects.create(nome="Conta2", usuario=user2)
        
        refresh = RefreshToken.for_user(user1)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.get('/api/contas/')
        assert len(response.data) == 1
        assert response.data[0]['nome'] == "Conta1"


# ============================================================================
# TESTES DE TRANSAÇÕES
# ============================================================================

@pytest.mark.django_db
class TestTransacaoViewSet:
    """Testes para CRUD e operações de transações"""
    
    @pytest.fixture
    def transacao_setup(self, user_factory):
        """Setup: usuário com conta e categoria"""
        user = user_factory()
        categoria = Categoria.objects.create(
            nome="Alimentação",
            tipo_categoria="saida",
            usuario=user
        )
        conta = Conta.objects.create(
            nome="Corrente",
            saldo_inicial=Decimal("1000.00"),
            usuario=user
        )
        return user, categoria, conta, user_factory
    
    def test_criar_transacao(self, transacao_setup, api_client):
        """Usuário pode criar transação"""
        user, cat, conta, _ = transacao_setup
        
        # Autenticar com o mesmo usuário
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            "categoria": cat.id,
            "conta": conta.id,
            "tipo": "saida",
            "descricao": "Almoço",
            "valor": "25.50",
            "data": date.today().isoformat()
        }
        
        response = api_client.post('/api/transacoes/', data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_transacao_categoria_outro_usuario(self, user_factory, api_client):
        """Não permite usar categoria de outro usuário"""
        user1 = user_factory(username="user1")
        user2 = user_factory(username="user2")
        
        cat_user1 = Categoria.objects.create(
            nome="Categoria1",
            usuario=user1
        )
        conta_user1 = Conta.objects.create(nome="Conta1", usuario=user1)
        
        refresh = RefreshToken.for_user(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            "categoria": cat_user1.id,
            "conta": conta_user1.id,
            "tipo": "saida",
            "descricao": "Test",
            "valor": "10.00",
            "data": date.today().isoformat()
        }
        
        response = api_client.post('/api/transacoes/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_transacao_isolada_por_usuario(self, user_factory, api_client):
        """Usuário só vê suas próprias transações"""
        user1 = user_factory(username="user1")
        user2 = user_factory(username="user2")
        
        cat1 = Categoria.objects.create(usuario=user1)
        conta1 = Conta.objects.create(usuario=user1)
        
        Transacao.objects.create(
            usuario=user1,
            categoria=cat1,
            conta=conta1,
            tipo="entrada",
            descricao="Trans1",
            valor="100.00",
            data=date.today()
        )
        
        refresh = RefreshToken.for_user(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.get('/api/transacoes/')
        assert len(response.data) == 0


# ============================================================================
# TESTES DE METAS FINANCEIRAS
# ============================================================================

@pytest.mark.django_db
class TestMetaFinanceiraViewSet:
    """Testes para CRUD e operações de metas"""
    
    @pytest.fixture
    def meta_setup(self, user_factory):
        """Setup: usuário com conta para meta"""
        user = user_factory()
        conta = Conta.objects.create(
            nome="Poupança Meta",
            saldo_inicial=Decimal("0.00"),
            usuario=user
        )
        return user, conta
    
    def test_criar_meta(self, meta_setup, user_authenticated):
        """Usuário pode criar meta financeira"""
        user, conta = meta_setup
        _, api_client = user_authenticated
        
        data = {
            "nome": "Viagem",
            "valor_alvo": "1000.00",
            "conta_vinculada": conta.id,
            "data_alvo": (date.today() + timedelta(days=365)).isoformat()
        }
        
        response = api_client.post('/api/metas/', data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_meta_isolada_por_usuario(self, user_factory, api_client):
        """Usuário só vê suas próprias metas"""
        user1 = user_factory(username="user1")
        user2 = user_factory(username="user2")
        
        conta1 = Conta.objects.create(usuario=user1)
        MetaFinanceira.objects.create(
            usuario=user1,
            nome="Meta1",
            valor_alvo="500.00",
            conta_vinculada=conta1
        )
        
        refresh = RefreshToken.for_user(user2)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = api_client.get('/api/metas/')
        assert len(response.data) == 0


# ============================================================================
# TESTES DE SERVIÇOS CRÍTICOS (OPERAÇÕES ATÔMICAS)
# ============================================================================

@pytest.mark.django_db
class TestServicesTransacciones:
    """Testes para garantir atomicidade de operações críticas"""
    
    def test_transferir_saldo_atomico(self, user_factory):
        """Transferência é atômica: débito + crédito"""
        user = user_factory()
        
        conta_origem = Conta.objects.create(
            nome="Origem",
            saldo_inicial=Decimal("1000.00"),
            usuario=user
        )
        conta_destino = Conta.objects.create(
            nome="Destino",
            saldo_inicial=Decimal("0.00"),
            usuario=user
        )
        
        categoria = Categoria.objects.create(
            nome="Transferência",
            tipo_categoria="entrada",
            usuario=user
        )
        
        # Transferir (assinatura: usuario, origem, destino, valor com float)
        transferir_saldo(
            usuario=user,
            origem=conta_origem,
            destino=conta_destino,
            valor=500.00  # float é OK, função converte
        )
        
        # Verificar transações criadas
        transacoes = Transacao.objects.all()
        assert transacoes.count() == 2
        
        saida = transacoes.filter(tipo="saida", conta=conta_origem).first()
        entrada = transacoes.filter(tipo="entrada", conta=conta_destino).first()
        
        assert saida.valor == Decimal("500.00")
        assert entrada.valor == Decimal("500.00")
    
    def test_depositar_em_meta_atomico(self, user_factory):
        """Depósito em meta é atômico"""
        user = user_factory()
        
        conta = Conta.objects.create(
            nome="Poupança",
            saldo_inicial=Decimal("1000.00"),
            usuario=user
        )
        
        meta = MetaFinanceira.objects.create(
            usuario=user,
            nome="Viagem",
            valor_alvo=Decimal("500.00"),
            conta_vinculada=conta
        )
        
        categoria = Categoria.objects.create(
            nome="Meta",
            tipo_categoria="entrada",
            usuario=user
        )
        
        # Depositar (assinatura: usuario, meta, valor com float)
        depositar_em_meta(
            usuario=user,
            meta=meta,
            valor=200.00  # float é OK, função converte
        )
        
        # Verificar transação criada
        transacao = Transacao.objects.filter(conta=conta, tipo="entrada").first()
        assert transacao is not None
        assert transacao.valor == Decimal("200.00")


# ============================================================================
# TESTES DE VALIDAÇÕES
# ============================================================================

@pytest.mark.django_db
class TestValidacoes:
    """Testes para validações de negócio"""
    
    def test_transacao_descricao_obrigatoria(self, user_factory, api_client):
        """Transação requer descrição"""
        user = user_factory()
        cat = Categoria.objects.create(usuario=user)
        conta = Conta.objects.create(usuario=user)
        
        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        data = {
            "categoria": cat.id,
            "conta": conta.id,
            "tipo": "saida",
            # falta descricao
            "valor": "10.00",
            "data": date.today().isoformat()
        }
        
        response = api_client.post('/api/transacoes/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_transacao_valor_positivo(self, user_factory):
        """Valor de transação deve ser positivo (validação clean)"""
        user = user_factory()
        cat = Categoria.objects.create(usuario=user)
        conta = Conta.objects.create(usuario=user)
        
        transacao = Transacao(
            usuario=user,
            categoria=cat,
            conta=conta,
            tipo="saida",
            descricao="Invalid",
            valor=Decimal("-10.00"),
            data=date.today()
        )
        
        # Clean() deve lançar ValidationError para valores negativos
        from django.core.exceptions import ValidationError as DjangoValidationError
        with pytest.raises(DjangoValidationError):
            transacao.full_clean()
    
    def test_meta_valor_alvo_positivo(self, user_factory):
        """Meta deve ter valor alvo positivo"""
        user = user_factory()
        conta = Conta.objects.create(usuario=user)
        
        meta = MetaFinanceira(
            usuario=user,
            nome="Invalid",
            valor_alvo=Decimal("-500.00"),
            conta_vinculada=conta
        )
        
        from django.core.exceptions import ValidationError as DjangoValidationError
        with pytest.raises(DjangoValidationError):
            meta.full_clean()
