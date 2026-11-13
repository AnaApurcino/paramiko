import paramiko
import json
import hashlib
import os
import shlex

ARQUIVO_LOCAL = "coleta.sh"
ARQUIVO_REMOTO = "coleta.sh"

def calcular_hash_local():
    sha256 = hashlib.sha256()

    with open(ARQUIVO_LOCAL, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(4096), b""):
            sha256.update(bloco)

    return sha256.hexdigest()


def distribuir(dispositivo, hash_local):
    nome = dispositivo["nome"]
    usuario = dispositivo["usuario"]

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(
            hostname=dispositivo["host"],
            port=dispositivo["porta"],
            username=usuario,
            key_filename=dispositivo["chave"]
        )

        caminho_remoto = f"/home/{usuario}/{ARQUIVO_REMOTO}"
        remoto = shlex.quote(caminho_remoto)

        print(f"\n=== {nome} ===")

        # Enviar arquivo via SFTP
        sftp = cliente.open_sftp()
        sftp.put(ARQUIVO_LOCAL, caminho_remoto)
        sftp.close()

        print("Arquivo enviado.")

        # Tornar executável
        stdin, stdout, stderr = cliente.exec_command(
            f"chmod +x {remoto}"
        )

        if stdout.channel.recv_exit_status() != 0:
            raise Exception("Falha ao tornar arquivo executável.")

        # Calcular hash remoto
        stdin, stdout, stderr = cliente.exec_command(
            f"sha256sum {remoto}"
        )

        saida = stdout.read().decode().strip()

        if stdout.channel.recv_exit_status() != 0:
            raise Exception("Falha ao calcular hash remoto.")

        hash_remoto = saida.split()[0]

        print(f"Hash local:  {hash_local}")
        print(f"Hash remoto: {hash_remoto}")

        # Comparar hashes
        if hash_local != hash_remoto:
            print("ERRO: Hashes diferentes. Execução cancelada.")
            return

        print("Integridade confirmada!")

        # Executar somente se os hashes forem iguais
        stdin, stdout, stderr = cliente.exec_command(
            f"bash {remoto}"
        )

        resultado = stdout.read().decode()
        erro = stderr.read().decode()
        status = stdout.channel.recv_exit_status()

        if status == 0:
            print("Script executado com sucesso:")
            print(resultado)
        else:
            print(f"Falha na execução: {erro}")

    except Exception as erro:
        print(f"FALHA em {nome}: {erro}")

    finally:
        cliente.close()


def main():
    hash_local = calcular_hash_local()

    print("Hash SHA-256 local:", hash_local)

    with open("inventario.json", "r") as arquivo:
        dispositivos = json.load(arquivo)

    for dispositivo in dispositivos:
        distribuir(dispositivo, hash_local)


if __name__ == "__main__":
    main()
