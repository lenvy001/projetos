# main.py
from database import tabela_ganhos, tabela_gastos, tabela_reserva, resumo_financeiro

def menu():
    print("\n=============================")
    print("      FINANCEIRO PESSOAL     ")
    print("=============================")
    print("  1. Adicionar ganho")
    print("  2. Adicionar gasto")
    print("  3. Adicionar reserva")
    print("  4. Ver resumo do mês")
    print("  5. Sair")
    print("=============================")
    return input("  Escolha uma opção: ")

def adicionar_ganho():
    valor = float(input("Valor do ganho: R$ "))
    data  = input("Data (AAAA-MM-DD): ")
    with tabela_ganhos() as db:
        db.inserir(valor, data)
    print("✅ Ganho adicionado!")

def adicionar_gasto():
    valor     = float(input("Valor do gasto: R$ "))
    descricao = input("Descrição: ")
    data      = input("Data (AAAA-MM-DD): ")
    with tabela_gastos() as db:
        db.inserir(valor, descricao, data)
    print("✅ Gasto adicionado!")

def adicionar_reserva():
    valor = float(input("Valor da reserva: R$ "))
    data  = input("Data (AAAA-MM-DD): ")
    with tabela_reserva() as db:
        db.inserir(valor, data)
    print("✅ Reserva adicionada!")

def ver_resumo():
    ano = int(input("Ano (ex: 2024): "))
    mes = int(input("Mês (ex: 6): "))
    with resumo_financeiro() as db:
        r = db.obter_resumo(ano, mes)
    print("\n=============================")
    print(f"   RESUMO {mes:02d}/{ano}")
    print("=============================")
    print(f"  Ganhos:  R$ {r['total_ganhos']:.2f}")
    print(f"  Gastos:  R$ {r['total_gastos']:.2f}")
    print(f"  Reserva: R$ {r['total_reserva']:.2f}")
    print("-----------------------------")
    print(f"  Saldo:   R$ {r['saldo']:.2f}")
    print("=============================")

if __name__ == "__main__":
    opcoes = {
        "1": adicionar_ganho,
        "2": adicionar_gasto,
        "3": adicionar_reserva,
        "4": ver_resumo,
    }

    while True:
        opcao = menu()
        if opcao == "5":
            print("Saindo... até logo!")
            break
        elif opcao in opcoes:
            opcoes[opcao]()  # chama a função correspondente
        else:
            print("❌ Opção inválida!")