from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Transacao, Incentivo

@receiver(post_delete, sender=Transacao)
def delete_incentivo_on_transacao_delete(sender, instance, **kwargs):
    Incentivo.objects.filter(transacao=instance).delete()

@receiver(post_save, sender=Transacao)
def update_incentivo_on_transacao_update(sender, instance, **kwargs):
    # Atualiza os campos do incentivo para refletir mudanças na transação
    incentivo = Incentivo.objects.filter(transacao=instance).first()
    if incentivo:
        incentivo.valor = instance.valor
        incentivo.conta = instance.conta
        incentivo.save()
