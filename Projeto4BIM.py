from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId  # Importar para converter IDs
from cryptography.fernet import Fernet
import hashlib
import base64
from cryptography.fernet import InvalidToken

#pegando URI do mongo
uri = "mongodb+srv://Kenzo:123@brunao.u01owig.mongodb.net/?retryWrites=true&w=majority&appName=Brunao" 
cliente = MongoClient(uri)

with open("chave.key", "rb") as chave_arquivo:
    chave = chave_arquivo.read()
fernet = Fernet(chave)


def criptografar_conteudo(conteudo):
    resultado = fernet.encrypt(conteudo.encode()) 
    return resultado  # Converte o texto criptografado em string para salvar no MongoDB


def descriptografar_conteudo(conteudo):
    resultado = fernet.decrypt(conteudo).decode()
    return resultado


def criptografia_senha(senha):
    sha_signature = hashlib.sha256(senha.encode()).hexdigest()
    return sha_signature




def comparar_senha(conteudo_buscado,conteudo_local):
   if colecao.find_one({conteudo_buscado : conteudo_local }):
       return 1
   else:
       return 0

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

        def cadastrar_profissional(colecao):
            nome_profissional = input('NOME DO PROFISSIONAL: ')
            while verificar_digito(nome_profissional) == 1: #VD
                print('Nao e possivel cadastrar um profissional com numeros')
                nome_profissional = input('NOME DO PROFISSIONAL: ')
            senha_profissional = input('SENHA DO PROFISSIONAL: ')
            
            nome_profissional = criptografar_conteudo(nome_profissional)       
            senha_profissional = criptografia_senha(senha_profissional)
            
            profissional = {'nome DO PROFISSIONAL': nome_profissional, 'SENHA DO PROFISSIONAL': senha_profissional} #DE           
            colecao.insert_one(profissional)
            print("profissional cadastrado com sucesso!")
       
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
            senha_profissional = input('Para acessar os dados dos pacientes, digite a sua senha: ')
            senha_profissional_hash = criptografia_senha(senha_profissional)
            
            profissional = colecao.find_one({'SENHA DO PROFISSIONAL': senha_profissional_hash})
            if profissional:
                print('Senha válida.')
                #todos_pacientes = colecao.find()
                dados_testes = input("teste : ")
                conteudo_criptografado = criptografar_conteudo(dados_testes)
                aux = {'teste': conteudo_criptografado}
                resultado = colecao.insert_one(aux)
                print("Conteúdo criptografado para teste:", conteudo_criptografado)
                conteudo_retornado = colecao.find(aux)
                if isinstance(conteudo_retornado, str):
                    conteudo_retornado = conteudo_retornado.encode('utf-8')
                    print(descriptografar_conteudo(conteudo_retornado))



                todos_pacientes = colecao.find()
                try:
                    for paciente in todos_pacientes:
                        nome = descriptografar_conteudo(paciente.get('nome', '').strip())
                        historico_medico = descriptografar_conteudo(paciente.get('Historico medico', '').strip())
                        tratamento = descriptografar_conteudo(paciente.get('tratamento', '').strip())
                        print("Nome do paciente:", nome)
                        print("Histórico médico:", historico_medico)
                        print("Tratamento:", tratamento)
                except Exception as e:
                    print(f"Ocorreu um erro ao exibir os dados: {e}")
                    # Para depuração, você pode adicionar mais detalhes, como:
                    import traceback
                    traceback.print_exc()  # Isso imprimirá o rastreamento completo da exceção.


                

                # Solicita o nome do paciente que deseja acessar
                nome_paciente = input('Qual o nome do paciente que deseja acessar? \n ')

                # Recupera todos os registros de paciente
                # Variável para armazenar se o paciente foi encontrado
                paciente_encontrado = False

                    # Descriptografa o nome do paciente
                    
                    
                    # Verifica se o nome do paciente corresponde
                        
                
                if not paciente_encontrado:
                    print("Paciente nao encontrado.")
            else:
                print("Senha incorreta. Acesso negado.")
        

        """""
        def consultar(colecao):
            escolha = input('Qual consulta você deseja fazer? \n (1) paciente \n (2) PROFESSOR \n (3) profissional (4) TODOS OS REGISTROS \n')
            
            if escolha == '1':
                nome_paciente_consulta = input('NOME COMPLETO DO paciente PARA CONSULTA: ')
                paciente_consulta = {'nome': nome_paciente_consulta}
                resultados = colecao.find(paciente_consulta)
                for resultado in resultados:
                    print(f"ID: {resultado['_id']}") #Pegando ID da busca
                    print(f"Nome: {resultado.get('nome', 'N/A')}") #.GET = pegar valores do campo. SE ESTIVER VAZIO vai aparecer N/A!
                    print(f"Matrícula: {resultado.get('Historico medico', 'N/A')}")
                    print(f"tratamento: {resultado.get('tratamento', 'N/A')}")
                    print("-" * 40)
            
            elif escolha == '2':
                nome_professor_consulta = input('NOME COMPLETO DO PROFESSOR PARA CONSULTA: ')
                professor_consulta = {'nome do professor': nome_professor_consulta}
                resultados = colecao.find(professor_consulta)
                for resultado in resultados:
                    print(f"ID: {resultado['_id']}")
                    print(f"Nome do Professor: {resultado.get('nome do professor', 'N/A')}")
                    print(f"Departamento: {resultado.get('departamento do professor', 'N/A')}")
                    print("-" * 40)
            
            elif escolha == '3':
                nome_profissional_consulta = input('NOME DO PROFISSIONAL PARA CONSULTA: ')
                profissional_consulta = {'nome DO PROFISSIONAL': nome_profissional_consulta}
                resultados = colecao.find(profissional_consulta)
                for resultado in resultados:
                    print(f"ID: {resultado['_id']}")
                    print(f"Nome DO PROFISSIONAL: {resultado.get('nome DO PROFISSIONAL', 'N/A')}")
                    print(f"Código DO PROFISSIONAL: {resultado.get('SENHA DO PROFISSIONAL', 'N/A')}")
                    print(f"Professor Responsável: {resultado.get('professor responsavel', 'N/A')}")
                    print("-" * 40)
            
            elif escolha == '4':
                todos_registros = colecao.find()
                for registro in todos_registros:
                    print(f"ID: {registro['_id']}")
                    print(f"Nome: {registro.get('nome', 'N/A')}")
                    print(f"Matrícula: {registro.get('Historico medico', 'N/A')}")
                    print(f"tratamento: {registro.get('tratamento', 'N/A')}")
                    print(f"Nome do Professor: {registro.get('nome do professor', 'N/A')}")
                    print(f"Departamento: {registro.get('departamento do professor', 'N/A')}")
                    print(f"Nome DO PROFISSIONAL: {registro.get('nome DO PROFISSIONAL', 'N/A')}")
                    print(f"Código DO PROFISSIONAL: {registro.get('SENHA DO PROFISSIONAL', 'N/A')}")
                    print(f"Professor Responsável: {registro.get('professor responsavel', 'N/A')}")
                    print("-" * 40)
            
            else:
                print("Consulta inválida.")
                

            id = input('Digite o ID do documento para remover (ex: 60b9b8f8e4b0c54c9e8d25b3): ')
            try:
                object_id = ObjectId(id) #transforma em objetoID
                result = colecao.delete_one({'_id': object_id}) #deletando objeto
                if result.deleted_count > 0: #se deletou..
                    print("Documento removido com sucesso!")
                else:
                    print("Nenhum documento encontrado com o ID fornecido.")
            except Exception as e:
                print(f"Erro ao remover o documento: {e}")
            """
       
    # Funções de mapeamento de opções
        def opcao_cadastro_profissional():
            cadastrar_profissional(colecao)

        def opca_cadastro_paciente():
            cadastrar_paciente(colecao)

        def opcao_acessar_consulta():
            consulta(colecao)

        def opcao_consulta_compartilhada():
            consultar(colecao)


        # Main
        try:
            meu_banco = cliente['Projeto4BIM'] #pegando o banco
            colecao = meu_banco['Registro Medico'] #pegando a colecao

            print('====CONECTADO AO GERENCIAMENTO DE REGISTROS MEDICOS ==== \n O que pretende fazer?')
            resp = input('1 - Cadastro de Profissional / 2 - Cadastro de Paciente   / 3 - Acessar consulta  / 4 - Acessar consulta compartilhada \n')

            switch = { #switch para controlar as opcoes
                '1': opcao_cadastro_profissional,
                '2': opca_cadastro_paciente,
                '3': opcao_acessar_consulta,
                '4': opcao_consulta_compartilhada,
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