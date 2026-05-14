import sqlite3
from tabulate import tabulate

DB = "estoque.db"

# ---------------- BANCO ---------------- #

def init_db():
    con = sqlite3.connect(DB)

    con.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            codigo TEXT PRIMARY KEY,
            nome_item TEXT NOT NULL,
            quantidade REAL NOT NULL,
            preco_unitario REAL NOT NULL,
            preco_total REAL NOT NULL
        )
    """)

    con.commit()
    con.close()

    print("Banco pronto!\n")


def con():
    return sqlite3.connect(DB)


# ---------------- FUNÇÕES ---------------- #

def adicionar(id, nome, qtd, preco):

    if qtd < 0 or preco < 0:
        return print("Erro: Valores negativos não permitidos!")

    if not nome.strip():
        return print("Erro: Nome inválido!")

    try:
        c = con()

        c.execute(
            "INSERT INTO estoque VALUES (?,?,?,?,?)",
            (str(id), nome, qtd, preco, qtd * preco)
        )

        c.commit()
        c.close()

        print(f"\nProduto '{nome}' adicionado com sucesso!\n")

    except sqlite3.IntegrityError:
        print("\nErro: ID já existe!\n")


def listar():

    c = con()

    rows = c.execute("""
        SELECT codigo, nome_item, quantidade,
               preco_unitario, preco_total
        FROM estoque
        ORDER BY codigo
    """).fetchall()

    c.close()

    if not rows:
        return print("\nEstoque vazio.\n")

    headers = [
        "ID",
        "Nome",
        "Quantidade",
        "Preço Unitário",
        "Preço Total"
    ]

    tabela = []

    for cod, nome, qtd, preco, total in rows:

        tabela.append([
            cod,
            nome,
            qtd,
            f"R$ {preco:.2f}",
            f"R$ {total:.2f}"
        ])

    print("\n=========== ESTOQUE ===========\n")

    print(tabulate(
        tabela,
        headers=headers,
        tablefmt="fancy_grid",
        stralign="center",
        numalign="center"
    ))

    print()


def atualizar(id, nova_qtd):

    if nova_qtd < 0:
        return print("\nErro: Quantidade inválida!\n")

    c = con()

    row = c.execute(
        "SELECT preco_unitario FROM estoque WHERE codigo=?",
        (str(id),)
    ).fetchone()

    if not row:
        c.close()
        return print("\nErro: Produto não encontrado!\n")

    preco = row[0]

    c.execute(
        "UPDATE estoque SET quantidade=?, preco_total=? WHERE codigo=?",
        (nova_qtd, nova_qtd * preco, str(id))
    )

    c.commit()
    c.close()

    print("\nQuantidade atualizada com sucesso!\n")


def remover(id):

    c = con()

    row = c.execute(
        "SELECT nome_item FROM estoque WHERE codigo=?",
        (str(id),)
    ).fetchone()

    if not row:
        c.close()
        return print("\nErro: Produto não encontrado!\n")

    c.execute(
        "DELETE FROM estoque WHERE codigo=?",
        (str(id),)
    )

    c.commit()
    c.close()

    print(f"\nProduto '{row[0]}' removido com sucesso!\n")


# ---------------- MENU ---------------- #

init_db()

while True:

    print("""
╔════════════════════════════╗
║     SISTEMA DE ESTOQUE     ║
╠════════════════════════════╣
║ 1 - Adicionar Produto      ║
║ 2 - Listar Produtos        ║
║ 3 - Atualizar Quantidade   ║
║ 4 - Remover Produto        ║
║ 5 - Sair                   ║
╚════════════════════════════╝
""")

    op = input("Escolha uma opção: ")

    # -------- ADICIONAR -------- #

    if op == "1":

        try:

            id_produto = int(input("ID: "))
            nome = input("Nome: ")
            quantidade = int(input("Quantidade: "))
            preco = float(input("Preço: "))

            adicionar(id_produto, nome, quantidade, preco)

        except ValueError:
            print("\nErro: Valores inválidos!\n")

    # -------- LISTAR -------- #

    elif op == "2":

        listar()

    # -------- ATUALIZAR -------- #

    elif op == "3":

        try:

            id_produto = int(input("ID: "))
            nova_qtd = int(input("Nova quantidade: "))

            atualizar(id_produto, nova_qtd)

        except ValueError:
            print("\nErro: Valores inválidos!\n")

    # -------- REMOVER -------- #

    elif op == "4":

        try:

            id_produto = int(input("ID: "))

            remover(id_produto)

        except ValueError:
            print("\nErro: ID inválido!\n")

    # -------- SAIR -------- #

    elif op == "5":

        print("\nSistema encerrado.")
        break

    # -------- OPÇÃO INVÁLIDA -------- #

    else:

        print("\nOpção inválida!\n")
