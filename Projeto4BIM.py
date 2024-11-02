from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from cryptography.fernet import Fernet, InvalidToken
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta
import json
import re  # Importando módulo para expressões regulares

# Conexão com MongoDB
uri = "mongodb+srv://Kenzo:123@brunao.u01owig.mongodb.net/?retryWrites=true&w=majority&appName=Brunao"
cliente = MongoClient(uri)  # Cria uma instância do cliente MongoDB
meu_banco = cliente['Projeto4BIM']  # Acessa o banco de dados 'Projeto4BIM'
colecao = meu_banco['Registro Medico']  # Acessa a coleção 'Registro Medico'

# Carregar chave de criptografia
with open("chave.key", "rb") as chave_arquivo:
    chave = chave_arquivo.read()  # Lê a chave de criptografia do arquivo
fernet = Fernet(chave)  # Inicializa o objeto Fernet com a chave lida

# Funções de criptografia e descriptografia
def criptografar_conteudo(conteudo):
    return fernet.encrypt(conteudo.encode())  # Retorna o conteúdo criptografado

def descriptografar_conteudo(conteudo):
    return fernet.decrypt(conteudo).decode()  # Retorna o conteúdo descriptografado

# Funções de validação de campos
def validar_campos_obrigatorios(*args):
    for campo in args:
        if not campo.strip():  # Verifica se algum campo está vazio
            return False
    return True  # Retorna True se todos os campos estão preenchidos

# Função para validar se o nome contém letras
def validar_nome(nome):
    return re.search(r'[a-zA-Z]', nome) is not None  # Verifica se há pelo menos uma letra no nome

# Função para cadastrar paciente
def cadastrar_paciente():
    # Coleta informações do paciente
    nome_paciente = simpledialog.askstring("Cadastro de Paciente", "Nome completo do paciente:")
    historico_medico = simpledialog.askstring("Cadastro de Paciente", "Histórico médico:")
    tratamento = simpledialog.askstring("Cadastro de Paciente", "Tratamento:")
    
    if not validar_campos_obrigatorios(nome_paciente, historico_medico, tratamento):
        messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")  # Alerta se campos obrigatórios não forem preenchidos
        return

    if not validar_nome(nome_paciente):
        messagebox.showwarning("Atenção", "O nome deve conter pelo menos uma letra!")  # Alerta se o nome não contiver letras
        return

    # Criptografa as informações do paciente
    nome_criptografado = criptografar_conteudo(nome_paciente)
    historico_criptografado = criptografar_conteudo(historico_medico)
    tratamento_criptografado = criptografar_conteudo(tratamento)

    # Cria o dicionário do paciente
    paciente = {
        'nome': nome_criptografado,
        'Historico medico': historico_criptografado,
        'tratamento': tratamento_criptografado
    }
    colecao.insert_one(paciente)  # Insere o dicionário do paciente na coleção
    messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!")  # Mensagem de sucesso

# Função para consultar pacientes
def consulta():
    senha = simpledialog.askstring("Autenticação", "Digite a sua senha para continuar:", show='*')
    
    if senha != chave.decode():  # Verifica se a senha digitada corresponde à chave
        messagebox.showwarning("Acesso Negado", "Senha incorreta.")  # Alerta se a senha estiver incorreta
        return

    janela_consulta = tk.Toplevel()  # Cria uma nova janela para consulta
    janela_consulta.title("Pacientes Registrados")

    # Adiciona uma área de texto com barra de rolagem
    scrollbar = tk.Scrollbar(janela_consulta)
    texto_label = tk.Text(janela_consulta, wrap="word", width=50, height=20, yscrollcommand=scrollbar.set)
    scrollbar.config(command=texto_label.yview)

    # Preenche a área de texto com os registros
    for paciente in colecao.find():  # Itera sobre todos os pacientes na coleção
        # Descriptografa os dados do paciente
        nome = descriptografar_conteudo(paciente['nome'])
        historico = descriptografar_conteudo(paciente['Historico medico'])
        tratamento = descriptografar_conteudo(paciente['tratamento'])
        paciente_id = str(paciente['_id'])  # Obtém o ID do paciente

        texto_paciente = f"Nome: {nome}\nHistórico Médico: {historico}\nTratamento: {tratamento}\nID: {paciente_id}\n{'-'*40}\n"
        texto_label.insert("end", texto_paciente)  # Insere os dados na área de texto

    texto_label.config(state="disabled")  # Desabilita a edição do texto
    texto_label.pack(side="left", fill="both", expand=True)  # Adiciona o texto à janela
    scrollbar.pack(side="right", fill="y")  # Adiciona a barra de rolagem

    janela_consulta.transient(janela_principal)  # Mantém a janela de consulta sobre a janela principal
    janela_consulta.grab_set()  # Concentra a entrada na janela de consulta
    janela_principal.wait_window(janela_consulta)  # Aguarda o fechamento da janela de consulta

