from .models import Transacao, Categoria, Conta
from datetime import date
from dateutil.relativedelta import relativedelta 

def automatizar_recebimentos_pede_meia(user, serie_aluno):
    
    VALOR_MATRICULA = 200.00
    VALOR_MENSAL = 200.00
    MESES_FREQUENCIA = 9

    conta_padrao = Conta.objects.filter(usuario=user).first()
    if not conta_padrao:
         conta_padrao = Conta.objects.create(usuario=user, nome="Principal", saldo_inicial=0.00)

    categoria_recebimento, created = Categoria.objects.get_or_create(
        usuario=user, 
        nome="Pé-de-Meia (Benefício)",
        defaults={'tipo_categoria': 'entrada'} 
    )

    hoje = date.today()
    mes_inicio_pagamento = 3
    ano_base = hoje.year
    data_matricula = date(ano_base, mes_inicio_pagamento, 30)
    
    Transacao.objects.create(
        usuario=user,
        conta=conta_padrao,
        categoria=categoria_recebimento,
        tipo='entrada',
        valor=VALOR_MATRICULA,
        data=data_matricula if data_matricula >= hoje else hoje, 
        descricao=f"Pé-de-Meia: Incentivo Matrícula - {serie_aluno}º Ano",
        pago=True 
    )

    data_inicio_mensal = date(ano_base, mes_inicio_pagamento, 1)
    
    for i in range(MESES_FREQUENCIA):
        data_recebimento = data_inicio_mensal + relativedelta(months=i)
        
        if data_recebimento.month >= hoje.month and data_recebimento.year == hoje.year:
            
            data_efetiva = data_recebimento.replace(day=28) 
            
            Transacao.objects.create(
                usuario=user,
                conta=conta_padrao,
                categoria=categoria_recebimento,
                tipo='entrada',
                valor=VALOR_MENSAL,
                data=data_efetiva,
                descricao=f"Pé-de-Meia: Frequência - {data_efetiva.strftime('%B/%Y')}",
                pago=True 
            )
            
    return True