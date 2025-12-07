from django.db import transaction
from django.utils import timezone
from .models import Transacao, Categoria, Conta, MetaFinanceira, Incentivo
from decimal import Decimal
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime, timedelta
from django.db.models import Sum


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
        categoria__nome__iexact="Pé de Meia"
    ).order_by('data').first()

    if not transacao:
        raise ConfirmacaoRecebimentoError(
            f"Nenhuma parcela do Pé-de-Meia pendente para {mes}/{ano}."
        )

    transacao.pago = True
    transacao.save()  

    return transacao


@transaction.atomic
def criar_parcela_pede_meia(usuario, mes: int, ano: int, valor: float, conta: Conta = None, categoria_nome: str = "Pé de Meia"):
    """Cria uma transação de entrada pendente para uma parcela mensal do Pé-de-Meia.
    - descricao contém "Pé-de-Meia - MM/AAAA"
    - pago=False
    """
    if not (1 <= mes <= 12):
        raise ConfirmacaoRecebimentoError("Mês deve estar entre 1 e 12.")
    if ano < 2000 or ano > 2100:
        raise ConfirmacaoRecebimentoError("Ano inválido.")

    # Evita duplicar: já existe parcela (paga ou pendente) neste mês/ano
    existente = Transacao.objects.filter(
        usuario=usuario,
        tipo='entrada',
        data__month=mes,
        data__year=ano,
        categoria__nome__iexact="Pé de Meia"
    ).exists()
    if existente:
        raise ConfirmacaoRecebimentoError("A parcela do mês atual já foi registrada.")

    if conta is None:
        conta = Conta.objects.filter(usuario=usuario).order_by('id').first()
    if not conta:
        raise ConfirmacaoRecebimentoError("Nenhuma conta encontrada para creditar a parcela.")

    categoria = _obter_ou_criar_categoria(usuario, categoria_nome, 'entrada')
    # Registrar o dia real de criação da transação
    data_criacao = timezone.localdate()

    transacao = Transacao.objects.create(
        usuario=usuario,
        conta=conta,
        categoria=categoria,
        tipo='entrada',
        valor=Decimal('200.00'),
        data=data_criacao,
        descricao="Parcela Mensal",
        pago=False,
        parcelas=1,
        vencimento=None,
    )

    # Registrar também o incentivo na tabela Incentivo
    incentivo = Incentivo.objects.create(
        usuario=usuario,
        tipo='pede_meia',
        ano=ano,
        valor=Decimal('200.00'),
        conta=conta,
        transacao=transacao,
        liberado=True,
    )

    return transacao


@transaction.atomic
def criar_incentivo_conclusao(usuario, ano: int, conta: Conta = None):
    """Cria registro de incentivo de conclusão (bloqueado até liberação)."""
    if Incentivo.objects.filter(usuario=usuario, tipo='conclusao', ano=ano).exists():
        raise DepositoMetaError("Incentivo de conclusão já concedido para esse ano.")

    valor = Decimal('1000.00')
    if conta is None:
        conta = Conta.objects.filter(usuario=usuario).order_by('id').first()

    incentivo = Incentivo.objects.create(
        usuario=usuario,
        tipo='conclusao',
        ano=ano,
        valor=valor,
        conta=conta,
        liberado=False
    )

    return incentivo


@transaction.atomic
def liberar_incentivo_conclusao(incentivo: Incentivo):
    """Libera o incentivo de conclusão criando a transação correspondente."""
    if incentivo.liberado:
        raise DepositoMetaError("Incentivo já liberado.")

    conta = incentivo.conta or Conta.objects.filter(usuario=incentivo.usuario).order_by('id').first()
    if not conta:
        raise DepositoMetaError("Nenhuma conta encontrada para creditar o incentivo.")

    categoria = _obter_ou_criar_categoria(incentivo.usuario, "Incentivo Conclusão", "entrada")
    hoje = timezone.localdate()

    transacao = Transacao.objects.create(
        usuario=incentivo.usuario,
        conta=conta,
        categoria=categoria,
        tipo='entrada',
        valor=incentivo.valor,
        data=hoje,
        descricao=f"Incentivo Conclusão - Ano {incentivo.ano}",
        pago=True
    )

    incentivo.transacao = transacao
    incentivo.liberado = True
    incentivo.save()

    return incentivo, transacao


