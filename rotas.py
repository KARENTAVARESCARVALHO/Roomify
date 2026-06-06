import sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
# Importa as configurações do arquivo banco.py que criamos antes
from banco import DB_NAME, HORARIOS_VALIDOS, SALAS_VALIDAS

# O APIRouter funciona como se fosse o "app", mas para arquivos separados
router = APIRouter()


class ModeloReserva(BaseModel):
    sala: str
    horario: str
    responsavel: str


@router.get("/reservas")
def listar_todas_as_reservas():
    """Rota para listar todas as reservas do banco."""
    with sqlite3.connect(DB_NAME) as conexao:
        conexao.row_factory = sqlite3.Row
        ponteiro = conexao.cursor()
        ponteiro.execute("SELECT * FROM reservas")
        linhas = ponteiro.fetchall()
        return [dict(linha) for linha in linhas]


@router.post("/reservas")
def realizar_nova_reserva(dados: ModeloReserva):
    """Rota para criar uma nova reserva."""
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

        ponteiro.execute(
            "INSERT INTO reservas (sala, horario, responsavel) VALUES (?, ?, ?)",
            (dados.sala, dados.horario, dados.responsavel),
        )
        conexao.commit()

    return {"mensagem": "Reserva confirmada com sucesso!"}


@router.delete("/reservas/{reserva_id}")
def cancelar_reserva(reserva_id: int):
    """Rota para deletar uma reserva existente."""
    with sqlite3.connect(DB_NAME) as conexao:
        ponteiro = conexao.cursor()
        ponteiro.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
        conexao.commit()
    return {"mensagem": f"Reserva {reserva_id} cancelada."}