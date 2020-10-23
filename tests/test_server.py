import os
import sys
import json
from time import sleep
import pytest

# Estas definições estão antes dos imports do server para que este seja inicializado com variáveis de teste
TESTDB = os.path.dirname(os.path.realpath(__file__)) + "/p2pservertest.db"
# Não vamos esperar 5 segundos nos testes de sessão =)
ALIVE_TIME = 1
os.environ["ALIVE_TIME"] = str(ALIVE_TIME)
os.environ["APPDB"] = TESTDB

# Adiciona o diretório acima ao path, para que o server seja encontrado
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import seed
from server.webserver import create_app

DATA_REGISTER = {"ip": "1.2.3.4"}
DATA_OFFERFILES = {
    "ip": "1.2.3.4",
    "files": [
        {
            "name": "arquivo1",
            "hash": "835480941C61BCD55A4BCB74CCB8A21833E34CD3F34CB977461539084A984A6C",
        },
        {
            "name": "arquivo2",
            "hash": "89D603EFB7FA042D322084A459E796764191111E5D9F46EBFB77D1D711EB4557",
        },
    ],
}


@pytest.fixture
def client():
    seed.create_tables()
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client

    seed.db.close()
    os.unlink(TESTDB)


def test_register(client):
    rs = client.post(path="/register", data=json.dumps(DATA_REGISTER))
    assert rs.status_code == 200


def test_offerfiles_unregistered(client):
    rs = client.post(
        path="/offerfiles",
        data=json.dumps(DATA_OFFERFILES),
    )
    assert rs.status_code == 401


def test_offerfiles_registered(client):
    rs = client.post(path="/register", data=json.dumps(DATA_REGISTER))
    assert rs.status_code == 200

    rs = client.post(
        path="/offerfiles",
        data=json.dumps(DATA_OFFERFILES),
    )
    assert rs.status_code == 201


def test_search(client):
    rs = client.post(path="/register", data=json.dumps(DATA_REGISTER))
    assert rs.status_code == 200

    rs = client.post(
        path="/offerfiles",
        data=json.dumps(DATA_OFFERFILES),
    )
    assert rs.status_code == 201

    rs = client.post(path="/search", data=json.dumps(DATA_REGISTER))
    data = json.loads(rs.data)
    assert all(
        elem in data["files"]
        for elem in [
            {"ip": DATA_OFFERFILES["ip"], "hash": d["hash"], "name": d["name"]}
            for d in DATA_OFFERFILES["files"]
        ]
    )


def test_not_alive(client):
    rs = client.post(path="/register", data=json.dumps(DATA_REGISTER))
    assert rs.status_code == 200

    sleep(ALIVE_TIME + 0.01)

    rs = client.post(
        path="/offerfiles",
        data=json.dumps(DATA_OFFERFILES),
    )
    assert rs.status_code == 401


def test_iamalive(client):
    rs = client.post(path="/register", data=json.dumps(DATA_REGISTER))
    assert rs.status_code == 200

    sleep(ALIVE_TIME * 0.75)

    rs = client.post(
        path="/iamalive",
        data=json.dumps(DATA_OFFERFILES),
    )
    assert rs.status_code == 200

    sleep(ALIVE_TIME * 0.75)

    rs = client.post(
        path="/offerfiles",
        data=json.dumps(DATA_OFFERFILES),
    )
    assert rs.status_code == 201