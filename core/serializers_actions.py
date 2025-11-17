from rest_framework import serializers
from .models import Conta


class TransferenciaSerializer(serializers.Serializer):
    conta_origem_id = serializers.IntegerField()
    conta_destino_id = serializers.IntegerField()
    valor = serializers.FloatField(min_value=0.01)

    def validate(self, data):
        user = self.context['request'].user

        try:
            origem = Conta.objects.get(id=data['conta_origem_id'], usuario=user)
            destino = Conta.objects.get(id=data['conta_destino_id'], usuario=user)
        except Conta.DoesNotExist:
            raise serializers.ValidationError("Uma das contas não existe ou não pertence ao usuário.")

        if origem.id == destino.id:
            raise serializers.ValidationError("A conta de origem e destino devem ser diferentes.")

        if origem.saldo_inicial < data['valor']:
            raise serializers.ValidationError("Saldo insuficiente na conta de origem.")

        data['origem'] = origem
        data['destino'] = destino
        return data

class DepositoMetaSerializer(serializers.Serializer):
    valor = serializers.FloatField(min_value=0.01)

    def validate(self, data):
        return data

class ConfirmarRecebimentoSerializer(serializers.Serializer):
    mes = serializers.IntegerField(required=False, min_value=1, max_value=12)
    ano = serializers.IntegerField(required=False, min_value=2000)

    def validate(self, data):
        return data
