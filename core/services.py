from django.db import transaction
from django.utils import timezone
from .models import Transacao, Categoria, Conta

@transaction.atomic
def transferir_saldo(usuario, origem: Conta, destino: Conta, valor: float):
    origem.saldo_inicial -= valor
    destino.saldo_inicial += valor
    origem.save()
    destino.save()

    cat_saida, _ = Categoria.objects.get_or_create(
        usuario=usuario,
        nome="Transferência (Saída)",
        defaults={"tipo_categoria": "saida"}
    )

    cat_entrada, _ = Categoria.objects.get_or_create(
        usuario=usuario,
        nome="Transferência (Entrada)",
        defaults={"tipo_categoria": "entrada"}
    )

    hoje = timezone.localdate()

    Transacao.objects.create(
        usuario=usuario,
        conta=origem,
        categoria=cat_saida,
        tipo="saida",
        valor=valor,
        descricao=f"Transferência para {destino.nome}",
        pago=True,
        data=hoje
    )

    Transacao.objects.create(
        usuario=usuario,
        conta=destino,
        categoria=cat_entrada,
        tipo="entrada",
        valor=valor,
        descricao=f"Transferência de {origem.nome}",
        pago=True,
        data=hoje
    )

@transaction.atomic
def depositar_em_meta(usuario, meta, valor: float):

    conta_principal = Conta.objects.filter(usuario=usuario).order_by('id').first()
    if not conta_principal:
        raise ValueError("Nenhuma conta principal encontrada.")

    if conta_principal.saldo_inicial < valor:
        raise ValueError("Saldo insuficiente na conta principal.")

    conta_meta = meta.conta_vinculada
    if not conta_meta:
        raise ValueError("Meta financeira não possui conta vinculada.")

    conta_principal.saldo_inicial -= valor
    conta_principal.save()
    conta_meta.saldo_inicial += valor
    conta_meta.save()

    cat_saida, _ = Categoria.objects.get_or_create(
        usuario=usuario,
        nome="Depósito em Meta (Saída)",
        defaults={"tipo_categoria": "saida"}
    )

    cat_entrada, _ = Categoria.objects.get_or_create(
        usuario=usuario,
        nome="Depósito em Meta (Entrada)",
        defaults={"tipo_categoria": "entrada"}
    )

    hoje = timezone.localdate()

    Transacao.objects.create(
        usuario=usuario,
        conta=conta_principal,
        categoria=cat_saida,
        tipo="saida",
        valor=valor,
        pago=True,
        descricao=f"Depósito para meta: {meta.nome}",
        data=hoje
    )

    Transacao.objects.create(
        usuario=usuario,
        conta=conta_meta,
        categoria=cat_entrada,
        tipo="entrada",
        valor=valor,
        pago=True,
        descricao=f"Depósito recebido para meta: {meta.nome}",
        data=hoje
    )

@transaction.atomic
def confirmar_recebimento_pede_meia(usuario, mes, ano):

    transacao = Transacao.objects.filter(
        usuario=usuario,
        tipo='entrada',
        pago=False,
        data__month=mes,
        data__year=ano,
        descricao__startswith="Frequência"
    ).order_by('data').first()

    if not transacao:
        raise ValueError("Nenhuma parcela pendente para esse mês.")

    transacao.pago = True
    transacao.save()
    conta = transacao.conta
    conta.saldo_inicial += transacao.valor
    conta.save()

    return transacao
