import json
from conexao import conectar

with open("inventario.json", "r") as arquivo:
    dispositivos = json.load(arquivo)

disp = dispositivos[0]

# Apontar para uma chave privada inexistente
disp["chave"] = "/home/ana/.ssh/chave_invalida"

print(f"Testando {disp['nome']} com chave inválida...")

try:
    cliente = conectar(disp)
    print("Conexão realizada.")
    cliente.close()

except Exception as erro:
    print(f"Falha na autenticação: {type(erro).__name__}")
    print(f"Detalhes: {erro}")
