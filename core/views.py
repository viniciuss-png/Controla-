from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
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
from .services import (
    transferir_saldo,
    depositar_em_meta,
    confirmar_recebimento_pede_meia,
    TransferenciaInvalidaError,
    DepositoMetaError,
    ConfirmacaoRecebimentoError,
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

        try:
            transacao = confirmar_recebimento_pede_meia(request.user, mes, ano)
            return Response(
                {
                    "detail": f"Parcela de {mes}/{ano} confirmada com sucesso.",
                    "transacao_id": transacao.id,
                    "valor": float(transacao.valor),
                },
                status=status.HTTP_200_OK
            )
        except ConfirmacaoRecebimentoError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
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

        try:
            origem = Conta.objects.get(id=conta_origem_id, usuario=request.user)
            destino = Conta.objects.get(id=conta_destino_id, usuario=request.user)
        except Conta.DoesNotExist:
            return Response(
                {"detail": "Uma ou ambas as contas não existem ou não pertencem a você."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            transacao_saida, transacao_entrada = transferir_saldo(
                request.user, origem, destino, valor
            )
            return Response(
                {
                    "detail": f"Transferência de R$ {valor:.2f} realizada com sucesso.",
                    "transacao_saida_id": transacao_saida.id,
                    "transacao_entrada_id": transacao_entrada.id,
                },
                status=status.HTTP_201_CREATED
            )
        except TransferenciaInvalidaError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
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
        try:
            valor = float(request.data.get('valor', 0))
        except (ValueError, TypeError):
            return Response(
                {"detail": "Valor inválido. Deve ser um número positivo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        meta = self.get_object()

        try:
            transacao_saida, transacao_entrada = depositar_em_meta(
                request.user, meta, valor
            )
            return Response(
                {
                    "detail": f"Depósito de R$ {valor:.2f} realizado na meta '{meta.nome}'.",
                    "transacao_saida_id": transacao_saida.id,
                    "transacao_entrada_id": transacao_entrada.id,
                },
                status=status.HTTP_200_OK
            )
        except DepositoMetaError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Erro inesperado: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )