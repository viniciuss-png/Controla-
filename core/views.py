from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
from .permissions import IsOwner
from .models import Transacao, Categoria, Conta, MetaFinanceira
from .serializers import (
    TransacaoSerializer,
    CategoriaSerializer,
    ContaSerializer,
    MetaFinanceiraSerializer,
    UserRegisterSerializer
)


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()


class TransacaoViewSet(viewsets.ModelViewSet):
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Transacao.objects.filter(usuario=self.request.user).order_by('-data')

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def resumo_financeiro(self, request):
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")

        filters = {"usuario": request.user}

        if from_date:
            filters["data__gte"] = parse_date(from_date)

        if to_date:
            filters["data__lte"] = parse_date(to_date)

        total_entradas = (
            Transacao.objects.filter(**filters, tipo="entrada", pago=True)
            .aggregate(Sum("valor"))["valor__sum"] or 0
        )

        total_saidas = (
            Transacao.objects.filter(**filters, tipo="saida", pago=True)
            .aggregate(Sum("valor"))["valor__sum"] or 0
        )

        return Response({
            "saldo_atual": total_entradas - total_saidas,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas
        })

    @action(detail=False, methods=['post'])
    def confirmar_recebimento(self, request):
        try:
            mes = int(request.data.get('mes', timezone.localdate().month))
            ano = int(request.data.get('ano', timezone.localdate().year))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Campos 'mes' e 'ano' devem ser inteiros válidos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        transacao = Transacao.objects.filter(
            usuario=request.user,
            tipo='entrada',
            pago=False,
            data__month=mes,
            data__year=ano,
            descricao__startswith="Pé-de-Meia"
        ).order_by('data').first()

        if not transacao:
            return Response(
                {"detail": "Nenhuma parcela pendente para esse mês."},
                status=status.HTTP_400_BAD_REQUEST
            )

        transacao.pago = True
        transacao.save()

        return Response(
            {"detail": f"Parcela de {mes}/{ano} confirmada com sucesso."},
            status=status.HTTP_200_OK
        )

class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)

