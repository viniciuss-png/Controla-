from django.db import models
from django.contrib.auth.models import User 


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