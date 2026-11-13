import paramiko
import json

LIMITE_DISCO = 80
LIMITE_CARGA = 2.0

def monitorar(dispositivo):
    nome = dispositivo["nome"]

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        cliente.connect(
            hostname=dispositivo["host"],
            port=dispositivo["porta"],
            username=dispositivo["usuario"],
            key_filename=dispositivo["chave"],
            timeout=5
        )

        comando = """
        df -P / | awk 'NR==2 {gsub("%","",$5); print $5}'
        awk '{print $1}' /proc/loadavg
        pgrep -x sshd >/dev/null && echo ATIVO || echo INATIVO
        """

        stdin, stdout, stderr = cliente.exec_command(comando)

        saida = stdout.read().decode().strip().splitlines()
        erro = stderr.read().decode().strip()

        if stdout.channel.recv_exit_status() != 0 or len(saida) < 3:
            raise Exception(erro or "Falha na coleta de informações")

        disco = int(saida[0])
        carga = float(saida[1])
        sshd = saida[2]

        alertas = []

        if disco > LIMITE_DISCO:
            alertas.append("Disco acima de 80%")

        if carga > LIMITE_CARGA:
            alertas.append("Carga média acima de 2.0")

        if sshd != "ATIVO":
            alertas.append("Serviço SSH inativo")

        if alertas:
            status = "ALERTA"
        else:
            status = "OK"

        return {
            "nome": nome,
            "status": status,
            "disco": disco,
            "carga": carga,
            "sshd": sshd,
            "alertas": alertas
        }

    except Exception as erro:
        return {
            "nome": nome,
            "status": "FALHA",
            "erro": str(erro)
        }

    finally:
        cliente.close()


def main():
    with open("inventario.json", "r") as arquivo:
        dispositivos = json.load(arquivo)

    resultados = []

    for dispositivo in dispositivos:
        resultados.append(monitorar(dispositivo))

    print("\n========== PAINEL DE MONITORAMENTO ==========")

    for item in resultados:
        print(f"\nDISPOSITIVO: {item['nome']}")
        print(f"STATUS: {item['status']}")

        if item["status"] == "FALHA":
            print(f"CAUSA: {item['erro']}")
            continue

        print(f"DISCO: {item['disco']}%")
        print(f"CARGA MÉDIA: {item['carga']}")
        print(f"SSHD: {item['sshd']}")

        for alerta in item["alertas"]:
            print(f"ALERTA: {alerta}")

    print("\n=============== RESUMO FINAL ===============")

    for status in ["OK", "ALERTA", "FALHA"]:
        quantidade = sum(
            1 for item in resultados
            if item["status"] == status
        )
        print(f"{status}: {quantidade}")

    print("============================================")


if __name__ == "__main__":
    main()
