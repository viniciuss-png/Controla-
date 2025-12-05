from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from django.core.exceptions import ValidationError


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
    saldo_atual = models.DecimalField(max_digits=12,decimal_places=2, default=0)
    
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_valor = self.valor
        self._original_tipo = self.tipo
        self._original_conta_id = self.conta_id
        self._original_pago = self.pago

    def __str__(self):
        return f"{self.tipo.upper()} - {self.descricao} - R$ {self.valor}"
    
    def clean(self):
        if self.valor <= 0:
            raise ValidationError("Valor da transação deve ser positivo")

    class Meta:
        ordering = ['-data'] 
        verbose_name_plural = "Transações"

class PerfilAluno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)

    email = models.EmailField()
    
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
    
    def clean(self):
        if self.valor_alvo <= 0:
            raise ValidationError("Valor alvo da meta deve ser positivo")
        
    class Meta:
        verbose_name = "Meta Financeira"
        verbose_name_plural = "Metas Financeiras"
        ordering = ['data_alvo']

class Lembrete(models.Model):
    RECOR_CHOICES = [
        ('nenhuma', 'Nenhuma'),
        ('diaria', 'Diária'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    data_lembrete = models.DateField(null=True, blank=True)
    dias_antes = models.IntegerField(default=0) 
    recorrencia = models.CharField(max_length=10, choices=RECOR_CHOICES, default='nenhuma')
    transacao = models.ForeignKey('Transacao', null=True, blank=True, on_delete=models.SET_NULL)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    ultimo_disparo = models.DateField(null=True, blank=True) 

    def __str__(self):
        return f"{self.titulo} ({self.usuario.username})"

class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.CharField(max_length=300)
    transacao = models.ForeignKey('Transacao', null=True, blank=True, on_delete=models.SET_NULL)
    criada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, null=True) 

    class Meta:
        ordering = ['-criada_em']


class Incentivo(models.Model):
    TIPO_CHOICES = [
        ('conclusao', 'Incentivo Conclusão'),
        ('enem', 'Incentivo ENEM'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    ano = models.IntegerField(null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    conta = models.ForeignKey(Conta, null=True, blank=True, on_delete=models.SET_NULL)
    transacao = models.ForeignKey(Transacao, null=True, blank=True, on_delete=models.SET_NULL)
    liberado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Incentivo"
        verbose_name_plural = "Incentivos"
        ordering = ['-criado_em']

    def __str__(self):
        return f"Incentivo {self.get_tipo_display()} - {self.usuario.username} - R$ {self.valor}"