from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId  # Importar para converter IDs
from cryptography.fernet import Fernet
import hashlib
import base64
from cryptography.fernet import InvalidToken
from datetime import datetime, timedelta
import json

#pegando URI do mongo
uri = "mongodb+srv://Kenzo:123@brunao.u01owig.mongodb.net/?retryWrites=true&w=majority&appName=Brunao" 
cliente = MongoClient(uri)

with open("chave.key", "rb") as chave_arquivo:
    chave = chave_arquivo.read()
fernet = Fernet(chave)

def verificar_chave(conteudo_esperado):
    chave_esperada_hash = conteudo_esperado  # Substitua pelo hash da chave original gerada uma vez.
    try:
        with open("chave.key", "rb") as chave_arquivo:
            chave = chave_arquivo.read()
            return chave
    except FileNotFoundError:
        print("Arquivo de chave não encontrado.")
        return False

def criptografar_conteudo(conteudo):
    resultado = fernet.encrypt(conteudo.encode()) 
    return resultado  # Converte o texto criptografado em string para salvar no MongoDB

def descriptografar_conteudo(conteudo):
    resultado = fernet.decrypt(conteudo).decode()
    return resultado

def gerar_chave_temporaria(tempo_validade_minutos):
    chave_temporaria = Fernet.generate_key()
    data_expiracao = datetime.now() + timedelta(minutes=tempo_validade_minutos)
    return chave_temporaria, data_expiracao

def compartilhar_registro_temporario(colecao, id_paciente, tempo_validade_minutos):
    chave_temporaria, data_expiracao = gerar_chave_temporaria(tempo_validade_minutos)
    fernet_temporario = Fernet(chave_temporaria)
    
    # Buscar o registro do paciente
    paciente = colecao.find_one({"_id": ObjectId(id_paciente)})
    if paciente:
        registro_criptografado_nome = fernet.decrypt(paciente['nome']).decode()
        registro_criptografado_historico = fernet.decrypt(paciente['Historico medico']).decode()
        registro_criptografado_tratamento = fernet.decrypt(paciente['tratamento']).decode()

        
        # Criptografar com a chave temporária
        registro_temporario_nome = fernet_temporario.encrypt(registro_criptografado_nome.encode())
        registro_temporario_historico = fernet_temporario.encrypt(registro_criptografado_historico.encode())
        registro_temporario_tratamento = fernet_temporario.encrypt(registro_criptografado_tratamento.encode())
        
        # Salvar os dados de compartilhamento em um arquivo JSON
        dados_compartilhamento = {
            "chave": chave_temporaria.decode(),
            "expira_em": data_expiracao.isoformat(),
            "registro_nome": registro_temporario_nome.decode(),
            "registro_historico": registro_temporario_historico.decode(),
            "registro_tratamento": registro_temporario_tratamento.decode()
        }
        
        with open("compartilhamento_temporario.json", "w") as arquivo:
            json.dump(dados_compartilhamento, arquivo)
        
        print("Registro compartilhado com sucesso!")
    else:
        print("Paciente não encontrado.")

def acessar_registro_compartilhado():
    try:
        with open("compartilhamento_temporario.json", "r") as arquivo:
            dados = json.load(arquivo)
        
        chave_temporaria = dados["chave"].encode()
        data_expiracao = datetime.fromisoformat(dados["expira_em"])

        if datetime.now() > data_expiracao:
            print("A chave temporária expirou e o acesso foi negado.")
            return None

        fernet_temporario = Fernet(chave_temporaria)
        registro_descriptografado_nome = fernet_temporario.decrypt(dados["registro_nome"].encode())
        registro_descriptografado_historico = fernet_temporario.decrypt(dados["registro_historico"].encode())
        registro_descriptografado_tratamento = fernet_temporario.decrypt(dados["registro_tratamento"].encode())
        print("Registro NOME descriptografado:", registro_descriptografado_nome.decode())
        print("Registro HISTORICO MEDICO descriptografado:", registro_descriptografado_historico.decode())
        print("Registro TRATAMENTO descriptografado:", registro_descriptografado_tratamento.decode())
        return registro_descriptografado_nome + registro_descriptografado_historico + registro_descriptografado_tratamento
    except (FileNotFoundError, InvalidToken):
        print("Erro ao acessar o registro compartilhado ou chave inválida.")
        return None




def verificar_digito(info): #verificar se a informacao enviada tem numeros, retorna 1 e 0
    
    if info.isdigit(): 
        return 1 
    else:
        return 0 
    
def verificar_conteudo(conteudo_buscado,conteudo_local): #verifica se o conteudo ja existe no banco de dados, retorna 1 e 0
    if colecao.find_one({conteudo_buscado : conteudo_local}):
        return 1
    else:
        return 0


