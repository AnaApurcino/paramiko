import json
from conexao import conectar, executar

with open("inventario.json", "r") as arquivo:
    dispositivos = json.load(arquivo)

print("=== TESTE DE AUTENTICACAO POR CHAVE PUBLICA ===")

for disp in dispositivos:
    print(f"\n=== {disp['nome']} ===")

    try:
        cliente = conectar(disp)
        codigo, saida, erro = executar(cliente, "whoami")

        print(f"Código de saída: {codigo}")
        print(f"Saída: {saida}")
        print(f"Erro: {erro}")

        cliente.close()

    except Exception as erro:
        print(f"Falha: {type(erro).__name__}: {erro}")


print("\n=== TESTE COM CHAVE PRIVADA INVALIDA ===")

disp = dispositivos[0].copy()
disp["chave"] = "/home/ana/.ssh/chave_invalida"

try:
    cliente = conectar(disp)
    print("Conexão realizada.")
    cliente.close()

except Exception as erro:
    print(f"Falha esperada: {type(erro).__name__}")
    print(f"Detalhes: {erro}")
