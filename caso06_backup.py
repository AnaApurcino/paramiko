import paramiko
import json
import os
import logging
from datetime import datetime

PASTA_BACKUP = "backups"
ARQUIVO_REMOTO = "dispositivo.cfg"

logging.basicConfig(
    filename="backup.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fazer_backup(dispositivo):
    nome = dispositivo["nome"]
    diretorio = os.path.join(PASTA_BACKUP, nome)

    os.makedirs(diretorio, exist_ok=True)

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(
            hostname=dispositivo["host"],
            port=dispositivo["porta"],
            username=dispositivo["usuario"],
            key_filename=dispositivo["chave"]
        )

        sftp = cliente.open_sftp()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        arquivo_local = os.path.join(
            diretorio,
            f"{timestamp}.cfg"
        )

        caminho_remoto = (
            f"/home/{dispositivo['usuario']}/{ARQUIVO_REMOTO}"
        )

        sftp.get(caminho_remoto, arquivo_local)

        sftp.close()

        backups = [
            os.path.join(diretorio, arquivo)
            for arquivo in os.listdir(diretorio)
            if arquivo.endswith(".cfg")
        ]

        backups.sort(key=os.path.getmtime, reverse=True)

        for antigo in backups[5:]:
            os.remove(antigo)
            print(f"Backup antigo removido: {antigo}")

        mensagem = f"SUCESSO - {nome} - {arquivo_local}"
        print(mensagem)
        logging.info(mensagem)

    except Exception as erro:
        mensagem = f"FALHA - {nome} - {erro}"
        print(mensagem)
        logging.error(mensagem)

    finally:
        cliente.close()


def main():
    os.makedirs(PASTA_BACKUP, exist_ok=True)

    with open("inventario.json", "r") as arquivo:
        dispositivos = json.load(arquivo)

    for dispositivo in dispositivos:
        fazer_backup(dispositivo)


if __name__ == "__main__":
    main()
