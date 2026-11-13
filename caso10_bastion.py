import paramiko
import socket

HOST_BASTION = "127.0.0.1"
PORTA_BASTION = 22
USUARIO_BASTION = "bastion"

HOST_INTERNO = "127.0.0.1"
PORTA_INTERNA = 2222
USUARIO_INTERNO = "r1"

CHAVE = "/home/ana/.ssh/id_ed25519_redes"

bastion = paramiko.SSHClient()
bastion.set_missing_host_key_policy(paramiko.AutoAddPolicy())

interno = paramiko.SSHClient()
interno.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("=== CONECTANDO AO BASTION ===")

    bastion.connect(
        hostname=HOST_BASTION,
        port=PORTA_BASTION,
        username=USUARIO_BASTION,
        key_filename=CHAVE
    )

    print("Conectado ao servidor intermediário!")

    transporte = bastion.get_transport()

    canal = transporte.open_channel(
        "direct-tcpip",
        (HOST_INTERNO, PORTA_INTERNA),
        ("127.0.0.1", 0)
    )

    print("\n=== CONECTANDO AO R1 PELO TUNEL ===")

    interno.connect(
        hostname=HOST_INTERNO,
        port=PORTA_INTERNA,
        username=USUARIO_INTERNO,
        key_filename=CHAVE,
        sock=canal
    )

    print("Conectado ao R1 através do bastion!")

    for comando in ["hostname", "whoami"]:
        stdin, stdout, stderr = interno.exec_command(comando)

        resultado = stdout.read().decode().strip()
        erro = stderr.read().decode().strip()

        print(f"\n$ {comando}")

        if resultado:
            print(resultado)

        if erro:
            print("ERRO:", erro)

    print("\nAcesso pelo bastion concluído!")

except Exception as erro:
    print(f"Falha na conexão: {erro}")

finally:
    interno.close()
    bastion.close()