@transaction.atomic
def criar_incentivo_enem(usuario, conta: Conta = None, ano: int = None):
    """Concede incentivo ENEM imediatamente como transação disponível."""
    valor = Decimal('200.00')
    if conta is None:
        conta = Conta.objects.filter(usuario=usuario).order_by('id').first()

    if not conta:
        raise DepositoMetaError("Nenhuma conta encontrada para creditar o incentivo ENEM.")

    # Verifica se já existe incentivo ENEM liberado para o ano
    if Incentivo.objects.filter(usuario=usuario, tipo='enem', ano=ano).exists():
        raise DepositoMetaError(f"O benefício ENEM já foi recebido no ano {ano}.")

    categoria = _obter_ou_criar_categoria(usuario, "Incentivo ENEM", "entrada")
    hoje = timezone.localdate()

    transacao = Transacao.objects.create(
        usuario=usuario,
        conta=conta,
        categoria=categoria,
        tipo='entrada',
        valor=valor,
        data=hoje,
        descricao=f"Incentivo ENEM{(' - ' + str(ano)) if ano else ''}",
        pago=True
    )

    incentivo = Incentivo.objects.create(
        usuario=usuario,
        tipo='enem',
        ano=ano,
        valor=valor,
        conta=conta,
        transacao=transacao,
        liberado=True
    )

    return incentivo, transacao


