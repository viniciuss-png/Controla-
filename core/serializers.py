from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Transacao,
    Categoria,
    Conta,
    PerfilAluno,
    MetaFinanceira
)

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários (estudantes).
    Aceita campos do frontend e mapeia para o modelo User + PerfilAluno.
    
    Campos aceitos:
    - username: identificador único (obrigatório)
    - password: senha (obrigatório, write_only)
    - nome: nome completo do estudante (obrigatório, mapeado para first_name)
    - ano_escolar: série (1-3), obrigatório (mapeado para PerfilAluno.serie_em)
    - email: email do estudante (opcional)
    """
    nome = serializers.CharField(
        max_length=150,
        required=True,
        write_only=True,  # Só entrada, não aparece na resposta
        help_text="Nome completo do estudante"
    )
    ano_escolar = serializers.IntegerField(
        write_only=True,  # Só entrada
        required=True,
        min_value=1,
        max_value=3,
        error_messages={
            'invalid': 'A série deve ser 1, 2 ou 3.',
            'required': 'O ano escolar é obrigatório.'
        }
    )
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'nome', 'email', 'ano_escolar', 'first_name')
        read_only_fields = ('id', 'first_name')  # first_name é read_only (não aceita input direto)
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'help_text': 'Identificador único para login'}
        }

    def validate_nome(self, value):
        """Valida se o nome tem pelo menos 3 caracteres"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "O nome deve ter pelo menos 3 caracteres."
            )
        return value.strip()

    def validate_username(self, value):
        """Valida se o username já existe"""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Este nome de usuário já está em uso."
            )
        return value.lower()

    def create(self, validated_data):
        """Cria novo usuário e seu perfil de aluno"""
        # Extrai campos customizados
        ano_escolar = validated_data.pop('ano_escolar')
        nome = validated_data.pop('nome')
        
        # Email é opcional
        email = validated_data.get('email') or f"{validated_data['username']}@pede-meia.edu.br"
        validated_data['email'] = email
        validated_data['first_name'] = nome
        
        # Cria o usuário
        user = User.objects.create_user(**validated_data)
        
        # Cria ou atualiza o PerfilAluno
        perfil, _ = PerfilAluno.objects.get_or_create(usuario=user)
        perfil.serie_em = ano_escolar
        perfil.save()

        return user

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'tipo_categoria']

    def validate_nome(self, value):
        user = self.context['request'].user
        qs = Categoria.objects.filter(usuario=user, nome__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Já existe uma categoria com esse nome.")
        return value


class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = ['id', 'nome', 'saldo_inicial']
        read_only_fields = ('usuario',)

    def validate_nome(self, value):
        user = self.context['request'].user
        qs = Conta.objects.filter(usuario=user, nome__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Já existe uma conta com esse nome.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return super().create({**validated_data, 'usuario': user})

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
            'categoria', 'categoria_nome', 'tipo_categoria',
            'conta', 'conta_nome'
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        conta = attrs.get('conta')
        categoria = attrs.get('categoria')

        if conta and conta.usuario != user:
            raise serializers.ValidationError({"conta": "Conta inválida para o usuário autenticado."})

        if categoria and categoria.usuario != user:
            raise serializers.ValidationError({"categoria": "Categoria inválida para o usuário autenticado."})

        return super().validate(attrs)

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        validated_data['usuario'] = user
        return super().create(validated_data)

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
        extra_kwargs = {
            "conta_vinculada": {"read_only": True}
        }

    def get_valor_atual(self, obj):
        if obj.conta_vinculada:
            return obj.conta_vinculada.saldo_inicial
        return 0.00

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['usuario'] = user
        return super().create(validated_data)