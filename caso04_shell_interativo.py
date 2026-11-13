
import paramiko
import time

HOST = "127.0.0.1"
PORT = 22
USUARIO = "r1"

def executar_interativo():
    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(
            hostname=HOST,
            port=PORT,
            username=USUARIO,
            key_filename="/home/ana/.ssh/id_ed25519_redes"
        )

        print("=== SESSÃO INTERATIVA (invoke_shell) ===")

        shell = cliente.invoke_shell()
        time.sleep(1)

        comandos = [
            "cd /tmp",
            "pwd",
            "export AMBIENTE=PRODUCAO",
            "echo $AMBIENTE"
        ]

        for comando in comandos:
            print(f"\n$ {comando}")
            shell.send(comando + "\n")
            time.sleep(0.5)

            if shell.recv_ready():
                saida = shell.recv(4096).decode("utf-8", errors="replace")
                print(saida, end="")

        time.sleep(1)

        while shell.recv_ready():
            print(shell.recv(4096).decode("utf-8", errors="replace"), end="")

        shell.close()

        print("\n=== SESSÃO INDEPENDENTE (exec_command) ===")

        for comando in comandos:
            stdin, stdout, stderr = cliente.exec_command(comando)

            saida = stdout.read().decode("utf-8", errors="replace")
            erro = stderr.read().decode("utf-8", errors="replace")

            print(f"\n$ {comando}")
            print(saida, end="")

            if erro:
                print("ERRO:", erro)

    except paramiko.AuthenticationException:
        print("Erro: falha na autenticação SSH.")

    except paramiko.SSHException as erro:
        print(f"Erro SSH: {erro}")

    except Exception as erro:
        print(f"Erro: {erro}")

    finally:
        cliente.close()


if __name__ == "__main__":
    executar_interativo()
