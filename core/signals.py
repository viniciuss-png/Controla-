from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from .models import Transacao, Conta, PerfilAluno

def _apply_change_to_account(conta: Conta, delta):
    conta.saldo_atual = (conta.saldo_atual or Decimal('0.00')) + Decimal(delta)
    conta.save(update_fields=['saldo_atual'])


@receiver(post_save, sender=Transacao)
def transacao_post_save(sender, instance: Transacao, created, **kwargs):
    from decimal import Decimal

    if created:
        delta = Decimal(instance.valor)
        if instance.tipo == 'saida':
            delta = -delta
        _apply_change_to_account(instance.conta, delta)
    else:
        old_val = getattr(instance, '_original_valor', None)
        old_tipo = getattr(instance, '_original_tipo', None)
        old_conta_id = getattr(instance, '_original_conta_id', None)

        new_val = instance.valor
        new_tipo = instance.tipo
        new_conta_id = instance.conta_id

        if old_conta_id and old_conta_id != new_conta_id:
            try:
                old_conta = Conta.objects.get(pk=old_conta_id)
                old_delta = Decimal(old_val)
                if old_tipo == 'saida':
                    old_delta = -old_delta
                _apply_change_to_account(old_conta, -old_delta)  
            except Conta.DoesNotExist:
                pass

            new_delta = Decimal(new_val)
            if new_tipo == 'saida':
                new_delta = -new_delta
            _apply_change_to_account(instance.conta, new_delta)
        else:
            if old_val is None:
                delta = Decimal(new_val)
                if new_tipo == 'saida':
                    delta = -delta
                _apply_change_to_account(instance.conta, delta)
            else:
                old_effect = Decimal(old_val)
                if old_tipo == 'saida':
                    old_effect = -old_effect
                new_effect = Decimal(new_val)
                if new_tipo == 'saida':
                    new_effect = -new_effect
                delta_effect = new_effect - old_effect
                if delta_effect != 0:
                    _apply_change_to_account(instance.conta, delta_effect)

        instance._original_valor = instance.valor
        instance._original_tipo = instance.tipo
        instance._original_conta_id = instance.conta_id


@receiver(post_delete, sender=Transacao)
def transacao_post_delete(sender, instance: Transacao, **kwargs):
    from decimal import Decimal
    delta = Decimal(instance.valor)
    if instance.tipo == 'saida':
        delta = -delta
    try:
        conta = instance.conta
        _apply_change_to_account(conta, -delta)
    except Conta.DoesNotExist:
        pass