class ContaViewSet(viewsets.ModelViewSet):
    serializer_class = ContaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Conta.objects.filter(usuario=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['post'])
    def transferir(self, request):
        try:
            conta_origem_id = request.data['conta_origem_id']
            conta_destino_id = request.data['conta_destino_id']
            valor = float(request.data['valor'])
        except (KeyError, ValueError, TypeError):
            return Response(
                {"detail": "Campos 'conta_origem_id', 'conta_destino_id' e 'valor' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if valor <= 0:
            return Response(
                {"detail": "O valor deve ser positivo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            origem = Conta.objects.get(id=conta_origem_id, usuario=request.user)
            destino = Conta.objects.get(id=conta_destino_id, usuario=request.user)
        except Conta.DoesNotExist:
            return Response(
                {"detail": "Uma ou ambas as contas não existem."},
                status=status.HTTP_404_NOT_FOUND
            )

        if origem.id == destino.id:
            return Response(
                {"detail": "As contas devem ser diferentes."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if origem.saldo_inicial < valor:
            return Response(
                {"detail": "Saldo insuficiente."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            origem.saldo_inicial -= valor
            destino.saldo_inicial += valor
            origem.save()
            destino.save()

            cat_saida, _ = Categoria.objects.get_or_create(
                usuario=request.user,
                nome="Transferência (Saída)",
                defaults={'tipo_categoria': 'saida'}
            )
            cat_entrada, _ = Categoria.objects.get_or_create(
                usuario=request.user,
                nome="Transferência (Entrada)",
                defaults={'tipo_categoria': 'entrada'}
            )

            hoje = timezone.localdate()

            Transacao.objects.create(
                usuario=request.user,
                categoria=cat_saida,
                conta=origem,
                tipo='saida',
                descricao=f"Transferência para {destino.nome}",
                valor=valor,
                data=hoje,
                pago=True
            )

            Transacao.objects.create(
                usuario=request.user,
                categoria=cat_entrada,
                conta=destino,
                tipo='entrada',
                descricao=f"Transferência de {origem.nome}",
                valor=valor,
                data=hoje,
                pago=True
            )

        return Response(
            {"detail": f"Transferência de R$ {valor:.2f} realizada com sucesso."},
            status=status.HTTP_201_CREATED
        )

class MetaFinanceiraViewSet(viewsets.ModelViewSet):
    serializer_class = MetaFinanceiraSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return MetaFinanceira.objects.filter(
            usuario=self.request.user
        ).order_by('-ativa', 'data_alvo')

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        user = self.request.user
        nome_conta = f"Poupança: {serializer.validated_data['nome']}"
        conta = Conta.objects.create(
            usuario=user,
            nome=nome_conta,
            saldo_inicial=0.00
        )

        serializer.save(usuario=user, conta_vinculada=conta)

    def perform_update(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=True, methods=['get'])
    def progresso(self, request, pk=None):
        meta = self.get_object()
        valor_atual = meta.conta_vinculada.saldo_inicial
        valor_alvo = meta.valor_alvo
        percentual = (valor_atual / valor_alvo) * 100 if valor_alvo > 0 else 0
        falta = max(0, valor_alvo - valor_atual)

        return Response({
            "meta_id": meta.id,
            "nome": meta.nome,
            "valor_alvo": valor_alvo,
            "valor_atual": valor_atual,
            "falta_atingir": round(falta, 2),
            "percentual_atingido": round(percentual, 2)
        })

    @action(detail=True, methods=['post'])
    def depositar(self, request, pk=None):
        """Depositar valor em uma meta financeira"""
        try:
            valor = float(request.data.get('valor', 0))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Valor inválido. Deve ser um número positivo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if valor <= 0:
            return Response(
                {"detail": "O valor deve ser positivo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        meta = self.get_object()
        
        # Validar se a meta tem conta vinculada
        if not meta.conta_vinculada:
            return Response(
                {"detail": "Meta não possui conta vinculada."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Encontrar conta principal do usuário
        conta_principal = Conta.objects.filter(
            usuario=request.user
        ).order_by('id').first()

        if not conta_principal:
            return Response(
                {"detail": "Nenhuma conta encontrada para fazer o depósito."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar saldo
        if conta_principal.saldo_inicial < valor:
            return Response(
                {"detail": "Saldo insuficiente na conta principal."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Atualizar saldos
                conta_principal.saldo_inicial -= valor
                conta_principal.save()
                
                meta.conta_vinculada.saldo_inicial += valor
                meta.conta_vinculada.save()

                # Criar transações
                cat_saida, _ = Categoria.objects.get_or_create(
                    usuario=request.user,
                    nome="Depósito em Meta (Saída)",
                    defaults={"tipo_categoria": "saida"}
                )

                cat_entrada, _ = Categoria.objects.get_or_create(
                    usuario=request.user,
                    nome="Depósito em Meta (Entrada)",
                    defaults={"tipo_categoria": "entrada"}
                )

                hoje = timezone.localdate()

                Transacao.objects.create(
                    usuario=request.user,
                    categoria=cat_saida,
                    conta=conta_principal,
                    tipo="saida",
                    descricao=f"Depósito para meta: {meta.nome}",
                    valor=valor,
                    data=hoje,
                    pago=True
                )

                Transacao.objects.create(
                    usuario=request.user,
                    categoria=cat_entrada,
                    conta=meta.conta_vinculada,
                    tipo="entrada",
                    descricao=f"Depósito recebido para meta: {meta.nome}",
                    valor=valor,
                    data=hoje,
                    pago=True
                )

            return Response(
                {"detail": f"Depósito de R$ {valor:.2f} realizado na meta '{meta.nome}'."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )