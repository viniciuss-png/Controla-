from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=60)
    
    TIPO_CHOICES = [
        ('entrada', 'Receita'),
        ('saida', 'Despesa'),
    ]
    tipo_categoria = models.CharField(max_length=10, choices=TIPO_CHOICES, default='saida')
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) 
    
    def __str__(self):
        return f"[{self.get_tipo_categoria_display()}] {self.nome}"

    class Meta:
        verbose_name_plural = "Categorias"
        unique_together = ('nome', 'usuario')
        ordering = ['nome']

class Conta(models.Model):
    nome = models.CharField(max_length=60)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Contas"
        unique_together = ('nome', 'usuario')
        ordering = ['nome']


class Transacao(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT) 
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT)    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descricao = models.CharField(max_length=120)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    parcelas = models.IntegerField(default=1)
    vencimento = models.DateField(null=True, blank=True) 
    pago = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.tipo.upper()} - {self.descricao} - R$ {self.valor}"

    class Meta:
        ordering = ['-data'] 
        verbose_name_plural = "Transações"

class PerfilAluno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    
    SERIE_CHOICES = [
        (1, '1º Ano'), 
        (2, '2º Ano'), 
        (3, '3º Ano')
    ]
    serie_em = models.IntegerField(
        choices=SERIE_CHOICES,
        default=1,
        verbose_name="Série do Ensino Médio"
    )
    
    ano_registro = models.IntegerField(default=timezone.now().year)
    concluiu = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.usuario.username} - {self.get_serie_em_display()}"
    
class MetaFinanceira(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100) 
    valor_alvo = models.DecimalField(max_digits=10, decimal_places=2) 
    conta_vinculada = models.OneToOneField(
        Conta, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        help_text="Conta separada onde o dinheiro desta meta será depositado."
    )
    
    data_alvo = models.DateField(null=True, blank=True) 
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"Meta: {self.nome} de {self.usuario.username}"
        
    class Meta:
        verbose_name = "Meta Financeira"
        verbose_name_plural = "Metas Financeiras"
        ordering = ['data_alvo']