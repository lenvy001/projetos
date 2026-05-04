# teste_db.py  — cria esse arquivo e roda
from database import tabela_ganhos, tabela_gastos, tabela_reserva

with tabela_ganhos() as db:
    print("GANHOS:", db.obter())

with tabela_gastos() as db:
    print("GASTOS:", db.obter())

with tabela_reserva() as db:
    print("RESERVA:", db.obter())