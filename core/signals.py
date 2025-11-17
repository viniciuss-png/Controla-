from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilAluno

@receiver(post_save, sender=User)
def criar_perfil_aluno(sender, instance, created, **kwargs):
    if created:
        PerfilAluno.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def salvar_perfil_aluno(sender, instance, **kwargs):
    if hasattr(instance, 'perfilaluno'):
        instance.perfilaluno.save()