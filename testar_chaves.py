import json
from conexao import conectar, executar

with open("inventario.json", "r") as arquivo:
    dispositivos = json.load(arquivo)

for disp in dispositivos:
    print(f"\n=== {disp['nome']} ===")

    try:
        cliente = conectar(disp)
        codigo, saida, erro = executar(cliente, "whoami")

        print(f"Código de saída: {codigo}")
        print(f"Saída: {saida}")
        print(f"Erro: {erro}")

        cliente.close()

    except Exception as e:
        print(f"Falha na conexão: {e}")
