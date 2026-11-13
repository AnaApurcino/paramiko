import paramiko
import json
import ipaddress
import shlex

NOVO_NTP = "10.0.0.50"

def validar_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ValueError:
        return False


def executar(cliente, comando):
    stdin, stdout, stderr = cliente.exec_command(comando)
    saida = stdout.read().decode().strip()
    erro = stderr.read().decode().strip()
    status = stdout.channel.recv_exit_status()

    if status != 0:
        raise Exception(erro or "Falha na execução do comando")

    return saida


def alterar_dispositivo(dispositivo):
    nome = dispositivo["nome"]
    usuario = dispositivo["usuario"]

    cliente = paramiko.SSHClient()
    cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    arquivo = f"/home/{usuario}/dispositivo.cfg"
    backup = arquivo + ".bak"

    backup_criado = False

    try:
        print(f"\n=== {nome} ===")

        cliente.connect(
            hostname=dispositivo["host"],
            port=dispositivo["porta"],
            username=usuario,
            key_filename=dispositivo["chave"]
        )

        remoto = shlex.quote(arquivo)
        copia = shlex.quote(backup)
        temporario = shlex.quote(arquivo + ".tmp")

        # Verificar se a configuração já está correta
        atual = executar(cliente, f"cat {remoto}")
        linhas = [l for l in atual.splitlines() if l.startswith("ntp_server=")]

        if linhas == [f"ntp_server={NOVO_NTP}"]:
            print("Configuração já está correta. Nenhuma alteração necessária.")
            print("RESULTADO: SUCESSO (IDEMPOTENTE)")
            return

        # A) Criar backup apenas se ainda não existir
        executar(cliente, f"test -f {copia} || cp -p {remoto} {copia}")
        backup_criado = True

        print("Backup criado com sucesso.")

        # B) Aplicar alteração sem duplicar linhas
        ip = NOVO_NTP

        comando = (
            f"awk '!/^ntp_server=/' {remoto} > {temporario} "
            f"&& printf '%s\\n' 'ntp_server={ip}' >> {temporario} "
            f"&& mv {temporario} {remoto}"
        )

        executar(cliente, comando)

        print("Configuração atualizada.")

        # C) Verificar o valor e a quantidade de linhas
        comando = (
            f"grep -Fxc -- 'ntp_server={ip}' {remoto}"
        )

        quantidade = executar(cliente, comando)

        if quantidade != "1":
            raise Exception("Verificação falhou.")

        print("Verificação concluída: valor correto e sem duplicações.")
        print("RESULTADO: SUCESSO")

    except Exception as erro:
        print(f"FALHA: {erro}")

        # D) Reverter somente se o backup foi criado
        if backup_criado:
            try:
                executar(
                    cliente,
                    f"cp -p {shlex.quote(backup)} {shlex.quote(arquivo)}"
                )
                print("REVERSÃO: configuração original restaurada.")

            except Exception as reversao:
                print(f"ERRO NA REVERSÃO: {reversao}")

    finally:
        cliente.close()


def main():
    if not validar_ip(NOVO_NTP):
        print("IP inválido. Operação cancelada.")
        return

    with open("inventario.json", "r") as arquivo:
        dispositivos = json.load(arquivo)

    for dispositivo in dispositivos:
        alterar_dispositivo(dispositivo)


if __name__ == "__main__":
    main()
