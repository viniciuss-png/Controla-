from .models import Incentivo, Transacao

def atualizar_incentivo_por_transacao(transacao: Transacao):
    incentivo = Incentivo.objects.filter(transacao=transacao).first()
    if incentivo:
        incentivo.valor = transacao.valor
        incentivo.conta = transacao.conta
        incentivo.ano = transacao.data.year
        incentivo.save()

def excluir_incentivo_por_transacao(transacao: Transacao):
    Incentivo.objects.filter(transacao=transacao).delete()
