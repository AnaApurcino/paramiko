import json
from conexao import conectar, executar


# Ler o inventário
with open("inventario.json", "r") as arquivo:
    dispositivos = json.load(arquivo)


# Selecionar o R1
disp = dispositivos[0]

print(f"\nConectando ao equipamento {disp['nome']}...")

try:
    cliente = conectar(disp)

    print("Conexão SSH estabelecida com sucesso!")

    # Lista de comandos que serão executados
    comandos = [
        "whoami",
        "hostname",
        "uptime -p",
        "comando-inexistente"
    ]

    # Executar cada comando
    for comando in comandos:

        print("\n" + "=" * 45)
        print(f"Comando: {comando}")

        codigo, saida, erro = executar(
            cliente, comando
        )

        print(f"Código de saída: {codigo}")
        print(f"Saída padrão: {saida}")
        print(f"Saída de erro: {erro}")

    cliente.close()

except Exception as e:
    print(f"Erro na conexão: {e}")
