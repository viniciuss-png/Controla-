from django.db import transaction
from django.utils import timezone
from .models import Transacao, Categoria, Conta, MetaFinanceira
from decimal import Decimal


class TransferenciaInvalidaError(Exception):
    pass

class DepositoMetaError(Exception):
    pass

class ConfirmacaoRecebimentoError(Exception):
    pass

def _obter_ou_criar_categoria(usuario, nome, tipo):
    categoria, _ = Categoria.objects.get_or_create(
        usuario=usuario,
        nome=nome,
        defaults={"tipo_categoria": tipo}
    )
    return categoria


def _criar_transacao_dupla(usuario, conta_saida, conta_entrada, valor, descricao_base):
    cat_saida = _obter_ou_criar_categoria(
        usuario, f"{descricao_base} (Saída)", "saida"
    )
    cat_entrada = _obter_ou_criar_categoria(
        usuario, f"{descricao_base} (Entrada)", "entrada"
    )
    
    hoje = timezone.localdate()
    
    transacao_saida = Transacao.objects.create(
        usuario=usuario,
        conta=conta_saida,
        categoria=cat_saida,
        tipo="saida",
        valor=valor,
        descricao=f"{descricao_base} para {conta_entrada.nome}",
        pago=True,
        data=hoje
    )
    
    transacao_entrada = Transacao.objects.create(
        usuario=usuario,
        conta=conta_entrada,
        categoria=cat_entrada,
        tipo="entrada",
        valor=valor,
        descricao=f"{descricao_base} de {conta_saida.nome}",
        pago=True,
        data=hoje
    )
    
    return transacao_saida, transacao_entrada


@transaction.atomic
def transferir_saldo(usuario, origem: Conta, destino: Conta, valor: float):
    valor = Decimal(str(valor))
    
    if valor <= 0:
        raise TransferenciaInvalidaError("O valor deve ser positivo.")
    
    if origem.id == destino.id:
        raise TransferenciaInvalidaError("As contas devem ser diferentes.")
    
    if origem.usuario != usuario or destino.usuario != usuario:
        raise TransferenciaInvalidaError("Contas não pertencem ao usuário.")
    
    if origem.saldo_inicial < valor:
        raise TransferenciaInvalidaError("Saldo insuficiente na conta de origem.")
    
    origem.saldo_inicial -= valor
    destino.saldo_inicial += valor
    origem.save()
    destino.save()
    
    return _criar_transacao_dupla(usuario, origem, destino, valor, "Transferência")


@transaction.atomic
def depositar_em_meta(usuario, meta: MetaFinanceira, valor: float):
    valor = Decimal(str(valor))
    
    if valor <= 0:
        raise DepositoMetaError("O valor deve ser positivo.")
    
    if meta.usuario != usuario:
        raise DepositoMetaError("Meta não pertence ao usuário.")
    
    if not meta.conta_vinculada:
        raise DepositoMetaError("Meta não possui conta vinculada.")
    
    if not meta.ativa:
        raise DepositoMetaError("Meta está inativa.")
    
    conta_principal = Conta.objects.filter(usuario=usuario).order_by('id').first()
    if not conta_principal:
        raise DepositoMetaError("Nenhuma conta encontrada para fazer o depósito.")
    
    if conta_principal.saldo_inicial < valor:
        raise DepositoMetaError("Saldo insuficiente na conta principal.")
    
    conta_principal.saldo_inicial -= valor
    conta_principal.save()
    
    meta.conta_vinculada.saldo_inicial += valor
    meta.conta_vinculada.save()
    
    return _criar_transacao_dupla(
        usuario, 
        conta_principal, 
        meta.conta_vinculada, 
        valor, 
        f"Depósito em Meta: {meta.nome}"
    )


@transaction.atomic
def confirmar_recebimento_pede_meia(usuario, mes: int, ano: int):
    if not (1 <= mes <= 12):
        raise ConfirmacaoRecebimentoError("Mês deve estar entre 1 e 12.")
    
    if ano < 2000 or ano > 2100:
        raise ConfirmacaoRecebimentoError("Ano inválido.")
    
    transacao = Transacao.objects.filter(
        usuario=usuario,
        tipo='entrada',
        pago=False,
        data__month=mes,
        data__year=ano,
        descricao__icontains="Pé-de-Meia"  
    ).order_by('data').first()
    
    if not transacao:
        raise ConfirmacaoRecebimentoError(
            f"Nenhuma parcela do Pé-de-Meia pendente para {mes}/{ano}."
        )
    
    transacao.pago = True
    transacao.save()
        
    return transacao
