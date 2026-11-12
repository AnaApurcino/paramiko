
import json
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from conexao import conectar, executar


# Ler o inventário
with open("inventario.json", "r") as arquivo:
    dispositivos = json.load(arquivo)


def coletar(disp):
    """Coleta informações de um equipamento."""

    resultado = {
        "nome": disp["nome"],
        "usuario": disp["usuario"],
        "whoami": "",
        "hostname": "",
        "kernel": "",
        "uptime": "",
        "status": "SUCESSO",
        "erro": ""
    }

    cliente = None

    try:
        cliente = conectar(disp)

        comandos = {
            "whoami": "whoami",
            "hostname": "hostname",
            "kernel": "uname -r",
            "uptime": "uptime -p"
        }

        for campo, comando in comandos.items():
            codigo, saida, erro = executar(
                cliente, comando
            )

            if codigo != 0:
                raise RuntimeError(
                    f"{comando}: {erro or saida}"
                )

            resultado[campo] = saida

    except Exception as e:
        resultado["status"] = "FALHA"
        resultado["erro"] = str(e)

    finally:
        if cliente:
            cliente.close()

    return resultado


# Executar as coletas em paralelo
resultados = []

with ThreadPoolExecutor(max_workers=3) as executor:

    tarefas = [
        executor.submit(coletar, disp)
        for disp in dispositivos
    ]

    for tarefa in as_completed(tarefas):
        resultado = tarefa.result()
        resultados.append(resultado)

        print(
            f"{resultado['nome']}: "
            f"{resultado['status']}"
        )


# Gerar o arquivo CSV
campos = [
    "nome", "usuario", "whoami", "hostname",
    "kernel", "uptime", "status", "erro"
]

with open(
    "inventario_coletado.csv",
    "w",
    newline="",
    encoding="utf-8"
) as arquivo:

    escritor = csv.DictWriter(
        arquivo,
        fieldnames=campos
    )

    escritor.writeheader()
    escritor.writerows(resultados)


print("\nColeta finalizada!")
print("Relatório salvo em inventario_coletado.csv")
