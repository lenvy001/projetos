import sqlite3

class banco_de_dados:
    def __init__(self):
        self.conexao = sqlite3.connect('financeiro.db')
        self.cursor = self.conexao.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS ganhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valor REAL NOT NULL,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valor REAL NOT NULL,
                descricao TEXT NOT NULL,
                data TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reserva (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                valor REAL NOT NULL,
                data TEXT NOT NULL
            );
        ''')
        self.conexao.commit()

    def fechar(self):
        self.conexao.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fechar()


class tabela_ganhos(banco_de_dados):
    def inserir(self, valor, data):
        self.cursor.execute(
            'INSERT INTO ganhos (valor, data) VALUES (?, ?)', (valor, data))
        self.conexao.commit()

    def obter(self):
        self.cursor.execute('SELECT * FROM ganhos')
        return self.cursor.fetchall()

    def total_mes(self, ano, mes):
        periodo = f"{ano}-{mes:02d}%"
        self.cursor.execute(
            'SELECT SUM(valor) FROM ganhos WHERE data LIKE ?', (periodo,))
        return self.cursor.fetchone()[0] or 0.0


class tabela_gastos(banco_de_dados):
    def inserir(self, valor, descricao, data):
        self.cursor.execute(
            'INSERT INTO gastos (valor, descricao, data) VALUES (?, ?, ?)', (valor, descricao, data))
        self.conexao.commit()

    def obter(self):
        self.cursor.execute('SELECT * FROM gastos')
        return self.cursor.fetchall()

    def total_mes(self, ano, mes):
        periodo = f"{ano}-{mes:02d}%"
        self.cursor.execute(
            'SELECT SUM(valor) FROM gastos WHERE data LIKE ?', (periodo,))
        return self.cursor.fetchone()[0] or 0.0


class tabela_reserva(banco_de_dados):
    def inserir(self, valor, data):
        self.cursor.execute(
            'INSERT INTO reserva (valor, data) VALUES (?, ?)', (valor, data))
        self.conexao.commit()

    def obter(self):
        self.cursor.execute('SELECT * FROM reserva')
        return self.cursor.fetchall()

    def total_mes(self, ano, mes):  # adicionei para ficar igual às outras
        periodo = f"{ano}-{mes:02d}%"
        self.cursor.execute(
            'SELECT SUM(valor) FROM reserva WHERE data LIKE ?', (periodo,))
        return self.cursor.fetchone()[0] or 0.0


class resumo_financeiro(banco_de_dados):
    def obter_resumo(self, ano, mes):
        periodo = f"{ano}-{mes:02d}%"

        self.cursor.execute(
            'SELECT SUM(valor) FROM ganhos WHERE data LIKE ?', (periodo,))
        total_ganhos = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute(
            'SELECT SUM(valor) FROM gastos WHERE data LIKE ?', (periodo,))
        total_gastos = self.cursor.fetchone()[0] or 0.0

        self.cursor.execute(
            'SELECT SUM(valor) FROM reserva WHERE data LIKE ?', (periodo,))
        total_reserva = self.cursor.fetchone()[0] or 0.0

        return {
            'total_ganhos': total_ganhos,
            'total_gastos': total_gastos,
            'total_reserva': total_reserva,
            'saldo': total_ganhos - total_gastos - total_reserva
        }


if __name__ == "__main__":
    with tabela_ganhos() as ganhos:
        ganhos.inserir(1000.0, '2024-06-01')
        print("Ganhos:", ganhos.obter())
        print("Total do mês:", ganhos.total_mes(2024, 6))

    with tabela_gastos() as gastos:
        gastos.inserir(200.0, 'Aluguel', '2024-06-02')
        gastos.inserir(150.0, 'Supermercado', '2024-06-05')
        gastos.inserir(50.0, 'Transporte', '2024-06-10')
        gastos.inserir(100.0, 'Lazer', '2024-06-15')
        print("Gastos:", gastos.obter())
        print("Total do mês:", gastos.total_mes(2024, 6))

    with tabela_reserva() as reserva:
        reserva.inserir(500.0, '2024-06-03')
        print("Reserva:", reserva.obter())
        print("Total do mês:", reserva.total_mes(2024, 6))

    with resumo_financeiro() as resumo:
        r = resumo.obter_resumo(2024, 6)
        print(f"\n--- Resumo Junho/2024 ---")
        print(f"Ganhos:  R$ {r['total_ganhos']:.2f}")
        print(f"Gastos:  R$ {r['total_gastos']:.2f}")
        print(f"Reserva: R$ {r['total_reserva']:.2f}")
        print(f"Saldo:   R$ {r['saldo']:.2f}")