continuar = 0 #controlador do fluxo
try:
    while continuar != 1:

        def cadastrar_paciente(colecao): 
            nome_paciente = input('NOME COMPLETO DO paciente: ')
            while verificar_digito(nome_paciente) == 1: #VERIFICAR DIGITACAO
                print('Nao e possivel cadastrar um paciente com numeros!')
            
                nome_paciente = input('NOME COMPLETO DO paciente: ')
            
            nome_paciente = criptografar_conteudo(nome_paciente)
            
            historico_medico = input('Historico medico: ')  
            while verificar_digito(historico_medico) == 1: #VERIFICAR DIGITACAO 
                print('Nao e possivel cadastrar uma Historico medico com apenas numeros!')
                historico_medico = input('Historico medico: ')

            historico_medico = criptografar_conteudo(historico_medico)
            
            tratamento = input('tratamento: ')
            while verificar_digito(tratamento) == 1: #VERIFICAR DIGITACAO
                print('Nao e possivel cadastrar um tratamento com numeros')
                tratamento = input('tratamento: ')
            tratamento = criptografar_conteudo(tratamento)
            paciente = {'nome': nome_paciente, 'Historico medico': historico_medico, 'tratamento': tratamento} #DICIONARIO PARA ENVIO
            colecao.insert_one(paciente)
            print("paciente cadastrado com sucesso!")

        
        def consulta(colecao):
            todos_pacientes = colecao.find()
            try:
                print('======== APENAS AUTORIZADOS ========')
                conteudo_esperado = input('Digite a sua senha para continuar : \n')
                if verificar_chave(conteudo_esperado):
                    print('==== SENHA AUTORIZADA ====') 
                    print('Pacientes Registrados:')
                    for paciente in todos_pacientes:
                        nome = descriptografar_conteudo(paciente['nome'])
                        print(f"Nome: {nome}")
                        print(f"ID: {paciente['_id']}")
                        print('-' * 40)

                    fluxo = input('Deseja visualizar um paciente específico? (s/n): ').lower()
                    if fluxo == 's':
                        paciente_especifico = input('Digite o ID do paciente: ')
                        try:
                            object_id = ObjectId(paciente_especifico)  # Converte para ObjectId
                            busca = colecao.find_one({"_id": object_id})
                            if busca:
                                nome = descriptografar_conteudo(busca['nome'])
                                historico_medico = descriptografar_conteudo(busca['Historico medico'])
                                tratamento = descriptografar_conteudo(busca['tratamento'])
                                print('-' * 40)
                                print(f"Nome do paciente: {nome}")
                                print(f"Histórico médico: {historico_medico}")
                                print(f"Tratamento: {tratamento}")
                            else:
                                print("Paciente não encontrado.")
                        except Exception as e:
                            print(f"Erro ao buscar paciente específico: {e}")
                else:
                    print('CHAVE INCORRETA')
                    exit()
            except Exception as e:
                print(f"Ocorreu um erro ao exibir os dados: {e}")

        def consulta_compartilhada(colecao):
            resp = input('1 - Compartilhar registro / 2 - Acessar registro compartilhado\n')
            if resp == '1':
                registro_compartilhado = input('Qual o ID do registro que deseja compartilhar? \n')
                tempo = int(input('Digite o tempo de validade (minutos) da chave temporaria:'))
                compartilhar_registro_temporario(colecao,registro_compartilhado,tempo)
            elif resp == '2':
                acessar_registro_compartilhado()



                

              
        
        

       
       
    # Funções de mapeamento de opções

        def opca_cadastro_paciente():
            cadastrar_paciente(colecao)

        def opcao_acessar_consulta():
            consulta(colecao)

        def opcao_consulta_compartilhada():
            consulta_compartilhada(colecao)


        # Main
        try:
            meu_banco = cliente['Projeto4BIM'] #pegando o banco
            colecao = meu_banco['Registro Medico'] #pegando a colecao

            print('====CONECTADO AO GERENCIAMENTO DE REGISTROS MEDICOS ==== \n O que pretende fazer?')
            resp = input('1 - Cadastro de Paciente   / 2 - Acessar consulta  / 3 - Acessar consulta compartilhada \n')

            switch = { #switch para controlar as opcoes 
                '1': opca_cadastro_paciente,
                '2': opcao_acessar_consulta,
                '3': opcao_consulta_compartilhada,
                #'5': opcao_remover,
                #'6': opcao_update
            }

            funcao = switch.get(resp) #.get serve para pegar a opcao do SWITCH CASE
            if funcao: # verifica se funcao nao eh null
                funcao()
            else:
                print("Opção inválida.")
        except Exception as e:
            print(e)

        continuar = int(input('Deseja encerrar o programa? : (1)SIM / (QUALQUER NUMERO INTEIRO)NAO \n'))

except Exception as e:
    print(f'Digito invalido{e}')