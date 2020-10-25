# p2p_simulator

## Requisitos
    - python 3.6+
    - pip3

## Instalação

### Linux

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

### Windows

    python -m venv venv
    venv\Scripts\Activate
    pip install -r requirements.txt

## Uso

    # Servidor
    python -m server
    
    # Peer (listen_port é a utilizada para servir os arquivos)
    python -m peer [listen_port]

## Testes

    pytest tests