def gerar_relatorio_financeiro_pdf(usuario, from_date=None, to_date=None):
    """
    Gera relatório financeiro em PDF com resumo, gráficos de dados e transações.
    
    Args:
        usuario: Usuário do Django
        from_date: Data inicial (datetime.date) - opcional
        to_date: Data final (datetime.date) - opcional
    
    Returns:
        BytesIO com PDF gerado
    """
    # Preparar filtros
    filters = {"usuario": usuario}
    if from_date:
        filters["data__gte"] = from_date
    if to_date:
        filters["data__lte"] = to_date
    
    # Calcular resumo financeiro
    total_entradas = (
        Transacao.objects.filter(**filters, tipo="entrada", pago=True)
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )
    
    total_saidas = (
        Transacao.objects.filter(**filters, tipo="saida", pago=True)
        .aggregate(Sum("valor"))["valor__sum"] or 0
    )
    
    saldo_liquido = total_entradas - total_saidas
    
    # Gastos por categoria
    gastos_categoria = list(
        Transacao.objects.filter(**filters, tipo="saida", pago=True)
        .values('categoria__nome')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )
    
    # Entradas Pé-de-Meia (recebidas)
    total_pede_meia = (
        Transacao.objects.filter(
            usuario=usuario,
            tipo='entrada',
            pago=True,
            categoria__nome__iexact="Pé de Meia"
        ).aggregate(Sum('valor'))['valor__sum'] or 0
    )
    
    # Saldos por conta
    saldos_contas = list(
        Conta.objects.filter(usuario=usuario)
        .values('nome', 'saldo_atual')
        .order_by('nome')
    )
    
    # Transações recentes (últimas 20)
    transacoes_recentes = list(
        Transacao.objects.filter(**filters)
        .values('data', 'tipo', 'descricao', 'valor', 'categoria__nome')
        .order_by('-data')[:20]
    )
    
    # Criar PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    # Construir elementos do PDF
    elements = []
    
    # Título
    elements.append(Paragraph("RELATÓRIO FINANCEIRO", title_style))
    elements.append(Paragraph(f"Usuário: {usuario.username}", styles['Normal']))
    
    data_str = ""
    if from_date and to_date:
        data_str = f"Período: {from_date.strftime('%d/%m/%Y')} a {to_date.strftime('%d/%m/%Y')}"
    elif from_date:
        data_str = f"A partir de: {from_date.strftime('%d/%m/%Y')}"
    elif to_date:
        data_str = f"Até: {to_date.strftime('%d/%m/%Y')}"
    else:
        data_str = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
    
    elements.append(Paragraph(data_str, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Resumo financeiro - Tabela
    elements.append(Paragraph("RESUMO FINANCEIRO", heading_style))
    resumo_data = [
        ['Métrica', 'Valor'],
        ['Total de Entradas', f'R$ {float(total_entradas):,.2f}'],
        ['Total de Saídas', f'R$ {float(total_saidas):,.2f}'],
        ['Saldo Líquido', f'R$ {float(saldo_liquido):,.2f}'],
        ['Pé-de-Meia Recebido', f'R$ {float(total_pede_meia):,.2f}'],
    ]
    
    resumo_table = Table(resumo_data, colWidths=[3*inch, 2*inch])
    resumo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
    ]))
    elements.append(resumo_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Gastos por categoria
    if gastos_categoria:
        elements.append(Paragraph("GASTOS POR CATEGORIA", heading_style))
        gastos_data = [['Categoria', 'Total']]
        for item in gastos_categoria[:10]:  # Top 10
            gastos_data.append([
                item['categoria__nome'],
                f"R$ {float(item['total']):,.2f}"
            ])
        
        gastos_table = Table(gastos_data, colWidths=[3*inch, 2*inch])
        gastos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
        ]))
        elements.append(gastos_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Saldos por conta
    if saldos_contas:
        elements.append(Paragraph("SALDOS POR CONTA", heading_style))
        saldos_data = [['Conta', 'Saldo']]
        for conta in saldos_contas:
            saldos_data.append([
                conta['nome'],
                f"R$ {float(conta['saldo_atual']):,.2f}"
            ])
        
        saldos_table = Table(saldos_data, colWidths=[3*inch, 2*inch])
        saldos_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
        ]))
        elements.append(saldos_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Transações recentes
    if transacoes_recentes:
        elements.append(PageBreak())
        elements.append(Paragraph("TRANSAÇÕES RECENTES", heading_style))
        
        trans_data = [['Data', 'Tipo', 'Descrição', 'Categoria', 'Valor']]
        for trans in transacoes_recentes:
            tipo_display = "Entrada" if trans['tipo'] == 'entrada' else "Saída"
            trans_data.append([
                trans['data'].strftime('%d/%m/%Y'),
                tipo_display,
                trans['descricao'][:20] + ('...' if len(trans['descricao']) > 20 else ''),
                trans['categoria__nome'][:15] + ('...' if len(trans['categoria__nome']) > 15 else ''),
                f"R$ {float(trans['valor']):,.2f}"
            ])
        
        trans_table = Table(trans_data, colWidths=[0.8*inch, 0.8*inch, 1.5*inch, 1.2*inch, 0.8*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
        ]))
        elements.append(trans_table)
    
    # Rodapé
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        f"<i>Documento gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</i>",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Gerar PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


