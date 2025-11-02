from rest_framework import serializers
from .models import Transacao, Categoria, Conta
from django.contrib.auth.models import User

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'tipo_categoria']
        read_only_fields = ('usuario',) 

class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = ['id', 'nome', 'saldo_inicial']
        read_only_fields = ('usuario',)

class TransacaoSerializer(serializers.ModelSerializer):
    
    categoria_nome = serializers.ReadOnlyField(source='categoria.nome')
    conta_nome = serializers.ReadOnlyField(source='conta.nome')
    tipo_categoria = serializers.ReadOnlyField(source='categoria.tipo_categoria')
    
    class Meta:
        model = Transacao
        fields = [
            'id', 
            'tipo', 
            'descricao', 
            'valor', 
            'data', 
            'parcelas', 
            'vencimento', 
            'pago', 
            'usuario',  
            'categoria', 'categoria_nome', 'tipo_categoria',  
            'conta', 'conta_nome'  
        ]
        read_only_fields = ('usuario',)

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user