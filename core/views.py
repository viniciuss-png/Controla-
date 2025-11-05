from rest_framework import viewsets, permissions, generics 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 
from django.db.models import Sum, Q 
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date 
from .models import Transacao, Categoria, Conta
from .serializers import (
    TransacaoSerializer, 
    CategoriaSerializer, 
    ContaSerializer,
    UserRegisterSerializer 
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