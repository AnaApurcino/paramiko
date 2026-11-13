import paramiko
import json
import difflib

REFERENCIA = "referencia.cfg"

def auditar(dispositivo, referencia):
    nome = dispositivo["nome"]
    usuario = dispositivo["usuario"]
    caminho = f"/home/{usuario}/dispositivo.cfg"

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(
            hostname=dispositivo["host"],
            port=dispositivo["porta"],
            username=usuario,
            key_filename=dispositivo["chave"]
        )

        sftp = cliente.open_sftp()

        with sftp.open(caminho, "r") as arquivo:
            remoto = arquivo.read().decode().splitlines()

        sftp.close()

        diferencas = list(difflib.unified_diff(
            referencia,
            remoto,
            fromfile="referencia.cfg",
            tofile=f"{nome}/dispositivo.cfg",
            lineterm=""
        ))

        print(f"\n=== {nome} ===")

        if diferencas:
            print("NÃO CONFORME")
            for linha in diferencas:
                print(linha)
            return f"{nome}: NÃO CONFORME"
        else:
            print("CONFORME")
            return f"{nome}: CONFORME"

    except Exception as erro:
        print(f"FALHA na auditoria: {erro}")
        return f"{nome}: FALHA NA AUDITORIA"

    finally:
        cliente.close()


def main():
    with open(REFERENCIA, "r") as arquivo:
        referencia = arquivo.read().splitlines()

    with open("inventario.json", "r") as arquivo:
        dispositivos = json.load(arquivo)

    resultados = []

    for dispositivo in dispositivos:
        resultados.append(auditar(dispositivo, referencia))

    with open("relatorio_auditoria.txt", "w") as arquivo:
        arquivo.write("RELATORIO DE AUDITORIA\n\n")
        arquivo.write("\n".join(resultados))

    print("\nRelatório salvo em relatorio_auditoria.txt")


if __name__ == "__main__":
    main()
