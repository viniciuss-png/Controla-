import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Incentivo, Conta, Transacao
from core.services import (
    criar_incentivo_conclusao,
    liberar_incentivo_conclusao,
    criar_incentivo_enem,
)


@pytest.mark.django_db
def test_criar_incentivo_conclusao_service():
    user = User.objects.create_user(username="incentivo_user", password="pass")
    conta = Conta.objects.create(usuario=user, nome='Conta', saldo_inicial=Decimal('1000.00'), saldo_atual=Decimal('1000.00'))

    incentivo = criar_incentivo_conclusao(user, timezone.now().year, conta)

    assert Incentivo.objects.filter(id=incentivo.id).exists()
    assert incentivo.liberado is False
    assert incentivo.valor == Decimal('1000.00')


@pytest.mark.django_db
def test_liberar_incentivo_conclusao_service():
    user = User.objects.create_user(username="incentivo_user2", password="pass")
    conta = Conta.objects.create(usuario=user, nome='Conta', saldo_inicial=Decimal('0.00'), saldo_atual=Decimal('0.00'))

    incentivo = criar_incentivo_conclusao(user, timezone.now().year, conta)
    incentivo, transacao = liberar_incentivo_conclusao(incentivo)

    assert incentivo.liberado is True
    assert transacao is not None
    assert transacao.valor == incentivo.valor

    conta.refresh_from_db()
    assert conta.saldo_atual == Decimal('1000.00')


@pytest.mark.django_db
def test_criar_incentivo_enem_service():
    user = User.objects.create_user(username="incentivo_enem", password="pass")
    conta = Conta.objects.create(usuario=user, nome='Conta', saldo_inicial=Decimal('0.00'), saldo_atual=Decimal('0.00'))

    incentivo, transacao = criar_incentivo_enem(user, conta, ano=timezone.now().year)

    assert incentivo.liberado is True
    assert transacao.valor == incentivo.valor == Decimal('200.00')

    conta.refresh_from_db()
    assert conta.saldo_atual == Decimal('200.00')


@pytest.mark.django_db
def test_incentivo_endpoints_api():
    user = User.objects.create_user(username='api_user', password='pass')
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    conta = Conta.objects.create(usuario=user, nome='Conta', saldo_inicial=Decimal('0.00'), saldo_atual=Decimal('0.00'))

    resp = client.post('/api/incentivos/conclusao/', {'ano': timezone.now().year, 'conta_id': conta.id}, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    inc_id = resp.data['id']
    assert resp.data['liberado'] is False

    resp_lib = client.post('/api/incentivos/conclusao/liberar/', {'incentivo_id': inc_id}, format='json')
    assert resp_lib.status_code == status.HTTP_200_OK

    resp_enem = client.post('/api/incentivos/enem/', {'ano': timezone.now().year, 'conta_id': conta.id}, format='json')
    assert resp_enem.status_code == status.HTTP_201_CREATED
