from rest_framework import viewsets, permissions, generics 
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny 
from django.db.models import Sum, Q 
from django.contrib.auth.models import User 

from .models import Transacao, Categoria, Conta
from .serializers import (
    TransacaoSerializer, 
    CategoriaSerializer, 
    ContaSerializer,
    UserRegisterSerializer 
)
class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.usuario == request.user

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny] 

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
        total_entradas = Transacao.objects.filter(
            usuario=request.user, 
            tipo='entrada', 
            pago=True
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        total_saidas = Transacao.objects.filter(
            usuario=request.user, 
            tipo='saida', 
            pago=True
        ).aggregate(Sum('valor'))['valor__sum'] or 0

        saldo_atual = total_entradas - total_saidas
        
        return Response({
            'saldo_atual': saldo_atual,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas
        })