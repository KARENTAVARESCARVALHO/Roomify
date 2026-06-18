import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


class TestApiReservas(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "reservas_test.db")
        self.patcher = patch.object(api, "DB_NAME", self.db_path)
        self.patcher.start()
        api.iniciar_banco()
        self.client = TestClient(api.app)

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def test_deve_salvar_e_recuperar_data_da_reserva(self):
        response = self.client.post(
            "/reservas",
            json={
                "data": "2026-06-18",
                "sala": "Sala 101 (Laboratório)",
                "horario": "08:00 - 10:00",
                "responsavel": "Professor Teste",
            },
        )

        self.assertEqual(response.status_code, 200, response.text)

        response = self.client.get("/reservas")
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()

        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["data"], "2026-06-18")


if __name__ == "__main__":
    unittest.main()
