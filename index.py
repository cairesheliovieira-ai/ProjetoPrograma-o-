import sqlite3

import sqlite3, os

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
    con.commit(); con.close()
    print("Banco pronto!\n")

def con(): return sqlite3.connect(DB)

# ---------------- FUNÇÕES ---------------- #

def adicionar(id, nome, qtd, preco):
    if qtd < 0 or preco < 0:
        return print("Erro: Valores negativos não permitidos!")
    try:
        c = con()
        c.execute("INSERT INTO estoque VALUES (?,?,?,?,?)",
                  (str(id), nome, qtd, preco, qtd * preco))
        c.commit(); c.close()
        print(f"Produto '{nome}' adicionado!")
    except sqlite3.IntegrityError:
        print("Erro: ID já existe!")


def listar():
    c = con()
    rows = c.execute("SELECT codigo, nome_item, quantidade, preco_unitario FROM estoque ORDER BY codigo").fetchall()
    c.close()
    if not rows:
        return print("\nEstoque vazio.\n")
    print("\n======= ESTOQUE =======")
    for cod, nome, qtd, preco in rows:
        print(f"ID: {cod} | Nome: {nome} | Qtd: {qtd} | Preço: R$ {preco:.2f}")
    print("========================\n")


def atualizar(id, nova_qtd):
    if nova_qtd < 0:
        return print("Erro: Quantidade inválida!")
    c = con()
    row = c.execute("SELECT preco_unitario FROM estoque WHERE codigo=?", (str(id),)).fetchone()
    if not row:
        c.close(); return print("Erro: Produto não encontrado!")
    c.execute("UPDATE estoque SET quantidade=?, preco_total=? WHERE codigo=?",
              (nova_qtd, nova_qtd * row[0], str(id)))
    c.commit(); c.close()
    print("Quantidade atualizada!")


def remover(id):
    c = con()
    row = c.execute("SELECT nome_item FROM estoque WHERE codigo=?", (str(id),)).fetchone()
    if not row:
        c.close(); return print("Erro: Produto não encontrado!")
    c.execute("DELETE FROM estoque WHERE codigo=?", (str(id),))
    c.commit(); c.close()
    print(f"Produto '{row[0]}' removido!")


# ---------------- MENU ---------------- #

init_db()

while True:
    print("======= MENU =======\n1 - Adicionar\n2 - Listar\n3 - Atualizar Quantidade\n4 - Remover\n5 - Sair\n====================")
    op = input("Opção: ")

    if op == "1":
        try:
            adicionar(int(input("ID: ")), input("Nome: "), int(input("Quantidade: ")), float(input("Preço: ")))
        except ValueError:
            print("Erro: Valores inválidos!")

    elif op == "2":
        listar()

    elif op == "3":
        try:
            atualizar(int(input("ID: ")), int(input("Nova quantidade: ")))
        except ValueError:
            print("Erro: Valores inválidos!")

    elif op == "4":
        try:
            remover(int(input("ID: ")))
        except ValueError:
            print("Erro: ID inválido!")

    elif op == "5":
        print("Sistema encerrado."); break

    else:
        print("Opção inválida!")