def obter_dados_dashboard(usuario, from_date=None, to_date=None):
    """
    Retorna dados otimizados para dashboard do frontend.
    
    Args:
        usuario: Usuário do Django
        from_date: Data inicial (datetime.date) - opcional
        to_date: Data final (datetime.date) - opcional
    
    Returns:
        Dict com estrutura pronta para frontend
    """
    filters = {"usuario": usuario}
    if from_date:
        filters["data__gte"] = from_date
    if to_date:
        filters["data__lte"] = to_date
    
    # Totalizadores
    total_entradas = (
        Transacao.objects.filter(**filters, tipo="entrada", pago=True)
        .aggregate(Sum("valor"))["valor__sum"] or Decimal('0')
    )
    total_saidas = (
        Transacao.objects.filter(**filters, tipo="saida", pago=True)
        .aggregate(Sum("valor"))["valor__sum"] or Decimal('0')
    )
    saldo_liquido = total_entradas - total_saidas
    
    # Gastos por categoria (para gráfico)
    gastos_categoria = list(
        Transacao.objects.filter(**filters, tipo="saida", pago=True)
        .values('categoria__nome')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )
    
    # Entradas por categoria (para gráfico)
    entradas_categoria = list(
        Transacao.objects.filter(**filters, tipo="entrada", pago=True)
        .values('categoria__nome')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )
    
    # Pé-de-Meia + Incentivo Conclusão
    pede_meia_recebido = (
        Transacao.objects.filter(
            usuario=usuario,
            tipo='entrada',
            pago=True,
            categoria__nome__in=["Pé de Meia", "Incentivo Conclusão", "Incentivo ENEM"]
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    )
    
    pede_meia_pendente = (
        Transacao.objects.filter(
            usuario=usuario,
            tipo='entrada',
            pago=False,
            categoria__nome__iexact="Pé de Meia"
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0')
    )

    # Última transação de Pé-de-Meia (para exibir junto dos incentivos)
    pede_meia_ultima = (
        Transacao.objects.filter(
            usuario=usuario,
            tipo='entrada',
            categoria__nome__iexact="Pé de Meia"
        )
        .values('id', 'data', 'descricao', 'valor', 'pago', 'categoria__nome')
        .order_by('-data', '-id')
        .first()
    )
    
    # Incentivos
    incentivos_conclusao = list(
        Incentivo.objects.filter(usuario=usuario, tipo='conclusao')
        .values('id', 'ano', 'valor', 'liberado', 'criado_em')
    )
    
    incentivos_enem = list(
        Incentivo.objects.filter(usuario=usuario, tipo='enem')
        .values('id', 'ano', 'valor', 'liberado', 'criado_em')
    )
    
    # Saldos por conta
    saldos_contas = list(
        Conta.objects.filter(usuario=usuario)
        .values('id', 'nome', 'saldo_inicial', 'saldo_atual')
        .order_by('nome')
    )
    
    # Metas financeiras
    metas = list(
        MetaFinanceira.objects.filter(usuario=usuario)
        .values('id', 'nome', 'valor_alvo', 'data_alvo', 'ativa')
    )
    
    # Transações recentes
    transacoes_recentes = list(
        Transacao.objects.filter(**filters)
        .values('id', 'data', 'tipo', 'descricao', 'valor', 'categoria__nome', 'pago')
        .order_by('-data')[:15]
    )
    
    # Converter Decimal para float para JSON serialization
    def convert_decimals(obj):
        if isinstance(obj, list):
            return [convert_decimals(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: float(v) if isinstance(v, Decimal) else v for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj
    
    dashboard_data = {
        "resumo": {
            "total_entradas": float(total_entradas),
            "total_saidas": float(total_saidas),
            "saldo_liquido": float(saldo_liquido),
            "pede_meia_recebido": float(pede_meia_recebido),
            "pede_meia_pendente": float(pede_meia_pendente),
        },
        "graficos": {
            "gastos_categoria": convert_decimals(gastos_categoria),
            "entradas_categoria": convert_decimals(entradas_categoria),
        },
        "incentivos": {
            "conclusao": convert_decimals(incentivos_conclusao),
            "enem": convert_decimals(incentivos_enem),
            "pede_meia": convert_decimals(pede_meia_ultima) if pede_meia_ultima else None,
        },
        "contas": convert_decimals(saldos_contas),
        "metas": convert_decimals(metas),
        "transacoes_recentes": convert_decimals(transacoes_recentes),
    }
    
    return dashboard_data