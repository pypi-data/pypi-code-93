import pytest as pytest

from libpythonprogoldani.spam.enviador_de_email import Enviador
from libpythonprogoldani.spam.enviador_de_email import EmailInvalido


def test_criar_enviador_de_email():
    enviador = Enviador()
    assert enviador is not None


@pytest.mark.parametrize("remetente", ["foo@ba.com.br", "gustavo@gmail.com"])
def test_remetente(remetente):
    enviador = Enviador()
    resultado = enviador.enviar(
        remetente, "goldani@gmail.com", "Curso PythonPro", "Turma Henrique Bastos"
    )
    assert remetente in resultado


@pytest.mark.parametrize("remetente", ["", "gustavo"])
def test_remetente_invalido(remetente):
    enviador = Enviador()
    with pytest.raises(EmailInvalido):
        enviador.enviar(
            remetente, "goldani@gmail.com", "Curso PythonPro", "Turma Henrique Bastos"
        )
