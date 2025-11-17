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
        perfil, _ = PerfilAluno.objects.get_or_create(usuario=user)
        perfil.serie_em = serie_em
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