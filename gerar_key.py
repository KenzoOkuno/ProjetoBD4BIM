from cryptography.fernet import Fernet

# Gerar a chave apenas uma vez
chave = Fernet.generate_key()

# Salvar a chave no arquivo "chave.key"
with open("chave.key", "wb") as chave_arquivo:
    chave_arquivo.write(chave)

print("Chave gerada e salva com sucesso!")
