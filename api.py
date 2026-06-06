import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sistema de Reservas da Faculdade")
DB_NAME = "reservas.db"


def iniciar_banco():
    with sqlite3.connect(DB_NAME) as conexao:
        ponteiro = conexao.cursor()
        ponteiro.execute(
            """
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sala TEXT NOT NULL,
                horario TEXT NOT NULL,
                responsavel TEXT NOT NULL
            )
        """
        )
        conexao.commit()


iniciar_banco()


# Configurações de opções válidas no sistema
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


class ModeloReserva(BaseModel):
    sala: str
    horario: str
    responsavel: str


# ROTA 1: Listar todas as reservas salvas
@app.get("/reservas")
def listar_todas_as_reservas():
    with sqlite3.connect(DB_NAME) as conexao:
        conexao.row_factory = sqlite3.Row  # Transforma o resultado em dicionário
        ponteiro = conexao.cursor()
        ponteiro.execute("SELECT * FROM reservas")
        linhas = ponteiro.fetchall()
        return [dict(linha) for linha in linhas]


# ROTA 2: Criar nova reserva com validação de conflito
@app.post("/reservas")
def realizar_nova_reserva(dados: ModeloReserva):
    # Valida se os dados enviados fazem sentido
    if dados.sala not in SALAS_VALIDAS or dados.horario not in HORARIOS_VALIDOS:
        raise HTTPException(
            status_code=400, detail="Sala ou horário inválidos."
        )

    if not dados.responsavel.strip():
        raise HTTPException(
            status_code=400, detail="Nome do responsável é obrigatório."
        )

    with sqlite3.connect(DB_NAME) as conexao:
        ponteiro = conexao.cursor()

        # Verifica se já existe a mesma sala no mesmo horário
        ponteiro.execute(
            "SELECT id FROM reservas WHERE sala = ? AND horario = ?",
            (dados.sala, dados.horario),
        )
        conflito = ponteiro.fetchone()

        if conflito:
            raise HTTPException(
                status_code=409,
                detail="Esta sala já está ocupada neste horário!",
            )

        # Se passou no teste, salva no banco
        ponteiro.execute(
            "INSERT INTO reservas (sala, horario, responsavel) VALUES (?, ?, ?)",
            (dados.sala, dados.horario, dados.responsavel),
        )
        conexao.commit()

    return {"mensagem": "Reserva confirmada com sucesso!"}


# ROTA 3: Cancelar/Excluir uma reserva pelo ID
@app.delete("/reservas/{reserva_id}")
def cancelar_reserva(reserva_id: int):
    with sqlite3.connect(DB_NAME) as conexao:
        ponteiro = conexao.cursor()
        ponteiro.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
        conexao.commit()
    return {"mensagem": f"Reserva {reserva_id} cancelada."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
