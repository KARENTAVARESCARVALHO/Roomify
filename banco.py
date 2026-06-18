import sqlite3

DB_NAME = "reservas.db"


def iniciar_banco():
    """Cria o banco de dados e a tabela se eles não existirem."""
    with sqlite3.connect(DB_NAME) as conexao:
        ponteiro = conexao.cursor()
        ponteiro.execute(
            """
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                sala TEXT NOT NULL,
                horario TEXT NOT NULL,
                responsavel TEXT NOT NULL
            )
        """
        )
        conexao.commit()


iniciar_banco()


# Lista de opções que o sistema aceita (dados fixos)
SALAS_VALIDAS = [
    "Sala 101 (Laboratório)",
    "Sala 102 (Teórica)",
    "Auditório A",
    "Bloco B - Sala 05",
]

HORARIOS_VALIDOS = [
    "08:00 - 10:00",
    "10:00 - 12:00",
    "14:00 - 16:00",
    "16:00 - 18:00",
]
