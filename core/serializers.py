from rest_framework import serializers
from .models import Transacao, Categoria, Conta
from django.contrib.auth.models import User
from .models import PerfilAluno
from .models import Transacao, Categoria, Conta, PerfilAluno, MetaFinanceira

class UserRegisterSerializer(serializers.ModelSerializer):
    
    serie_em = serializers.IntegerField(
        write_only=True, 
        min_value=1, 
        max_value=3,
        error_messages={'invalid': 'A série deve ser 1, 2 ou 3.'}
    ) 

    class Meta:
        model = User
        fields = ('username', 'password', 'serie_em') 
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        serie_em = validated_data.pop('serie_em') 
        user = User.objects.create_user(**validated_data)
        
        PerfilAluno.objects.create(
            usuario=user,
            serie_em=serie_em
        )
        return user

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

class MetaFinanceiraSerializer(serializers.ModelSerializer):
    valor_atual = serializers.SerializerMethodField()
    conta_nome = serializers.ReadOnlyField(source='conta_vinculada.nome') 
    
    class Meta:
        model = MetaFinanceira
        fields = [
            'id', 
            'nome', 
            'valor_alvo', 
            'data_alvo', 
            'ativa',
            'conta_vinculada', 
            'conta_nome',      
            'valor_atual',     
        ]
        read_only_fields = ('usuario',) 

    def get_valor_atual(self, obj):
        if obj.conta_vinculada:
            return obj.conta_vinculada.saldo_inicial 
        return 0.00