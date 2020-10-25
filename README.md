# P2P Simulator

## Requisitos
    - python 3.6+
    - pip3
    - Docker (para a simulação de rede de peers com Docker)

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
    
### Simulação de rede de peers com Docker
Os scripts executam em modo interativo, deve ser executado um em cada terminal

    # Iniciar servidor
    docker_scripts/server.sh
    
    # Iniciar peer
    docker_scripts/peer.sh
    
    # Remover redes, containers e imagens
    docker_scripts/cleanup.sh

## Testes

    pytest tests