# Funções de compartilhamento temporário
def gerar_chave_temporaria(tempo_validade_minutos):
    chave_temporaria = Fernet.generate_key()  # Gera uma nova chave temporária
    data_expiracao = datetime.now() + timedelta(minutes=tempo_validade_minutos)  # Define a data de expiração
    return chave_temporaria, data_expiracao  # Retorna a chave e a data de expiração

def compartilhar_registro_temporario():
    registro_compartilhado = simpledialog.askstring("Compartilhar Registro", "Digite o ID do registro a compartilhar:")
    tempo = simpledialog.askinteger("Compartilhar Registro", "Tempo de validade (minutos) da chave temporária:")

    if not validar_campos_obrigatorios(registro_compartilhado, str(tempo)):
        messagebox.showwarning("Atenção", "Todos os campos são obrigatórios!")  # Alerta se campos obrigatórios não forem preenchidos
        return

    try:
        object_id = ObjectId(registro_compartilhado)  # Converte o ID para ObjectId
        paciente = colecao.find_one({"_id": object_id})  # Busca o paciente pelo ID

        if paciente:
            # Gera chave temporária e expiração
            chave_temporaria, data_expiracao = gerar_chave_temporaria(tempo)
            fernet_temporario = Fernet(chave_temporaria)  # Inicializa o Fernet com a chave temporária

            # Criptografa os dados do paciente
            nome_temp = fernet_temporario.encrypt(descriptografar_conteudo(paciente['nome']).encode())
            historico_temp = fernet_temporario.encrypt(descriptografar_conteudo(paciente['Historico medico']).encode())
            tratamento_temp = fernet_temporario.encrypt(descriptografar_conteudo(paciente['tratamento']).encode())

            # Cria um dicionário com os dados compartilhados
            dados_compartilhamento = {
                "chave": chave_temporaria.decode(),
                "expira_em": data_expiracao.isoformat(),
                "registro_nome": nome_temp.decode(),
                "registro_historico": historico_temp.decode(),
                "registro_tratamento": tratamento_temp.decode()
            }

            # Salva os dados de compartilhamento em um arquivo JSON
            with open("compartilhamento_temporario.json", "w") as arquivo:
                json.dump(dados_compartilhamento, arquivo)

            messagebox.showinfo("Sucesso", "Registro compartilhado com sucesso!")  # Mensagem de sucesso
        else:
            messagebox.showerror("Erro", "Paciente não encontrado.")  # Mensagem de erro se paciente não for encontrado
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")  # Mensagem de erro para exceções

def acessar_registro_compartilhado():
    try:
        with open("compartilhamento_temporario.json", "r") as arquivo:
            dados = json.load(arquivo)  # Carrega os dados do compartilhamento

        chave_temporaria = dados["chave"].encode()  # Codifica a chave temporária
        data_expiracao = datetime.fromisoformat(dados["expira_em"])  # Converte a data de expiração

        if datetime.now() > data_expiracao:  # Verifica se a chave expirou
            messagebox.showerror("Erro", "A chave temporária expirou.")  # Mensagem de erro
            return

        fernet_temporario = Fernet(chave_temporaria)  # Inicializa o Fernet com a chave temporária

        # Descriptografa os dados
        nome = fernet_temporario.decrypt(dados["registro_nome"].encode()).decode()
        historico = fernet_temporario.decrypt(dados["registro_historico"].encode()).decode()
        tratamento = fernet_temporario.decrypt(dados["registro_tratamento"].encode()).decode()

        # Exibe os dados
        messagebox.showinfo("Registro Compartilhado", f"Nome: {nome}\nHistórico Médico: {historico}\nTratamento: {tratamento}")
    except InvalidToken:
        messagebox.showerror("Erro", "Chave inválida ou dados corrompidos.")  # Mensagem de erro para chave inválida
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")  # Mensagem de erro para exceções

# Configuração da interface gráfica
janela_principal = tk.Tk()
janela_principal.title("Gerenciamento de Registros Médicos")

# Botões da interface
btn_cadastrar = tk.Button(janela_principal, text="Cadastrar Paciente", command=cadastrar_paciente)
btn_consultar = tk.Button(janela_principal, text="Consultar Pacientes", command=consulta)
btn_compartilhar = tk.Button(janela_principal, text="Compartilhar Registro Temporário", command=compartilhar_registro_temporario)
btn_acessar_compartilhado = tk.Button(janela_principal, text="Acessar Registro Compartilhado", command=acessar_registro_compartilhado)

# Adiciona os botões na janela
btn_cadastrar.pack(pady=10)
btn_consultar.pack(pady=10)
btn_compartilhar.pack(pady=10)
btn_acessar_compartilhado.pack(pady=10)

# Executa a interface gráfica
janela_principal.mainloop()
