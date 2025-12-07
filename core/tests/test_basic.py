import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import date, timedelta
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from django.test import TestCase
from core.models import (
    Categoria, Conta, Transacao, PerfilAluno, MetaFinanceira
)
from core.services import transferir_saldo, depositar_em_meta

@pytest.fixture
def user_factory(db):
    def create_user(username="testuser", password="testpass123"):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@test.com",
            password=password
        )
        PerfilAluno.objects.get_or_create(
            usuario=user,
            defaults={
                'email': f"{username}@test.com",
                'serie_em': 1
            }
        )
        return user
    return create_user

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user_authenticated(user_factory, api_client):
    user = user_factory(username="authenticated_user")
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return user, api_client

@pytest.fixture
def setup_transacao(user_factory):
    user = user_factory(username="transacao_test_user")
    categoria = Categoria.objects.create(
        nome="Alimentação",
        tipo_categoria="saida",
        usuario=user
    )
    conta_principal = Conta.objects.create(
        nome="Principal",
        saldo_inicial=Decimal("1000.00"),
        saldo_atual=Decimal("1000.00"),
        usuario=user
    )
    conta_secundaria = Conta.objects.create(
        nome="Reserva",
        saldo_inicial=Decimal("200.00"),
        saldo_atual=Decimal("200.00"),
        usuario=user
    )
    return user, categoria, conta_principal, conta_secundaria

@pytest.mark.django_db
class TestUserRegistration:
    
    def test_user_registration_success(self, api_client):
        data = {
            "username": "newuser123",
            "password": "securepass123",
            "email": "newuser123@test.com",
            "serie_em": 2
        }
        response = api_client.post('/api/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser123").exists()
        perfil = PerfilAluno.objects.get(usuario__username="newuser123")
        assert perfil.serie_em == 2
    
    def test_user_registration_duplicate_username(self, api_client, user_factory):
        user_factory(username="existing")
        data = {
            "username": "existing",
            "password": "pass123",
            "email": "different@test.com",
            "serie_em": 1
        }
        response = api_client.post('/api/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data
    
    def test_perfil_aluno_created_automatically(self, user_factory):
        user = user_factory()
        perfil = PerfilAluno.objects.get(usuario=user)
        assert perfil.serie_em == 1 
        assert perfil.ano_registro == timezone.now().year
        assert perfil.concluiu == False


@pytest.mark.django_db
class TestJWTAuthentication:
    
    def test_token_obtain(self, user_factory, api_client):
        user_factory(username="testuser", password="testpass123")
        data = {"username": "testuser", "password": "testpass123"}
        response = api_client.post('/api/token/', data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
    
    def test_access_protected_endpoint_without_token(self, api_client):
        response = api_client.get('/api/transacoes/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
class TestCategoriaViewSet:
    
    def test_criar_categoria(self, user_authenticated):
        user, api_client = user_authenticated
        data = {"nome": "Alimentação", "tipo_categoria": "saida"}
        response = api_client.post('/api/categorias/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Categoria.objects.filter(nome="Alimentação", usuario=user).exists()
    
    def test_categoria_unique_por_usuario(self, user_authenticated):
        user, api_client = user_authenticated
        data = {"nome": "Transporte", "tipo_categoria": "saida"}
        api_client.post('/api/categorias/', data)
        response = api_client.post('/api/categorias/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_listar_categorias_isoladas_por_usuario(self, user_authenticated, user_factory, api_client):
        user1, api_client = user_authenticated
        user2 = user_factory(username="user2")
        
        Categoria.objects.create(nome="Cat1", usuario=user1)
        Categoria.objects.create(nome="Cat2", usuario=user2)
        
        response = api_client.get('/api/categorias/')
        assert len(response.data) == 1
        assert response.data[0]['nome'] == "Cat1"


@pytest.mark.django_db
class TestServicesTransacciones:
    
    def test_transferir_saldo_atomico_e_saldo_atualizado(self, setup_transacao):
        user, _, conta_origem, conta_destino = setup_transacao
        valor = Decimal("500.00")
        
        transferir_saldo(
            usuario=user,
            origem=conta_origem,
            destino=conta_destino,
            valor=float(valor)
        )
        
        conta_origem.refresh_from_db()
        conta_destino.refresh_from_db()
        
        assert conta_origem.saldo_atual == Decimal("500.00")
        assert conta_destino.saldo_atual == Decimal("700.00")
        
        transacoes = Transacao.objects.all()
        assert transacoes.count() == 2
        
        saida = transacoes.filter(tipo="saida", conta=conta_origem).first()
        assert saida.valor == valor
        
        entrada = transacoes.filter(tipo="entrada", conta=conta_destino).first()
        assert entrada.valor == valor
    
    def test_depositar_em_meta_atomico_e_saldo_atualizado(self, setup_transacao):
        user, _, conta_principal, _ = setup_transacao
        valor = Decimal("200.00")
        
        conta_meta = Conta.objects.create(
            nome="Conta Meta",
            saldo_inicial=Decimal("0.00"),
            usuario=user
        )
        
        meta = MetaFinanceira.objects.create(
            usuario=user,
            nome="Viagem",
            valor_alvo=Decimal("500.00"),
            conta_vinculada=conta_meta
        )
        
        depositar_em_meta(
            usuario=user,
            meta=meta,
            valor=float(valor)
        )
        
        conta_principal.refresh_from_db()
        conta_meta.refresh_from_db()
        
        assert conta_principal.saldo_atual == Decimal("800.00") 
        assert conta_meta.saldo_atual == Decimal("200.00") 

        transacoes = Transacao.objects.all()
        saida_principal = transacoes.filter(tipo="saida", conta=conta_principal).first()
        entrada_meta = transacoes.filter(tipo="entrada", conta=conta_meta).first()

        assert saida_principal is not None
        assert entrada_meta is not None
        assert entrada_meta.descricao.startswith("Depósito em Meta: Viagem")


@pytest.mark.django_db
class TestValidacoesEIsolamento:
    
    def test_transacao_valor_positivo_model_validation(self, setup_transacao):
        user, cat, conta, _ = setup_transacao
        
        transacao = Transacao(
            usuario=user,
            categoria=cat,
            conta=conta,
            tipo="saida",
            descricao="Invalid",
            valor=Decimal("-10.00"),
            data=date.today()
        )
        
        with pytest.raises(DjangoValidationError):
            transacao.full_clean()
    
    def test_transferir_saldo_contas_diferentes(self, setup_transacao):
        user, _, conta_origem, _ = setup_transacao
        
        from core.services import TransferenciaInvalidaError
        with pytest.raises(TransferenciaInvalidaError):
            transferir_saldo(
                usuario=user,
                origem=conta_origem,
                destino=conta_origem,
                valor=100.00
            )
            
    def test_meta_isolada_por_usuario(self, user_authenticated, user_factory, api_client):
        user1, api_client = user_authenticated
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