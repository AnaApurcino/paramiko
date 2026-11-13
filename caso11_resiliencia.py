import json
import time
import socket
import paramiko

from paramiko.ssh_exception import (
    AuthenticationException,
    NoValidConnectionsError,
    SSHException
)

ARQUIVO_INVENTARIO = "inventario_caso11.json"
ARQUIVO_RELATORIO = "relatorio_caso11.txt"

MAX_TENTATIVAS = 3
TEMPO_ESPERA = 2


def conectar(dispositivo):
    nome = dispositivo["nome"]
    tentativas = 0

    while tentativas < MAX_TENTATIVAS:
        tentativas += 1
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            print(f"\n[{nome}] Tentativa {tentativas}")

            parametros = {
                "hostname": dispositivo["host"],
                "port": dispositivo["porta"],
                "username": dispositivo["usuario"],
                "timeout": 3,
                "banner_timeout": 3,
                "auth_timeout": 3,
                "allow_agent": False,
                "look_for_keys": False
            }

            if dispositivo["metodo"] == "chave":
                parametros["key_filename"] = dispositivo["chave"]

            elif dispositivo["metodo"] == "senha":
                parametros["password"] = dispositivo["senha"]

            ssh.connect(**parametros)

            print(f"[{nome}] CONEXÃO BEM-SUCEDIDA")

            ssh.close()

            return {
                "nome": nome,
                "status": "SUCESSO",
                "causa": "Nenhuma falha identificada",
                "tentativas": tentativas
            }

        except AuthenticationException:
            print(f"[{nome}] ERRO DE AUTENTICAÇÃO")

            return {
                "nome": nome,
                "status": "FALHA",
                "causa": "Senha incorreta ou credencial rejeitada",
                "tentativas": tentativas
            }

        except NoValidConnectionsError as erro:
            causas = list(erro.errors.values())

            if any(isinstance(e, (socket.timeout, TimeoutError))
                   for e in causas):

                if tentativas < MAX_TENTATIVAS:
                    espera = TEMPO_ESPERA * (2 ** (tentativas - 1))
                    print(f"[{nome}] TIMEOUT. Aguardando {espera}s...")
                    time.sleep(espera)
                    continue

                return {
                    "nome": nome,
                    "status": "FALHA",
                    "causa": "Timeout: equipamento sem resposta",
                    "tentativas": tentativas
                }

            if any(isinstance(e, ConnectionRefusedError)
                   for e in causas):

                return {
                    "nome": nome,
                    "status": "FALHA",
                    "causa": "Conexão recusada: porta fechada ou serviço SSH indisponível",
                    "tentativas": tentativas
                }

            return {
                "nome": nome,
                "status": "FALHA",
                "causa": f"Falha de conexão: {erro}",
                "tentativas": tentativas
            }

        except (socket.timeout, TimeoutError):
            if tentativas < MAX_TENTATIVAS:
                espera = TEMPO_ESPERA * (2 ** (tentativas - 1))
                print(f"[{nome}] TIMEOUT. Aguardando {espera}s...")
                time.sleep(espera)
                continue

            return {
                "nome": nome,
                "status": "FALHA",
                "causa": "Timeout: equipamento sem resposta",
                "tentativas": tentativas
            }

        except SSHException as erro:
            return {
                "nome": nome,
                "status": "FALHA",
                "causa": f"Falha SSH: {erro}",
                "tentativas": tentativas
            }

        except OSError as erro:
            return {
                "nome": nome,
                "status": "FALHA",
                "causa": f"Erro de sistema ou rede: {erro}",
                "tentativas": tentativas
            }

        finally:
            ssh.close()


def main():
    with open(ARQUIVO_INVENTARIO, "r") as arquivo:
        dispositivos = json.load(arquivo)

    resultados = []

    print("=== CASO 11: AUTOMACAO RESILIENTE A FALHAS ===")

    for dispositivo in dispositivos:
        try:
            resultado = conectar(dispositivo)
            resultados.append(resultado)

        except Exception as erro:
            resultados.append({
                "nome": dispositivo["nome"],
                "status": "FALHA",
                "causa": f"Erro inesperado: {erro}",
                "tentativas": 0
            })

    with open(ARQUIVO_RELATORIO, "w") as arquivo:
        arquivo.write("RELATORIO - CASO 11\n")
        arquivo.write("=" * 50 + "\n")

        for resultado in resultados:
            arquivo.write(f"\nEquipamento: {resultado['nome']}\n")
            arquivo.write(f"Status: {resultado['status']}\n")
            arquivo.write(f"Causa provável: {resultado['causa']}\n")
            arquivo.write(f"Tentativas: {resultado['tentativas']}\n")

        arquivo.write("\n" + "=" * 50 + "\n")
        arquivo.write("Fim do relatório.\n")

    print("\n=== RESULTADO FINAL ===")

    for resultado in resultados:
        print(
            f"{resultado['nome']}: "
            f"{resultado['status']} - {resultado['causa']}"
        )

    print(f"\nRelatório salvo em: {ARQUIVO_RELATORIO}")


if __name__ == "__main__":
    main()
