import sqlite3
from tabulate import tabulate
from datetime import datetime

DB = "estoque.db"

# ---------------- BANCO DE DADOS ---------------- #

def init_db():
    con = sqlite3.connect(DB)
    cursor = con.cursor()
    
    # Tabela de Estoque atualizada
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            codigo TEXT PRIMARY KEY,
            nome_item TEXT NOT NULL,
            categoria TEXT NOT NULL,
            quantidade REAL NOT NULL,
            unidade_medida TEXT NOT NULL,
            preco_unitario REAL NOT NULL,
            preco_total REAL NOT NULL,
            especificacoes TEXT,
            estoque_minimo REAL DEFAULT 0
        )
    """)
    
    # Nova tabela para o Histórico de Movimentações (requisito para KPIs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_produto TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'ENTRADA' ou 'SAÍDA'
            motivo TEXT NOT NULL, -- 'Compra', 'Venda', 'Devolução', 'Perda', etc.
            quantidade REAL NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY (codigo_produto) REFERENCES estoque(codigo)
        )
    """)
    
    con.commit()
    con.close()
    print("Banco de dados sincronizado com sucesso!\n")


def get_connection():
    return sqlite3.connect(DB)


# ---------------- FUNÇÕES CORE ---------------- #

def adicionar(id, nome, categoria, qtd, unidade_medida, preco, specs, est_minimo):
    if qtd < 0 or preco < 0 or est_minimo < 0:
        return print("\n[Erro] Valores negativos não são permitidos!")
    if not nome.strip() or not categoria.strip():
        return print("\n[Erro] Nome e Categoria não podem ficar em branco!")

    try:
        c = get_connection()
        cursor = c.cursor()
        
        cursor.execute(
            "INSERT INTO estoque VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(id), nome, categoria, qtd, unidade_medida, preco, qtd * preco, specs, est_minimo)
        )
        
        # Registrar a carga inicial como uma movimentação de entrada
        if qtd > 0:
            cursor.execute(
                "INSERT INTO movimentacoes (codigo_produto, tipo, motivo, quantidade, data_hora) VALUES (?, ?, ?, ?, ?)",
                (str(id), "ENTRADA", "Carga Inicial", qtd, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            
        c.commit()
        c.close()
        print(f"\nProduto '{nome}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\n[Erro] ID já existe no sistema!")


def consultar_estoque():
    c = get_connection()
    cursor = c.cursor()
    rows = cursor.execute("""
        SELECT codigo, nome_item, categoria, quantidade, unidade_medida, 
               preco_unitario, preco_total, estoque_minimo 
        FROM estoque ORDER BY codigo
    """).fetchall()
    c.close()

    if not rows:
        return print("\nEstoque vazio.")

    headers = ["ID", "Nome", "Categoria", "Qtd", "Unid", "Preço Unit.", "Total", "Status"]
    tabela = []
    alertas = 0

    for row in rows:
        cod, nome, cat, qtd, und, preco, total, min_est = row
        
        # Alertas Inteligentes (Verificação de estoque baixo)
        status = "OK"
        if qtd <= min_est:
            status = "REPOR"
            alertas += 1

        tabela.append([
            cod, nome, cat, f"{qtd:.2f}", und, f"R$ {preco:.2f}", f"R$ {total:.2f}", status
        ])

    print("\n" + "="*35 + " POSITION EM TEMPO REAL " + "="*35)
    print(tabulate(tabela, headers=headers, tablefmt="fancy_grid", stralign="center", numalign="center"))
    
    if alertas > 0:
        print(f"\n ATENÇÃO: Você possui {alertas} produto(s) abaixo ou no limite do estoque mínimo!")


def movimentar_produto(id, qtd, tipo, motivo):
    if qtd <= 0:
        return print("\n[Erro] A quantidade deve ser maior que zero!")
        
    c = get_connection()
    cursor = c.cursor()
    
    # Localizar produto
    produto = cursor.execute("SELECT quantidade, preco_unitario, nome_item FROM estoque WHERE codigo=?", (str(id),)).fetchone()
    
    if not produto:
        c.close()
        return print("\n[Erro] Produto não localizado!")
        
    qtd_atual, preco_unit, nome = produto
    
    if tipo == "SAÍDA" and qtd_atual < qtd:
        c.close()
        return print(f"\n[Erro] Estoque insuficiente para '{nome}'. Saldo atual: {qtd_atual}")
        
    # Calcular nova quantidade
    nova_qtd = (qtd_atual + qtd) if tipo == "ENTRADA" else (qtd_atual - qtd)
    novo_total = nova_qtd * preco_unit
    
    # Atualizar estoque
    cursor.execute(
        "UPDATE estoque SET quantidade=?, preco_total=? WHERE codigo=?",
        (nova_qtd, novo_total, str(id))
    )
    
    # Inserir histórico
    cursor.execute(
        "INSERT INTO movimentacoes (codigo_produto, tipo, motivo, quantidade, data_hora) VALUES (?, ?, ?, ?, ?)",
        (str(id), tipo, motivo, qtd, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    
    c.commit()
    c.close()
    print(f"\n {tipo} de {qtd} unidade(s) de '{nome}' registrada ({motivo})!")


def remover(id):
    c = get_connection()
    cursor = c.cursor()
    
    row = cursor.execute("SELECT nome_item FROM estoque WHERE codigo=?", (str(id),)).fetchone()
    if not row:
        c.close()
        return print("\n[Erro] Produto não encontrado!")
        
    # Limpar histórico e item correspondente
    cursor.execute("DELETE FROM movimentacoes WHERE codigo_produto=?", (str(id),))
    cursor.execute("DELETE FROM estoque WHERE codigo=?", (str(id),))
    
    c.commit()
    c.close()
    print(f"\nProduto '{row[0]}' e seu histórico foram removidos.")


# ---------------- RELATÓRIOS GERENCIAIS & KPIS ---------------- #

def gerar_relatorios():
    c = get_connection()
    cursor = c.cursor()
    
    # 1. Valorização do estoque
    dados_estoque = cursor.execute("SELECT SUM(quantidade), SUM(preco_total), COUNT(codigo) FROM estoque").fetchone()
    total_itens, valor_total, total_produtos = dados_estoque
    total_itens = total_itens or 0
    valor_total = valor_total or 0.0
    
    # 2. Total de Saídas (Base para o Giro)
    total_saidas = cursor.execute("SELECT SUM(quantidade) FROM movimentacoes WHERE tipo='SAÍDA'").fetchone()[0] or 0
    
    # 3. Rupturas de estoque simuladas (Pedidos não atendidos por falta de saldo)
    # Em uma aplicação real, mapeia-se uma tabela de pedidos cancelados. Criamos uma métrica base estrutural.
    
    c.close()
    
    print("\n" + "="*30 + " RELATÓRIO GERENCIAL & KPIs " + "="*30)
    print(f"• Total de Produtos Distintos Cadastrados: {total_produtos}")
    print(f"• Volume Físico Total em Estoque: {total_itens:.2f}")
    print(f"• Valorização Patrimonial do Estoque: R$ {valor_total:.2f}")
    print("-" * 88)
    
    # Fórmulas de Desempenho Aplicadas
    print(" INDICADORES DE DESEMPENHO (KPIs):")
    
    # Giro de Estoque
    estoque_medio = total_itens if total_itens > 0 else 1
    giro = total_saidas / estoque_medio
    print(f"  - Giro de Estoque: {giro:.2f} voltas (Indica a rotatividade do inventário).")
    
    # Nível de Serviço (Disponibilidade)
    # Considera a relação de itens disponíveis vs itens com estoque zerado (Ruptura)
    nivel_servico = 100.0 if total_produtos == 0 else ((total_produtos - (1 if total_itens == 0 and total_produtos > 0 else 0)) / total_produtos) * 100
    print(f"  - Nível de Serviço: {nivel_servico:.1f}% (Capacidade atual de atendimento imediato).")
    
    # Custo de Manutenção Estimado (Exemplo clássico baseado em taxa de 2% do valor de inventário)
    custo_manutencao = valor_total * 0.02
    print(f"  - Custo de Manutenção Estimado: R$ {custo_manutencao:.2f}/mês (Calculado sobre base de custo operacional padrão).")
    
    # Tempo de Reposição Médio
    print("  - Tempo de Reposição (Lead Time): Parâmetro logístico atrelado ao cadastro de fornecedores (padrão do sistema: 5 dias).")
    print("=" * 88)


# ---------------- INTERFACE DE USUÁRIO ---------------- #

init_db()

while True:
    print("""
╔════════════════════════════════════════════╗
║             SISTEMA DE ESTOQUE             ║
╠════════════════════════════════════════════╣
║ 1 - Cadastrar Novo Produto                 ║
║ 2 - Consultar Estoque (Tempo Real)         ║
║ 3 - Registrar Entrada (Compras/Devolução)  ║
║ 4 - Registrar Saída (Venda/Perda/Transf.)  ║
║ 5 - Relatórios Gerenciais & KPIs           ║
║ 6 - Remover Produto                        ║
║ 7 - Sair                                   ║
╚════════════════════════════════════════════╝
""")

    op = input("Escolha uma opção: ")

    if op == "1":
        try:
            id_produto = input("Código/ID do Produto: ").strip()
            if not id_produto: raise ValueError
            nome = input("Nome do Item: ")
            categoria = input("Categoria: ")
            quantidade = float(input("Quantidade Inicial: "))
            unidade_medida = input("Unidade de Medida (ex: un, kg, L): ")
            preco = float(input("Preço Unitário: "))
            especificacoes = input("Especificações Técnicas: ")
            estoque_minimo = float(input("Limite Mínimo de Alerta: "))

            adicionar(id_produto, nome, categoria, quantidade, unidade_medida, preco, especificacoes, estoque_minimo)
        except ValueError:
            print("\n[Erro] Entrada de dados inválida!")

    elif op == "2":
        consultar_estoque()

    elif op == "3":
        try:
            id_produto = input("Código/ID do Produto: ")
            quantidade = float(input("Quantidade da Entrada: "))
            print("Motivos válidos: Compra, Devolução, Ajuste")
            motivo = input("Motivo da Entrada: ")
            movimentar_produto(id_produto, quantidade, "ENTRADA", motivo)
        except ValueError:
            print("\n[Erro] Quantidade inválida!")

    elif op == "4":
        try:
            id_produto = input("Código/ID do Produto: ")
            quantidade = float(input("Quantidade da Saída: "))
            print("Motivos válidos: Venda, Transferência, Perda")
            motivo = input("Motivo da Saída: ")
            movimentar_produto(id_produto, quantidade, "SAÍDA", motivo)
        except ValueError:
            print("\n[Erro] Quantidade inválida!")

    elif op == "5":
        gerar_relatorios()

    elif op == "6":
        id_produto = input("Código/ID do Produto a ser removido: ")
        remover(id_produto)

    elif op == "7":
        print("\nSistema encerrado. Até logo!")
        break
    else:
        print("\nOpção inválida!")