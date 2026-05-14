estoque = {}

def adicionar(id, nome, qtd, preco):
    if id in estoque:
        print("Erro: Esse ID já existe!")
    else:
        estoque[id] = {
            "nome": nome,
            "quantidade": qtd,
            "preco": preco
        }
        print(f"{nome} adicionado com sucesso!")

def listar():
    if not estoque:
        print("\n O estoque está vazio.")
    else:
        print("\n--- ESTOQUE ATUAL ---")
        for id, dados in estoque.items():
            print(f"ID: {id} | Nome: {dados[0]} | Qtd: {dados[1]} | R$: {dados[2]:.2f}")
        print("------------------------\n")

def atualizar(id, nova_qtd):
    if id in estoque:
        estoque[id][1] = nova_qtd  # O índice 1 é onde guardamos a quantidade
        print(f"Quantidade do ID {id} atualizada para {nova_qtd}.")
    else:
        print("Erro: Produto não encontrado!")

def remover(id):
    if id in estoque:
        item = estoque.pop(id)
        print(f"Produto '{item[0]}' removido com sucesso!")
    else:
        print("Erro: Produto não encontrado!")

# --- MENU INTERATIVO ---
while True:
    print("\n--- MENU DE GERENCIAMENTO ---")
    print("1. Adicionar Produto")
    print("2. Listar Estoque")
    print("3. Atualizar Quantidade")
    print("4. Remover Produto")
    print("5. Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        try:
            id_prod = int(input("Digite o ID (número): "))
            nome_prod = input("Digite o nome do produto: ")
            qtd_prod = int(input("Digite a quantidade: "))
            preco_prod = float(input("Digite o preço: "))
            adicionar(id_prod, nome_prod, qtd_prod, preco_prod)
        except ValueError:
            print("Erro: Use apenas números para ID, Qtd e Preço!")

    elif opcao == "2":
        listar()

    elif opcao == "3":
        try:
            id_prod = int(input("Digite o ID do produto que deseja atualizar: "))
            nova_qtd = int(input("Digite a nova quantidade total: "))
            atualizar(id_prod, nova_qtd)
        except ValueError:
            print("Erro: Digite números válidos!")

    elif opcao == "4":
        try:
            id_prod = int(input("Digite o ID do produto que deseja remover: "))
            remover(id_prod)
        except ValueError:
            print("Erro: Digite um ID numérico válido!")

    elif opcao == "5":
        print("Saindo do sistema... Até logo!")
        break
    else:
        print("🚫 Opção inválida! Tente novamente.")