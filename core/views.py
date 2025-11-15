from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 
from django.db.models import Sum, Q 
from django.contrib.auth.models import User
from django.db import transaction 
from django.utils.dateparse import parse_date 
from django.utils import timezone 
from .models import Transacao, Categoria, Conta, MetaFinanceira
from .serializers import (
    TransacaoSerializer, 
    CategoriaSerializer, 
    ContaSerializer,
    UserRegisterSerializer,
    MetaFinanceiraSerializer 
)
from .autofill import automatizar_recebimentos_pede_meia

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.usuario == request.user

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny] 
    def perform_create(self, serializer):
        user = serializer.save() 
        serie_aluno = user.perfilaluno.serie_em 

        automatizar_recebimentos_pede_meia(user, serie_aluno)

class CategoriaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner] 

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user).order_by('nome')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class ContaViewSet(viewsets.ModelViewSet):
    serializer_class = ContaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Conta.objects.filter(usuario=self.request.user).order_by('nome')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
        
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def transferir(self, request):
        user = request.user
        
        try:
            conta_origem_id = request.data['conta_origem_id']
            conta_destino_id = request.data['conta_destino_id']
            valor = float(request.data['valor'])
        except (KeyError, ValueError, TypeError):
            return Response(
                {"detail": "Campos 'conta_origem_id', 'conta_destino_id' e 'valor' são obrigatórios e devem ser válidos."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conta_origem = Conta.objects.get(id=conta_origem_id, usuario=user)
            conta_destino = Conta.objects.get(id=conta_destino_id, usuario=user)
        except Conta.DoesNotExist:
            return Response(
                {"detail": "Uma das contas não existe ou não pertence a você."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if conta_origem.id == conta_destino.id:
             return Response(
                {"detail": "A conta de origem e destino devem ser diferentes."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if valor <= 0:
            return Response(
                {"detail": "O valor da transferência deve ser positivo."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        categoria_transferencia_saida, created = Categoria.objects.get_or_create(
            usuario=user, 
            nome="Transferência (Saída)",
            defaults={'tipo_categoria': 'saida'}
        )
        
        Transacao.objects.create(
            usuario=user,
            categoria=categoria_transferencia_saida,
            conta=conta_origem,
            tipo='saida',
            descricao=f"Transferência para {conta_destino.nome} (Meta)",
            valor=valor,
            data=timezone.now().date(),
            pago=True 
        )

        categoria_transferencia_entrada, created = Categoria.objects.get_or_create(
            usuario=user, 
            nome="Transferência (Entrada)",
            defaults={'tipo_categoria': 'entrada'}
        )

        Transacao.objects.create(
            usuario=user,
            categoria=categoria_transferencia_entrada,
            conta=conta_destino,
            tipo='entrada',
            descricao=f"Transferência de {conta_origem.nome}",
            valor=valor,
            data=timezone.now().date(),
            pago=True 
        )
        
        return Response(
            {"detail": f"Transferência de R$ {valor:.2f} de {conta_origem.nome} para {conta_destino.nome} realizada com sucesso."}, 
            status=status.HTTP_201_CREATED
        )

class TransacaoViewSet(viewsets.ModelViewSet):
    serializer_class = TransacaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Transacao.objects.filter(usuario=self.request.user).order_by('-data')

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def resumo_financeiro(self, request):
        from_date_str = request.query_params.get('from_date')
        to_date_str = request.query_params.get('to_date')
        filters = {'usuario': request.user}
        
        if from_date_str:
            filters['data__gte'] = parse_date(from_date_str)

        if to_date_str:
            filters['data__lte'] = parse_date(to_date_str)

        total_entradas = Transacao.objects.filter(
            **filters, 
            tipo='entrada', 
            pago=True
        ).aggregate(Sum('valor'))['valor__sum'] or 0.00

        total_saidas = Transacao.objects.filter(
            **filters, 
            tipo='saida', 
            pago=True
        ).aggregate(Sum('valor'))['valor__sum'] or 0.00

        saldo_atual = total_entradas - total_saidas
        
        return Response({
            'saldo_atual': round(saldo_atual, 2), 
            'total_entradas': round(total_entradas, 2),
            'total_saidas': round(total_saidas, 2)
        })
        
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def confirmar_recebimento(self, request):
        user = request.user
        hoje = timezone.localdate()
        transacao_a_promover = Transacao.objects.filter(
            usuario=user,
            pago=False,
            tipo='entrada',
            data__lte=hoje, 
            descricao__startswith='Pé-de-Meia: Frequência'
        ).order_by('data').first() 

        if not transacao_a_promover:
            return Response(
                {"detail": "Nenhuma parcela de Pé-de-Meia pendente ou com data de pagamento atingida para confirmação."},
                status=status.HTTP_400_BAD_REQUEST
            )

        transacao_a_promover.pago = True
        transacao_a_promover.save()

        return Response(
            {"detail": f"Recebimento de R$ {transacao_a_promover.valor:.2f} (Pé-de-Meia) confirmado com sucesso! Saldo atualizado."},
            status=status.HTTP_200_OK
        )
    
class MetaFinanceiraViewSet(viewsets.ModelViewSet):
    serializer_class = MetaFinanceiraSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner] 

    def get_queryset(self):
        return MetaFinanceira.objects.filter(usuario=self.request.user).order_by('-ativa', 'data_alvo')

    @transaction.atomic 
    def perform_create(self, serializer):
        user = self.request.user
        nome_conta = f"Poupança: {serializer.validated_data['nome']}"
        conta = Conta.objects.create(
            usuario=user,
            nome=nome_conta,
            saldo_inicial=0.00
        )
        
        serializer.save(usuario=user, conta_vinculada=conta)

    @action(detail=True, methods=['get'])
    def progresso(self, request, pk=None):
        meta = self.get_object()
        valor_atual = meta.conta_vinculada.saldo_inicial 
        valor_alvo = meta.valor_alvo
        falta = max(0, valor_alvo - valor_atual)
        percentual = (valor_atual / valor_alvo) * 100 if valor_alvo > 0 else 0
        
        return Response({
            'meta_id': meta.id,
            'nome': meta.nome,
            'valor_alvo': valor_alvo,
            'valor_atual': valor_atual,
            'falta_atingir': round(falta, 2),
            'percentual_atingido': round(percentual, 2),
        }) 