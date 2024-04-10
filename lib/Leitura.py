# -*- coding: utf-8 -*-

#   Neste arquivo encontram-se as funcoes de leitura do modelo.
#   Aqui ha' coisas como verificacao de arquivos de entrada, leitura e geracao de diretorios.
#   E' onde o modelo acessa os dados fornecidos pelo usuario para executa'-lo.


#   Import das bibliotecas Python
from os import path, listdir
from numpy import array, float64
from tkinter import Tk
from tkinter import filedialog
#   Import das bibliotecas customizadas
from Hydrolib import calcular_TC_Kirpich
from Utilidades import atualizarBarraProgresso, contarLinhas, mensagensSelecaoArquivos
from Utilidades import mensagensIntegridadeArquivos,  mensagensIntegridadeInfoGerais
from Utilidades import mensagensIntegridadeChuvas,    mensagensIntegridadePQ
from Utilidades import mensagensIntegridadePULS,      mensagensIntegridadeMKC
from Utilidades import mensagensIntegridadeJUN,       mensagensIntegridadeHIDRO
from Utilidades import mensagensIntegridadeDERIVACAO, mensagensIntegridadeArquivosObservados
from Utilidades import mensagensIntegridadePlotagens
from Utilidades import mensagensIntegridadePlotagensPQ,    mensagensIntegridadePlotagensPULS
from Utilidades import mensagensIntegridadePlotagensMKC,   mensagensIntegridadePlotagensJUN
from Utilidades import mensagensIntegridadePlotagensHIDRO, mensagensIntegridadePlotagensDERIVACAO


#----------------------------------------------------------------------
def determinarDiretorios(isFolder, diretorio_do_software):
    """"""
    #   Testar se e' um arquivo ou uma pasta como entrada...
    if isFolder == False:
        #   Lendo arquivo de entrada ---> diretorio_saida == diretorio de entrada
        diretorios_arquivos_entrada, diretorio_saida = gerenciarLeitura(diretorio_do_software)

    #   Trata-se de uma pasta...
    else:
        #   Ja retorna a lista
        diretorio_pasta_entrada, arquivos_da_pasta = gerenciarLeituraPasta(diretorio_do_software)
        #   Pasta de saida igual da entrada
        diretorio_saida = diretorio_pasta_entrada # ---> diretorio_saida == diretorio de entrada
        #   Corrigir erro
        if not diretorio_pasta_entrada == None:
            #   Criar a lista dos diretorios dos arquivos.
            diretorios_arquivos_entrada = [diretorio_pasta_entrada + "/".encode() + arquivos_da_pasta[ii] for ii in range(len(arquivos_da_pasta))]
        #   Corrigir ero
        else: diretorios_arquivos_entrada = [None]
    
    #   "gimme gimme!"
    return diretorios_arquivos_entrada, diretorio_saida
#----------------------------------------------------------------------
def gerenciarLeitura(diretorio_do_software):
    """"""
    #   Abra o arquivo... Se 'diretorio_arquivo_entrada' == None, o arquivo nao e' txt.
    diretorio_arquivo_entrada = procurarArquivo(diretorio_do_software)
    
    #   Se um diretorio foi detectado, e' um arquivo txt.
    if not diretorio_arquivo_entrada == None:
        #   Selecionar extensao
        extensao_arquivo = diretorio_arquivo_entrada.decode().split("/")[-1].split(".")[-1]
        
        #   Verificar se um arquivo txt foi selecionado
        if (extensao_arquivo == "hyd") or (extensao_arquivo == "HYD"):
            #   integridade_entrada guarda os resultados dos testes de integridade
            integridade_entrada = [False, False, False]
            #   Faca o teste de integridade do arquivo, isto vou deixar para depois.
            integridade_entrada[0], entrada_operacoes = checarIntegridadeEntrada(diretorio_arquivo_entrada)
            
            #   As verificacoes mais complexas farei em funcoes separadas.
            #   Verificar unicidade das operacoes
            if integridade_entrada[0] == True:
                #   So' testo a segunda se passou na primeira (otimizacao e correcao de bug)
                integridade_entrada[1] = checarUnicidade(entrada_operacoes)
            
            #   Verificar logica circular das operacoes
            if integridade_entrada[1] == True:
                #   So' testo a terceira se passou na segunda (otimizacao e correcao de bug)
                integridade_entrada[2], ordem_operacoes = checarLogicaCircular(entrada_operacoes)
        
            #   Se o arquivo for integro (nao possuir erros), continue
            if not False in integridade_entrada:
                #   Armazenar o diretorio de saida
                diretorio_saida = path.dirname(diretorio_arquivo_entrada)
                #   Retorne o diretorio
                return [diretorio_arquivo_entrada], diretorio_saida
            #   Arquivo ruim
            else:
                print ("\n\tArquivo de entrada com problemas. Cheque seu arquivo de entrada.\n")
                return [None], None
        #   Formato incorreto
        else:
            print ("\n\tExtensao do arquivo de entrada e' incompativel.\n")
            mensagensSelecaoArquivos(1, '')
            return [None], None
    #   Se NAO for dado um arquivo de entrada
    else:
        print ("\n\tNenhum arquivo selecionado.\n")
        mensagensSelecaoArquivos(2, '')
        return [None], None
#----------------------------------------------------------------------
def procurarArquivo(diretorio_do_software):
    """Abre a janela para procurar um arquivo de entrada"""
    #   Iniciar nova janela
    root4 = Tk()
    root4.withdraw()
    entrada = filedialog.askopenfile(mode = 'r', title = "Selecione o arquivo de entrada", initialdir = diretorio_do_software)
    root4.destroy()
    
    #    verificar se algo foi selecionado
    if (not entrada == None):
        #   Armazenar nome
        diretorio_arquivo_entrada = entrada.name
        #   Fechar aquivo
        entrada.close()
        #   Retornar informacao relevante
        return diretorio_arquivo_entrada.encode()
    #   Nada foi selecionado
    else:
        return None
#----------------------------------------------------------------------
def gerenciarLeituraPasta(diretorio_do_software):
    """"""
    #   Abra o arquivo... Se 'diretorio_arquivo_entrada' == None, o arquivo nao e' txt.
    diretorio_pasta_entrada = procurarPasta(diretorio_do_software)
    
    #   Se um diretorio foi detectado, e' um arquivo txt.
    if not diretorio_pasta_entrada == None:
        #   Listar os arquivos presentes nesta pasta... Nome.extensao
        arquivos_da_pasta = listdir(diretorio_pasta_entrada) 
        #   Variavel Auxiliar
        arquivos_deletados = 0
        
        #   Loop para tirar os arquivos de saida (ohy) e (txt) dos diretorios de entrada
        for numero_arquivo in range(len(arquivos_da_pasta)):
            #   Selecionar extensao
            extensao_arquivo = arquivos_da_pasta[numero_arquivo - arquivos_deletados].decode().split(".")[-1]
            #   Testar extensao
            if (not extensao_arquivo == "hyd") and (not extensao_arquivo == "HYD"):
                #   Delete o arquivo da lista
                del arquivos_da_pasta[numero_arquivo - arquivos_deletados]
                #   Somar um...
                arquivos_deletados += 1
        
        #   Se nao sobrou nenhum arquivo na lista, e' porque nenhum deles e' valido
        if len(arquivos_da_pasta) == 0:
            print ("\n\tNenhum dos arquivos da pasta possui o formato valido.\n")
            mensagensSelecaoArquivos(3, '')
            return None, None

        #   Loop principal... de arquivo em arquivo
        for indice_arquivo, nome_arquivo in enumerate(arquivos_da_pasta):# range(len(arquivos_da_pasta)):
            #   Especificar arquivo
            diretorio_arquivo_entrada = (diretorio_pasta_entrada + "/".encode() + nome_arquivo)
            #   Selecionar extensao
            extensao_arquivo = nome_arquivo.decode().split(".")[-1]
        
            #   Verificar se um arquivo txt foi selecionado
            if (extensao_arquivo == "hyd") or (extensao_arquivo == "HYD"):
                #   integridade_entrada guarda os resultados dos testes de integridade
                integridade_entrada = [False, False, False]
                #   Faca o teste de integridade do arquivo, isto vou deixar para depois.
                integridade_entrada[0], entrada_operacoes = checarIntegridadeEntrada(diretorio_arquivo_entrada)
            
                #   As verificacoes mais complexas farei em funcoes separadas.
                #   Verificar unicidade das operacoes
                if integridade_entrada[0] == True:
                    #   So' testo a segunda se passou na primeira (otimizacao e correcao de bug)
                    integridade_entrada[1] = checarUnicidade(entrada_operacoes)
                
                #   Verificar logica circular das operacoes
                if integridade_entrada[1] == True:
                    #   So' testo a terceira se passou na segunda (otimizacao e correcao de bug)
                    integridade_entrada[2], ordem_operacoes = checarLogicaCircular(entrada_operacoes)
                
                #   Se o arquivo for integro (nao possuir erros), continue
                if not False in integridade_entrada:
                    #   Testar se e' o ultimo loop
                    if (indice_arquivo + 1) == len(arquivos_da_pasta):
                        #   Retorne o diretorio
                        return diretorio_pasta_entrada, arquivos_da_pasta
                #   Arquivo ruim
                else:
                    print ("\n\tArquivo '%s' com problemas.\n\tCheque seu arquivo de entrada.\n" %(nome_arquivo.decode()))
                    return None, None
            #   Formato incorreto
            else:
                print ("\n\tO formato do arquivo '%s' nao adequado.\n" %(nome_arquivo.decode()))
                mensagensSelecaoArquivos(4, nome_arquivo.decode())
                return None, None
    #   Se NAO for dado um arquivo de entrada
    else:
        print ("\n\tNenhuma pasta selecionada.\n")
        mensagensSelecaoArquivos(5, '')
        return None, None
#----------------------------------------------------------------------
def procurarPasta(diretorio_do_software):
    """Abre a janela para procurar uma pasta com arquivos de entrada"""
    #   Iniciar nova janela
    root4 = Tk()
    root4.withdraw()
    pasta = filedialog.askdirectory(title = "Selecione o diretorio com os arquivos de entrada", initialdir = diretorio_do_software)
    root4.destroy()
    
    #    verificar se algo foi selecionado
    if (not pasta == '') and (not pasta == None):
        #   Armazenar nome
        diretorio_pasta_entrada = pasta.encode()
       #   Testar se o diretorio e' valido, remocao de erros basicamente
        if (path.isdir(diretorio_pasta_entrada) == True):
            #   Retornar informacao relevante
            return diretorio_pasta_entrada
        #   Diretorio nao existe
        else:
            #   Avisa duas vezes
            mensagensSelecaoArquivos(6, diretorio_pasta_entrada.decode())
            return None
    #   Nada foi selecionado
    else:
        return None
#----------------------------------------------------------------------
def checarIntegridadeEntrada(diretorio_arquivo_entrada):
    """Testa o conteudo do arquivo de entrada em busca de erros de digitacao."""
    #   Diretorio do arquivo de entrada
    diretorio_pasta_entrada = path.dirname(diretorio_arquivo_entrada)
    #   Avisar que estamos testando
    print ("\n\tExaminando o arquivo: %s" %(diretorio_arquivo_entrada.decode().split("/")[-1]))
    #   Contar numero de linhas
    numero_linhas = contarLinhas(diretorio_arquivo_entrada)
    linhas_lidas = 0
    
    #   Declarar auxiliares
    linhas_comentario = 0
    nch = 0
    nop = 0
    nblocos = 0
    numero_intervalos_tempo = 0
    numero_intervalos_tempo_chuva = 0
    numero_estruturas_puls = 0
    nch_declaradas = 0
    nop_declaradas = 0
    integridade_entrada = True # Comeco dizendo que e' belezinha, mas no final da funcao eu avalio melhor
    
    #   Abrir arquivo de entrada
    arquivo_entrada = open(diretorio_arquivo_entrada, 'r')
    
    #   Ler arquivo de entrada ate' pegar inicio
    conteudo_linha = arquivo_entrada.readline().split(";")
    linhas_lidas += 1
    
    #   Desconsiderar comentario
    while (not conteudo_linha[0] == "INICIO"):
        #   Cuidar se existe a palavra "INICIO" no arquivo de entrada
        if linhas_comentario < numero_linhas:
            #   Ler arquivo de entrada ate' pegar inicio
            conteudo_linha = arquivo_entrada.readline().split(";")
            linhas_lidas += 1
            #   Acrescer comentario
            linhas_comentario += 1
        #   Nao ha' a palavra "INICIO"
        else:
            #   Avise o usuario
            arquivo_entrada.close(); mensagensIntegridadeArquivos(1, linhas_lidas, nch, nop, nch_declaradas, nop_declaradas, ""); return False, None
    
    #   Testar tamanho da linha
    if not len(conteudo_linha) == 7:
        #   Avise o usuario
        arquivo_entrada.close(); mensagensIntegridadeInfoGerais(1, linhas_lidas); return False, None
    
    #   Leu inicio, teste informacoes gerais
    try: int(conteudo_linha[1]) #numero_intervalos_tempo
    except: arquivo_entrada.close(); mensagensIntegridadeInfoGerais(2, linhas_lidas); return False, None
    
    try: int(conteudo_linha[2]) #duracao_intervalo_tempo
    except: arquivo_entrada.close(); mensagensIntegridadeInfoGerais(3, linhas_lidas); return False, None
    
    try: int(conteudo_linha[3]) #numero_chuvas
    except: arquivo_entrada.close(); mensagensIntegridadeInfoGerais(4, linhas_lidas); return False, None
    
    try: int(conteudo_linha[4]) #numero_intervalos_tempo_chuva
    except: arquivo_entrada.close(); mensagensIntegridadeInfoGerais(5, linhas_lidas); return False, None
    
    try: int(conteudo_linha[5]) #numero_operacoes_hidrologicas
    except: arquivo_entrada.close(); mensagensIntegridadeInfoGerais(6, linhas_lidas); return False, None

    #   Se o nint_tempo_chuva > nint_tempo, ta errado
    if int(conteudo_linha[4]) > int(conteudo_linha[1]):
        #   Avise o usuario
        arquivo_entrada.close(); mensagensIntegridadeInfoGerais(7, linhas_lidas); return False, None
        
    #   Armazenar os valores
    numero_intervalos_tempo = int(conteudo_linha[1]) 
    numero_intervalos_tempo_chuva = int(conteudo_linha[4])
    nch_declaradas = int(conteudo_linha[3])
    nop_declaradas = int(conteudo_linha[5])
    #   0: nao precisa de outra operacao; >0: representa o numero da op de entrada dessa operacao
    #   Essa variavel e' feita duas vezes. Faz-se aqui pois precisamos dela pra avaliar unicidade e logica circular.
    #   Ela nao e' carregada adiante apenas pra deixar o code mais limpo
    entrada_operacoes = [0 for ii in range(nop_declaradas)] 
    
    #   Nao pode ser zero
    if int(conteudo_linha[1]) == 0:
        arquivo_entrada.close(); mensagensIntegridadeInfoGerais(8, linhas_lidas); return False, None
    if int(conteudo_linha[2]) == 0:
        arquivo_entrada.close(); mensagensIntegridadeInfoGerais(9, linhas_lidas); return False, None
    if (nch_declaradas > 0) and (int(conteudo_linha[4]) == 0):
        arquivo_entrada.close(); mensagensIntegridadeInfoGerais(10, linhas_lidas); return False, None
    if int(conteudo_linha[5]) == 0:
        arquivo_entrada.close(); mensagensIntegridadeInfoGerais(11, linhas_lidas); return False, None
        
    #   Ver quantos blocos de leitura
    nblocos = int(conteudo_linha[3]) + int(conteudo_linha[5])
    
    #   Loop para ler o restante:
    for bloco in range(nblocos):
        #   Ler a linha
        conteudo_linha = arquivo_entrada.readline().split(";")
        linhas_lidas += 1
        #   Tirar os espacos em branco, se houver
        while conteudo_linha[0][0] == " ":
            conteudo_linha[0] = conteudo_linha[0][1:]
        #   Testar conteudo
        #   Se for chuva
        if conteudo_linha[0] == "CHUVA":
            #   Testar tamanho da linha
            if len(conteudo_linha) < 3:
                #   Avise o usuario
                arquivo_entrada.close(); mensagensIntegridadeChuvas(1, linhas_lidas, (nch+1), ""); return False, None
        
            #   Testar o numero dela
            try: int(conteudo_linha[1]) #numero da chuva
            except: arquivo_entrada.close(); mensagensIntegridadeChuvas(2, linhas_lidas, nch, ""); return False, None
            
            #   Testar o numero dela
            if (int(conteudo_linha[1]) == (nch+1)):
                #   Ler a linha
                conteudo_linha = arquivo_entrada.readline().split(";")
                linhas_lidas += 1
                #   Testar se e' IDF ou OBS
                if conteudo_linha[0] == "IDF":
                    #   Testar tamanho da linha
                    if len(conteudo_linha) < 10:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(3, linhas_lidas, (nch+1), ""); return False, None
                        
                    #   TEstar valores das linhas
                    try: int(conteudo_linha[1]) #tipo IDF
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(4, linhas_lidas, nch, ""); return False, None
                    
                    try: float(conteudo_linha[2]) #posicao do pico
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(5, linhas_lidas, nch, ""); return False, None
                    
                    try: int(conteudo_linha[3]) #tempo de retorno
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(6, linhas_lidas, nch, ""); return False, None
                    
                    try: float(conteudo_linha[4]) #parametro a
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(7, linhas_lidas, nch, ""); return False, None
                    
                    try: float(conteudo_linha[5]) #parametro b
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(8, linhas_lidas, nch, ""); return False, None
                    
                    try: float(conteudo_linha[6]) #parametro c
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(9, linhas_lidas, nch, ""); return False, None
                    
                    try: float(conteudo_linha[7]) #parametro d
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(10, linhas_lidas, nch, ""); return False, None
                    
                    try: int(conteudo_linha[8]) #limitante
                    except: arquivo_entrada.close(); mensagensIntegridadeChuvas(11, linhas_lidas, nch, ""); return False, None
                    
                    #   Nao pode ser zero
                    if not int(conteudo_linha[1]) == 1:
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(12, linhas_lidas, nch, str(conteudo_linha[1])); return False, None
                    if (float(conteudo_linha[2]) < 0) or (float(conteudo_linha[2]) > 1):
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(13, linhas_lidas, nch, ""); return False, None
                    if int(conteudo_linha[3]) == 0:
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(14, linhas_lidas, nch, ""); return False, None
                    if float(conteudo_linha[4]) <= 0.0:
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(15, linhas_lidas, nch, ""); return False, None
                    if float(conteudo_linha[5]) <= 0.0:
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(16, linhas_lidas, nch, ""); return False, None
                    if float(conteudo_linha[6]) <= 0.0:
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(17, linhas_lidas, nch, ""); return False, None
                    if float(conteudo_linha[7]) <= 0.0:
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(18, linhas_lidas, nch, ""); return False, None
                    if int(conteudo_linha[8]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(19, linhas_lidas, nch, ""); return False, None
                    
                #   Se for chuva observada
                elif conteudo_linha[0] == "OBS":
                    #   Testar tamanho da linha
                    if not len(conteudo_linha) == 3:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(1, linhas_lidas, (nch+1), ""); return False, None
                        
                    #   Substituir a \ por /
                    conteudo_linha[1] = conteudo_linha[1].replace("\\","/")
                
                    #   Tirar os espacos em branco do diretorio informado, se houver
                    while conteudo_linha[1][0] == " ":
                        conteudo_linha[1] = conteudo_linha[1][1:]
                        
                    #   Verificar se o arquivo existe
                    if (path.isfile(conteudo_linha[1]) == True):
                        #   Selecionar ultimo nome
                        extensao_arquivo = conteudo_linha[1].split("/")
                        #   Selecionar extensao
                        extensao_arquivo = extensao_arquivo[-1].split(".")[-1]
                        
                        #   Verificar se a extensao dele e' txt 
                        if ((extensao_arquivo == "txt") or (extensao_arquivo == "TXT")):
                            #   Testar o arquivo de entrada
                            integridade_arquivo, linha = checarIntegridadeArquivoTexto(conteudo_linha[1], numero_intervalos_tempo_chuva)
                            
                            #   Se deu bom, faca nada, mas se deu ruim....
                            if not integridade_arquivo == True:
                                #   Que ruim que deu?
                                if linha == 0: #    Numero de dados incorretos
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(1, linha, (nch+1), nop, numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                                
                                else: # Linha X e' o problema
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(2, linha, (nch+1), nop, numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                        
                        #   Nao e' txt
                        else: 
                            #   Avise o usuario
                            arquivo_entrada.close(); mensagensIntegridadeChuvas(20, linhas_lidas, (nch+1), ""); return False, None
                    
                    #   Da pra entrar so' com o nome do arquivo se o mesmo estiver na mesma pasta do arquivo de entrada
                    elif (path.isfile(diretorio_pasta_entrada + "/".encode() + conteudo_linha[1].encode()) == True):
                        #   Selecionar ultimo nome
                        extensao_arquivo = conteudo_linha[1].split("/")
                        #   Selecionar extensao
                        extensao_arquivo = extensao_arquivo[-1].split(".")[-1]
                        
                        #   Verificar se a extensao dele e' txt 
                        if ((extensao_arquivo == "txt") or (extensao_arquivo == "TXT")):
                            #   Testar o arquivo de entrada
                            integridade_arquivo, linha = checarIntegridadeArquivoTexto(diretorio_pasta_entrada + "/".encode() + conteudo_linha[1].encode(), numero_intervalos_tempo_chuva)
                            
                            #   Se deu bom, faca nada, mas se deu ruim....
                            if not integridade_arquivo == True:
                                #   Que ruim que deu?
                                if linha == 0: #    Numero de dados incorretos
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(1, linha, (nch+1), nop, numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                                
                                else: # Linha X e' o problema
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(2, linha, (nch+1), nop, numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                        
                        #   Nao e' txt
                        else: 
                            #   Avise o usuario
                            arquivo_entrada.close(); mensagensIntegridadeChuvas(20, linhas_lidas, (nch+1), ""); return False, None
                    
                    #   Arquivo nao encontrado
                    else: 
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeChuvas(21, linhas_lidas, (nch+1), ""); return False, None
                
                #   Tipo de chuva incorreto
                else: 
                    #   Avise o usuario
                    arquivo_entrada.close(); mensagensIntegridadeChuvas(22, linhas_lidas, (nch+1), str(conteudo_linha[0])); return False, None
                    
            #   Numero incorreto
            else: 
                #   Avise o usuario
                arquivo_entrada.close(); mensagensIntegridadeChuvas(23, linhas_lidas, (nch+1), ""); return False, None
        
            #   Deu tudo certo, some uma chuva
            nch += 1
        
        #   Se for operacao
        elif conteudo_linha[0] == "OPERACAO":
            #   Teste o tipo de operacao
            #   Testar tamanho da linha
            if len(conteudo_linha) < 3:
                #   Avise o usuario
                arquivo_entrada.close(); mensagensIntegridadeArquivos(2, linhas_lidas, nch, (nop+1), nch_declaradas, nop_declaradas, ""); return False, None
        
            #   Testar o numero dela
            try: int(conteudo_linha[1]) #numero da operacao
            except: arquivo_entrada.close(); mensagensIntegridadePQ(1, linhas_lidas, nop, 0, nch_declaradas); return False, None
            
            #   Testar o numero dela
            if (int(conteudo_linha[1]) == (nop+1)):
                #   Ler a linha
                conteudo_linha = arquivo_entrada.readline().split(";")
                linhas_lidas += 1
                
                #   Tirar os espacos em branco se houver
                while conteudo_linha[0][0] == " ":
                    conteudo_linha[0] = conteudo_linha[0][1:]
                
                #   Testar se e' PQ
                if conteudo_linha[0] == "PQ":
                    #   Testar tamanho da linha
                    if not len(conteudo_linha) == 3:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadePQ(2, linhas_lidas, (nop+1), 0, nch_declaradas); return False, None
                    
                    #   Numero da chuva correspondente
                    try: int(conteudo_linha[1]) 
                    except: arquivo_entrada.close(); mensagensIntegridadePQ(3, linhas_lidas, nop, 0, nch_declaradas); return False, None
                    
                    #   Checar se o numero da chuva e' possivel de ser encontrada no arquivo de entrada
                    if int(conteudo_linha[1]) > nch_declaradas:
                        arquivo_entrada.close(); mensagensIntegridadePQ(4, linhas_lidas, (nop+1), (int(conteudo_linha[1])), nch_declaradas); return False, None
                    
                    #   Ler a linha
                    conteudo_linha = arquivo_entrada.readline().split(";")
                    linhas_lidas += 1
                    
                    #   Testar tamanho da linha
                    if not len(conteudo_linha) == 3:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadePQ(5, linhas_lidas, nop, 0, nch_declaradas); return False, None
                    
                    #   Tirar os espacos em branco, se houver
                    while conteudo_linha[0][0] == " ":
                        conteudo_linha[0] = conteudo_linha[0][1:]
                    
                    #   Espera-se um CN
                    if not conteudo_linha[0] == "CN":
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadePQ(6, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                    #   Coeficiente CN
                    try: float(conteudo_linha[1]) 
                    except: arquivo_entrada.close(); mensagensIntegridadePQ(7, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                    #   Testar seu valor
                    if (float(conteudo_linha[1]) <= 0.0) or (float(conteudo_linha[1]) > 100.0):
                        arquivo_entrada.close(); mensagensIntegridadePQ(8, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                    #   Ler a linha
                    conteudo_linha = arquivo_entrada.readline().split(";")
                    linhas_lidas += 1
                    
                    #   Testar tamanho da linha
                    if len(conteudo_linha) < 3:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadePQ(9, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                    #   Tirar os espacos em branco, se houver
                    while conteudo_linha[0][0] == " ":
                        conteudo_linha[0] = conteudo_linha[0][1:]
                        
                    #   Espera-se um HUT
                    if not conteudo_linha[0] == "HUT":
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadePQ(10, linhas_lidas, nop, 0, nch_declaradas); return False, None
                    
                    #   Area
                    try: float(conteudo_linha[1]) 
                    except: arquivo_entrada.close(); mensagensIntegridadePQ(11, linhas_lidas, nop, 0, nch_declaradas); return False, None
                    
                    #   Testar seu valor
                    if (float(conteudo_linha[1]) <= 0.0):
                        arquivo_entrada.close(); mensagensIntegridadePQ(12, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                    #   Tirar os espacos em branco, se houver
                    while conteudo_linha[2][0] == " ":
                        conteudo_linha[2] = conteudo_linha[2][1:]
                    
                    #   Testar TC
                    if "KIRPICH" in conteudo_linha[2]:
                        #   Diferenca cota
                        try: float(conteudo_linha[3]) 
                        except: arquivo_entrada.close(); mensagensIntegridadePQ(13, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        #   Comprimento canal
                        try: float(conteudo_linha[4])
                        except: arquivo_entrada.close(); mensagensIntegridadePQ(14, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                        #   Testar seu valor
                        if (float(conteudo_linha[3]) <= 0.0):
                            arquivo_entrada.close(); mensagensIntegridadePQ(15, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        #   Testar seu valor
                        if (float(conteudo_linha[4]) <= 0.0):
                            arquivo_entrada.close(); mensagensIntegridadePQ(16, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                    else:   #   E' o valor em hora
                        try: float(conteudo_linha[2]) #numero da chuva correspondente
                        except: arquivo_entrada.close(); mensagensIntegridadePQ(17, linhas_lidas, nop, 0, nch_declaradas); return False, None
                        
                        #   Testar seu valor
                        if (float(conteudo_linha[2]) <= 0.0):
                            arquivo_entrada.close(); mensagensIntegridadePQ(18, linhas_lidas, nop, 0, nch_declaradas); return False, None
                    
                    #   Dizer que ela nao precisa da saida de outra operacao, ou seja, 0
                    entrada_operacoes[nop] = 0
                    
                    
                #   Testar se e' PULS
                elif conteudo_linha[0] == "PULS":
                    #   Testar tamanho da linha
                    if not len(conteudo_linha) == 6:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadePULS(1, linhas_lidas, (nop+1), 0, nop_declaradas, ""); return False, None
                    
                    try: int(conteudo_linha[1]) 
                    except: arquivo_entrada.close(); mensagensIntegridadePULS(2, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                    #   Testar seu valor
                    if (int(conteudo_linha[1]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadePULS(3, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                        
                    #   Checar se o numero do hidrograma de entrada e' possivel de ser encontrado no arquivo de entrada
                    if int(conteudo_linha[1]) > nop_declaradas:
                        arquivo_entrada.close(); mensagensIntegridadePULS(4, linhas_lidas, (nop+1), int(conteudo_linha[1]), nop_declaradas, ""); return False, None
                    
                    #   Dizer ao software que essa operacao precisa da saida de outra
                    entrada_operacoes[nop] = int(conteudo_linha[1])
                    
                    #   Cota inicial
                    try: float(conteudo_linha[2]) 
                    except: arquivo_entrada.close(); mensagensIntegridadePULS(5, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                    #   Testar seu valor
                    if (float(conteudo_linha[2]) < 0):
                        arquivo_entrada.close(); mensagensIntegridadePULS(6, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                    #   Vazao do by-pass
                    try: float(conteudo_linha[3]) 
                    except: arquivo_entrada.close(); mensagensIntegridadePULS(7, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                    #   Testar seu valor
                    if (float(conteudo_linha[3]) < 0):
                        arquivo_entrada.close(); mensagensIntegridadePULS(8, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                    #   Numero Estruturas
                    try: int(conteudo_linha[4]) 
                    except: arquivo_entrada.close(); mensagensIntegridadePULS(9, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                    #   Testar seu valor
                    if (int(conteudo_linha[4]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadePULS(10, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                    #   Armazenar
                    numero_estruturas_puls = int(conteudo_linha[4])
                    
                    #   loop para estruturas
                    for estrutura in range(numero_estruturas_puls):
                        #   Ler a linha
                        conteudo_linha = arquivo_entrada.readline().split(";")
                        linhas_lidas += 1
                        
                        #   Tirar os espacos em branco, se houver
                        while conteudo_linha[0][0] == " ":
                            conteudo_linha[0] = conteudo_linha[0][1:]
                        
                        #   Vertedor
                        if conteudo_linha[0] == "VERTEDOR":
                            #   Testar tamanho da linha
                            if not len(conteudo_linha) == 6:
                                #   Avise o usuario
                                arquivo_entrada.close(); mensagensIntegridadePULS(11, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            #   C. descarga
                            try: float(conteudo_linha[1]) 
                            except: arquivo_entrada.close(); mensagensIntegridadePULS(12, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            #   Largura soleira
                            try: float(conteudo_linha[2]) 
                            except: arquivo_entrada.close(); mensagensIntegridadePULS(13, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            #   COta soleira
                            try: float(conteudo_linha[3]) 
                            except: arquivo_entrada.close(); mensagensIntegridadePULS(14, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            #   Cota maxima
                            try: float(conteudo_linha[4]) 
                            except: arquivo_entrada.close(); mensagensIntegridadePULS(15, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            
                            #   Testar os valores
                            if (float(conteudo_linha[1]) <= 0):
                                arquivo_entrada.close(); mensagensIntegridadePULS(16, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            if (float(conteudo_linha[2]) <= 0):
                                arquivo_entrada.close(); mensagensIntegridadePULS(17, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            if (float(conteudo_linha[3]) <= 0):
                                arquivo_entrada.close(); mensagensIntegridadePULS(18, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            if (float(conteudo_linha[4]) <= 0):
                                arquivo_entrada.close(); mensagensIntegridadePULS(19, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                                
                        #   Orificio
                        elif conteudo_linha[0] == "ORIFICIO":
                            #   Testar tamanho da linha
                            if not len(conteudo_linha) == 5:
                                #   Avise o usuario
                                arquivo_entrada.close(); mensagensIntegridadePULS(20, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            #   C. descarga
                            try: float(conteudo_linha[1]) 
                            except: arquivo_entrada.close(); mensagensIntegridadePULS(21, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            #   Altura/Diametro
                            try: float(conteudo_linha[2]) 
                            except: arquivo_entrada.close(); mensagensIntegridadePULS(22, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            #   Cota do centro
                            try: float(conteudo_linha[3]) 
                            except: arquivo_entrada.close(); mensagensIntegridadePULS(23, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                        
                            #   Testar os valores
                            if (float(conteudo_linha[1]) <= 0):
                                arquivo_entrada.close(); mensagensIntegridadePULS(24, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            if (float(conteudo_linha[2]) <= 0):
                                arquivo_entrada.close(); mensagensIntegridadePULS(25, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            if (float(conteudo_linha[3]) <= 0):
                                arquivo_entrada.close(); mensagensIntegridadePULS(26, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                                
                        else: # Bobagem escrita
                            #   Avise o usuario
                            arquivo_entrada.close(); mensagensIntegridadePULS(27, linhas_lidas, nop, 0, nop_declaradas, str(conteudo_linha[0])); return False, None
                        
                    #   Ler a linha
                    conteudo_linha = arquivo_entrada.readline().split(";")
                    linhas_lidas += 1
                    
                    #   Substituir a \ por /
                    conteudo_linha[0] = conteudo_linha[0].replace("\\","/")
                
                    #   Tirar os espacos em branco do diretorio informado, se houver
                    while conteudo_linha[0][0] == " ":
                        conteudo_linha[0] = conteudo_linha[0][1:]
                        
                    #   Curva cota volume
                    #   Verificar se o arquivo existe
                    if (path.isfile(conteudo_linha[0]) == True):
                        #   Selecionar ultimo nome
                        extensao_arquivo = conteudo_linha[0].split("/")
                        #   Selecionar extensao
                        extensao_arquivo = extensao_arquivo[-1].split(".")[-1]
                        
                        #   Verificar se a extensao dele e' txt
                        if ((extensao_arquivo == "txt") or (extensao_arquivo == "TXT")):
                            #   Testar o arquivo de entrada
                            integridade_arquivo, linha = checarIntegridadeArquivoCotaVolume(conteudo_linha[0])
                            
                            #   Se deu ruim
                            if integridade_arquivo == False:
                                #   Que ruim que deu?
                                if linha == 0: #    Numero de dados incorretos
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(5, linha, nch, (nop+1), numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                                
                                else: # Linha X e' o problema
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(6, linha, nch, (nop+1), numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                        
                        else: # nao e' txt
                            #   Avise o usuario
                            arquivo_entrada.close(); mensagensIntegridadePULS(28, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                        
                    #   Da pra entrar so' com o nome do arquivo se o mesmo estiver na mesma pasta do arquivo de entrada
                    elif (path.isfile(diretorio_pasta_entrada + "/".encode() + conteudo_linha[0].encode()) == True):
                        #   Selecionar extensao
                        extensao_arquivo = conteudo_linha[0].split(".")[-1]
                        
                        #   Verificar se a extensao dele e' txt
                        if ((extensao_arquivo == "txt") or (extensao_arquivo == "TXT")):
                            #   Testar o arquivo de entrada
                            integridade_arquivo, linha = checarIntegridadeArquivoCotaVolume(diretorio_pasta_entrada + "/".encode() + conteudo_linha[0].encode())
                            
                            #   Dizer ao programa que essa operacao nao precisa da saida de outra
                            entrada_operacoes[nop] = 0
                            
                            #   Se nao deu bom
                            if integridade_arquivo == False:
                                #   Que ruim que deu?
                                if linha == 0: #    Numero de dados incorretos
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(5, linha, nch, (nop+1), numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                                
                                else: # Linha X e' o problema
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(6, linha, nch, (nop+1), numero_intervalos_tempo_chuva, numero_intervalos_tempo); return False, None
                        #   Nao e' txt
                        else: 
                            #   Avise o usuario
                            arquivo_entrada.close(); mensagensIntegridadePULS(28, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                            
                    #   Nao e' path
                    else: 
                        arquivo_entrada.close(); mensagensIntegridadePULS(29, linhas_lidas, nop, 0, nop_declaradas, ""); return False, None
                    
                
                #   Testar se e' MKC
                elif conteudo_linha[0] == "MKC":
                    #   Testar tamanho da linha
                    if not len(conteudo_linha) == 7:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeMKC(1, linhas_lidas, (nop+1), 0, nop_declaradas); return False, None
                    
                    try: int(conteudo_linha[1]) 
                    except: arquivo_entrada.close(); mensagensIntegridadeMKC(2, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    
                    #   Testar seu valor
                    if (int(conteudo_linha[1]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadeMKC(3, linhas_lidas, nop, 0, nop_declaradas); return False, None
                        
                    #   Checar se o numero do hidrograma de entrada e' possivel de ser encontrado no arquivo de entrada
                    if int(conteudo_linha[1]) > nop_declaradas:
                        arquivo_entrada.close(); mensagensIntegridadeMKC(4, linhas_lidas, (nop+1), (int(conteudo_linha[1])), nop_declaradas); return False, None
                    
                    #   Dizer ao software que essa operacao precisa da saida de outra
                    entrada_operacoes[nop] = int(conteudo_linha[1])
                    
                    #   Diferenca cota (m)
                    try: float(conteudo_linha[2]) 
                    except: arquivo_entrada.close(); mensagensIntegridadeMKC(5, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    #   Comprimento canal (km)
                    try: float(conteudo_linha[3]) 
                    except: arquivo_entrada.close(); mensagensIntegridadeMKC(6, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    #   Largura canal (m)
                    try: float(conteudo_linha[4]) 
                    except: arquivo_entrada.close(); mensagensIntegridadeMKC(7, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    #   Coeficiente de rugosidade
                    try: float(conteudo_linha[5]) 
                    except: arquivo_entrada.close(); mensagensIntegridadeMKC(8, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    
                    #   Testar os valores
                    if (float(conteudo_linha[2]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadeMKC(9, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    if (float(conteudo_linha[3]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadeMKC(10, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    if (float(conteudo_linha[4]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadeMKC(11, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    if (float(conteudo_linha[5]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadeMKC(12, linhas_lidas, nop, 0, nop_declaradas); return False, None
                
                
                #   Testar se e' JUN
                elif conteudo_linha[0] == "JUN":
                    #   NAO e' possivel entrar com diretorios para operacoes de juncao
                    #   Testar tamanho da linha
                    if len(conteudo_linha) < 4:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeJUN(1, linhas_lidas, (nop+1), 0, nop_declaradas); return False, None
                    
                    #   (Re)inicio uma variavel auxiliar para armazenar o numero das operacoes dessa juncao
                    operacoes_juncao = []
                    
                    #   Testar os numeros dos hidrogramas
                    for num_hidros_jun in range(1, len(conteudo_linha)-2):
                        #   Testar se todos os dados da juncao sao numeros
                        try: int(conteudo_linha[num_hidros_jun]) 
                        except: arquivo_entrada.close(); mensagensIntegridadeJUN(2, linhas_lidas, (nop+1), num_hidros_jun, nop_declaradas); return False, None
                        
                        #   Testar a qualidade dos numeros inseridos
                        
                        #   Testar seu valor
                        if (int(conteudo_linha[num_hidros_jun]) <= 0):
                            arquivo_entrada.close(); mensagensIntegridadeJUN(3, linhas_lidas, (nop+1), num_hidros_jun, nop_declaradas); return False, None
                            
                        #   Checar se o numero do hidrograma de entrada e' possivel de ser encontrado no arquivo de entrada
                        if int(conteudo_linha[num_hidros_jun]) > nop_declaradas:
                            arquivo_entrada.close(); mensagensIntegridadeJUN(4, linhas_lidas, (nop+1), num_hidros_jun, nop_declaradas); return False, None
                    
                        #   Adiciono o numero 'a variavel auxiliar
                        operacoes_juncao.append(int(conteudo_linha[num_hidros_jun]))
                    
                    #   Dizer ao software que essa operacao precisa da saida de outra
                    entrada_operacoes[nop] = operacoes_juncao
                    
                
                #   Testar se e' HIDROGRAMA lido 
                elif conteudo_linha[0] == "HIDROGRAMA":
                    #   Testar tamanho da linha
                    if not len(conteudo_linha) == 3:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeHIDRO(1, linhas_lidas, (nop+1), nop_declaradas, str(conteudo_linha[1])); return False, None
                
                    #   Substituir a \ por /
                    conteudo_linha[1] = conteudo_linha[1].replace("\\","/")
                
                    #   Tirar os espacos em branco do diretorio informado, se houver
                    while conteudo_linha[1][0] == " ":
                        conteudo_linha[1] = conteudo_linha[1][1:]
                    
                    #   hidrograma de entrada
                    #   Verificar se o arquivo existe
                    if (path.isfile(conteudo_linha[1]) == True):
                        #   Selecionar ultimo nome
                        extensao_arquivo = conteudo_linha[1].split("/")
                        #   Selecionar extensao
                        extensao_arquivo = extensao_arquivo[-1].split(".")[-1]
                        
                        #   Verificar se a extensao dele e' txt
                        if ((extensao_arquivo == "txt") or (extensao_arquivo == "TXT")):
                            #   Testar o arquivo de entrada
                            integridade_arquivo, linha = checarIntegridadeArquivoTexto(conteudo_linha[1], numero_intervalos_tempo)
                            
                            #   Dizer ao programa que essa operacao nao precisa da saida de outra
                            entrada_operacoes[nop] = 0
                            
                            #   Se nao deu bom 
                            if integridade_arquivo == False:
                                #   Que ruim que deu?
                                if linha == 0: #    Numero de dados incorretos
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(3, linha, nch, (nop+1), 0, numero_intervalos_tempo); return False, None
                                
                                else: # Linha X e' o problema
                                    arquivo_entrada.close();  mensagensIntegridadeArquivosObservados(4, linha, nch, (nop+1), 0, numero_intervalos_tempo); return False, None
                        #   Nao e' txt
                        else: 
                            #   Avise o usuario
                            arquivo_entrada.close(); mensagensIntegridadeHIDRO(2, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    
                    #   Da pra entrar so' com o nome do arquivo se o mesmo estiver na mesma pasta do arquivo de entrada
                    elif (path.isfile(diretorio_pasta_entrada + "/".encode() + conteudo_linha[1].encode()) == True):
                        #   Selecionar extensao
                        extensao_arquivo = conteudo_linha[1].split(".")[-1]
                        
                        #   Verificar se a extensao dele e' txt
                        if ((extensao_arquivo == "txt") or (extensao_arquivo == "TXT")):
                            #   Testar o arquivo de entrada
                            integridade_arquivo, linha = checarIntegridadeArquivoTexto((diretorio_pasta_entrada + "/".encode() + conteudo_linha[1].encode()), numero_intervalos_tempo)
                            
                            #   Dizer ao programa que essa operacao nao precisa da saida de outra
                            entrada_operacoes[nop] = 0
                            
                            #   Se nao deu bom
                            if integridade_arquivo == False:
                                #   Que ruim que deu?
                                if linha == 0: #    Numero de dados incorretos
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(3, linha, nch, (nop+1), 0, numero_intervalos_tempo); return False, None
                                
                                else: # Linha X e' o problema
                                    arquivo_entrada.close(); mensagensIntegridadeArquivosObservados(4, linha, nch, (nop+1), 0, numero_intervalos_tempo); return False, None
                        #   Nao e' txt
                        else:
                            #   Avise o usuario
                            arquivo_entrada.close(); mensagensIntegridadeHIDRO(2, linhas_lidas, nop, 0, nop_declaradas); return False, None
                    
                    #   Nao e' path, Neste caso, ocorre erro.
                    else: 
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeHIDRO(3, linhas_lidas, nop, 0, nop_declaradas); return False, None
                
                
                #   Testar se e' DERIVACAO
                elif conteudo_linha[0] == "DERIVACAO": 
                    #   Testar tamanho da linha
                    if not len(conteudo_linha) == 6:
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(1, linhas_lidas, (nop+1), 0, nop_declaradas, ""); return False, None
                    
                    #   Testar hidrograma de entrada
                    try: int(conteudo_linha[1]) 
                    except: arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(2, linhas_lidas, (nop+1), 0, nop_declaradas, ""); return False, None
                    
                    #   Testar seu valor
                    if (int(conteudo_linha[1]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(3, linhas_lidas, (nop+1), 0, nop_declaradas, ""); return False, None
                        
                    #   Checar se o numero do hidrograma de entrada e' possivel de ser encontrado no arquivo de entrada
                    if int(conteudo_linha[1]) > nop_declaradas:
                        arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(4, linhas_lidas, (nop+1), int(conteudo_linha[1]), nop_declaradas, ""); return False, None
                    
                    #   Dizer ao software que essa operacao precisa da saida de outra
                    entrada_operacoes[nop] = int(conteudo_linha[1])
                    
                    #   Tirar os espacos em branco, se houver
                    while conteudo_linha[2][0] == " ":
                        conteudo_linha[2] = conteudo_linha[2][1:]
                    
                    #   Testar adiante
                    if ((not conteudo_linha[2] == "CONSTANTE") and (not conteudo_linha[2] == "PORCENTAGEM") and (not conteudo_linha[2] == "HIDROGRAMA")):
                        #   Avise o usuario
                        arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(5, linhas_lidas, (nop+1), 0, nop_declaradas, str(conteudo_linha[2])); return False, None
                        
                    #   Testar adiante: valor
                    try: float(conteudo_linha[3])
                    except: arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(6, linhas_lidas, (nop+1), 0, nop_declaradas, ""); return False, None
                    
                    #   Testar o valor
                    if (float(conteudo_linha[3]) <= 0):
                        arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(7, linhas_lidas, (nop+1), 0, nop_declaradas, ""); return False, None
                        
                    #   Tirar os espacos em branco, se houver
                    while conteudo_linha[4][0] == " ":
                        conteudo_linha[4] = conteudo_linha[4][1:]
                        
                    #   Testar adiante
                    if ((not conteudo_linha[4] == "PRINCIPAL") and (not conteudo_linha[4] == "DERIVADO")):
                        arquivo_entrada.close(); mensagensIntegridadeDERIVACAO(8, linhas_lidas, (nop+1), 0, nop_declaradas, conteudo_linha[4]); return False, None
                
                
                #   Tipo de operacao incorreto
                else: 
                    #   Avise o usuario
                    arquivo_entrada.close(); mensagensIntegridadeArquivos(3, linhas_lidas, nch, (nop+1), nch_declaradas, nop_declaradas, str(conteudo_linha[0])); return False, None
            
            #   Numero operacao incorreto
            else: 
                #   Avise o usuario
                arquivo_entrada.close(); mensagensIntegridadeArquivos(4, linhas_lidas, nch, (nop+1), nch_declaradas, nop_declaradas, ""); return False, None
            
            #   Se o code chegou ate' aqui, e' porque ele leu uma operacao belezinha, entao some uma op
            nop += 1
        
        #   Deu erro ai, ta escrito bobagem
        else: 
            if linhas_lidas < (numero_linhas+1):
                #   Que erro que e'? Linhas em branco no final do arquivo?
                if conteudo_linha[0] == "\n":
                    #   Avise o usuario
                    arquivo_entrada.close(); mensagensIntegridadeArquivos(5, linhas_lidas, nch, nop, nch_declaradas, nop_declaradas, ""); return False, None
                #   Escrito bobagem
                else:
                    #   Avise o usuario
                    arquivo_entrada.close(); mensagensIntegridadeArquivos(6, linhas_lidas, nch, nop, nch_declaradas, nop_declaradas, str(conteudo_linha[0])); return False, None

    #   Fechar arquivo de entrada
    arquivo_entrada.close()
    
    #   Checar conteudo a mais
    #   Checar se o numero de chuvas lido corresponde ao numero de chuvas declarado
    if not nch == nch_declaradas:
        mensagensIntegridadeArquivos(7, linhas_lidas, nch, nop, nch_declaradas, nop_declaradas, ""); return False, None
        
    #   Checar se o numero de operacoes lidas corresponde ao numero de operacoes declaradas
    if not nop == nop_declaradas:
        mensagensIntegridadeArquivos(8, linhas_lidas, nch, nop, nch_declaradas, nop_declaradas, ""); return False, None
        
    #   Checar conteudo a menos
    if not linhas_lidas == numero_linhas:
        mensagensIntegridadeArquivos(12, linhas_lidas, nch, nop, nch_declaradas, nop_declaradas, ""); return False, None
    
    #   Se chegou ate' aqui, o arquivo e' feitoria
    return True, entrada_operacoes
#----------------------------------------------------------------------
def checarUnicidade(entrada_operacoes):
    #   Checar se uma operacao nao da saida para mais de uma operacao. (exemplo: operacao 4 e 5 terem (ambas) a operacao 3 como entrada)
    #   Usa-se a mesma variavel (lista_repeticao) para verificar isso. A ideia e' se for adicionar 2 numeros iguais: erro.
    #   Checar tambem, se uma operacao nao e' o hidrograma de saida como sua entrada: so' para PULS, MKC e JUN - a operacao PQ e HIDROGRAMA nao usam hidrograma de outra operacao como entrada
    #   Nao preciso de variavel pra isso, basta eu comparar o numero da operacao com o numero da operacao de entrada. Nao podem ser o mesmo
    lista_repeticao = []
    #   Verificar todas as operacoes...
    for ii in range(len(entrada_operacoes)):
        #   SE NAO for JUN (JUN tera' mais de um valor)
        if type(entrada_operacoes[ii]) == int:
            #   Adicionar na lista somente se a operacao nao for "standalone"
            if not entrada_operacoes[ii] == 0: #    Acho que essa linha devera' ser modificada no futuro pra incluir os casos em que ha' leitura de hidrogramas (ii == 4)
                #   Verificar se a operacao ja' nao esta' adicionada
                if not entrada_operacoes[ii] in lista_repeticao:
                    #   Adicionar na lista
                    lista_repeticao.append(entrada_operacoes[ii])
                #   Se ja esta' adicionada, temos um erro
                else:
                    mensagensIntegridadeArquivos(9, 0, 0, entrada_operacoes[ii], 0, 0, ""); return False

                #   Testar se a operacao em questao e' entrada de si mesma
                if entrada_operacoes[ii] == (ii+1):
                    #   Avisar
                    mensagensIntegridadeArquivos(10, 0, 0, (ii+1), 0, 0, ""); return False
                    
        #   Se FOR JUN:
        else:
            #   Deve-se fazer em um for pq JUN tera' mais de um unico valor (e' uma lista de valores, DEVO avaliar um a um)
            for numero_operacoes in entrada_operacoes[ii]:
                #   Adicionar na lista somente se a operacao nao for "standalone"
                if not numero_operacoes == 0:
                    #   Verificar se a operacao ja' nao esta' adicionada
                    if not numero_operacoes in lista_repeticao:
                        #   Adicionar na lista
                        lista_repeticao.append(numero_operacoes)
                    #   Se ja esta' adicionada, temos um erro
                    else:
                        mensagensIntegridadeArquivos(9, 0, 0, numero_operacoes, 0, 0, ""); return False

                    #   Testar se a operacao em questao e' entrada de si mesma
                    if numero_operacoes == (ii+1):
                        #   Avisar
                        mensagensIntegridadeArquivos(10, 0, 0, (ii+1), 0, 0, ""); return False
    
    #   Se chegou aqui.... sucesso
    return True
#----------------------------------------------------------------------
def checarLogicaCircular(entrada_operacoes):
    #   A partir daqui e' sabido que nao ha' operacoes sendo entrada de mais de uma operacao e nem que...
    #   ... nenhuma operacao usa sua propria saida como entrada. Falta analisar logica circular.
            
    #   Checar se nao ha logica circular nas operacoes (4->5, 5->6 e 6->4) : Verificar a ordem das operacoes
    #   A ideia e' sempre ir "voltando" as operacoes ate' chegar em operacoes com entrada_operacoes == 0
    #   O problema e' que como JUN possui mais de uma operacao de entrada, gera um problema pois deve-se avaliar uma a uma
    indices_aprovados = []
    #   Verificar todas as operacoes...
    for ii in range(len(entrada_operacoes)):
        #   Aqui armazenam-se as operacoes para servir de inicio de busca no while
        fila_indices = []
        
        #   Verificar se o indice a ser avaliado ja' nao e' aprovado: Adicione 'a fila somente se NAO for
        if not ii in indices_aprovados: 
            #   Adicionar indice 'a fila
            fila_indices.append(ii)
            
        #   Loop da fila: cada operacao da fila tem um caminho, enquanto houver operacao na fila, rode esse while
        #   E' um while pois o tamanho da fila pode aumentar no meio do caminho
        while len(fila_indices) > 0:
                
            #   Primeira coisa e' verificar se a operacao avaliada e' de juncao
            if type(entrada_operacoes[fila_indices[-1]]) == int:
                #   Testar se essa operacao e' "standalone", ou se o proximo indice ja' esta' aprovado: otimizacao
                if ((entrada_operacoes[fila_indices[-1]] == 0) or ((entrada_operacoes[fila_indices[-1]]-1) in indices_aprovados)):
                    #   Adiciono o indice avaliado (nesse caso e' o fim do caminho) como aprovada
                    if not fila_indices[-1] in indices_aprovados:
                        indices_aprovados.append(fila_indices[-1])
                    #   Removo o ultimo indice da fila: resolvo de tras pra frente, como a pilha do magic the gathering
                    del fila_indices[-1]
                #   A proxima operacao NAO esta' no caminho, adicione-a ao caminho e avalie-a
                elif not((entrada_operacoes[fila_indices[-1]]-1) in fila_indices):
                    #   Tudo certo, adicione ao caminho: Nao sei se cairei em logica circular, entao nao adicionarei o caminho 'a variavel das aprovacoes por hora
                    fila_indices.append(entrada_operacoes[fila_indices[-1]] - 1) # -1 para transformar em indice
                #   A operacao ja' esta' no caminho: verifica logica circular
                else:
                    #   Mostrar ao usuario
                    mensagensIntegridadeArquivos(11, 0, 0, 0, 0, 0, str(fila_indices[0]+1)); return False, None
                    
            #   Se for uma JUN
            else:
                #   Trigger pra saber se fora adicionado novos indices 'a fila
                adicionou_indice = False
                ultimo_indice = fila_indices[-1] # Armazena o valor do ultimo indice antes de -possivelmente- adicionar mais operacoes 'a fila
                #   Adicionar as operacoes desta juncao 'a fila
                for op_juncao in entrada_operacoes[ultimo_indice]:
                    #   Adicionar somente se nao esta' no rol de operacoes aprovadas: -1 para transformar de operacao para indice
                    if not (op_juncao - 1) in indices_aprovados:
                        #   Adicionar INDICE (por isso -1) 'a fila
                        fila_indices.append(op_juncao - 1)
                        adicionou_indice = True
                #   Tirar a juncao da fila: Deleto o indice na variavel fila que esta' armazenado o indice da operacao de JUN a ser removida
                #   Porem so' faco isso se nenhuma operacao foi adicionada 'a fila: ou seja, a juncao esta' finalizada
                if adicionou_indice == False:
                    indices_aprovados.append(fila_indices[fila_indices.index(ultimo_indice)])
                    del fila_indices[fila_indices.index(ultimo_indice)]
        
    #   Se chegou aqui... sucesso
    return True, indices_aprovados
#----------------------------------------------------------------------
def checarIntegridadeArquivoTexto(diretorio_arquivo, numero_linhas_deve_ter):
    """
    Checa o conteudo de arquivos de texto que sao dados de entrada, com excessao do arquivo de chuva-observada.
    Retorna: True/False (se e' integro), numero (da linha com o erro - 0 significa sem erro)
    """
    #   Contar numero de linhas
    numero_linhas = contarLinhas(diretorio_arquivo)
    
    #   Verificar se ele possui o mesmo numero de termos que o numero de intervalos de tempo de chuva
    if (not numero_linhas == numero_linhas_deve_ter):
        return False, 0
        
    #   Verificar se todos os valores sao de fato valores.... 
    arquivo_leitura_dados = open(diretorio_arquivo,'r')
    
    #   Verificar o arquivo de chuva dado: esta verificacao sera' movida para uma funcao de integridade no inicio do processamento
    for linha_arquivo in range(numero_linhas):
        #   Ler a linha e substituir virgulas por ponto
        conteudo_linha = arquivo_leitura_dados.readline().split(";")
        conteudo_linha = conteudo_linha[0].replace(",",".")
        
        #   Tentar transformar o conteudo da linha em numero flutante
        try: float(conteudo_linha)
        except: arquivo_leitura_dados.close(); return False, (linha_arquivo+1)
    
    #   Se chegou ate' aqui, e' porque esta' tudo certo
    arquivo_leitura_dados.close()
    #   Se chegou ate' aqui, retorne verdadeiro
    return True, 0
#----------------------------------------------------------------------
def checarIntegridadeArquivoCotaVolume(diretorio_arquivo):
    """
    Checa o conteudo de arquivos de texto que sao dados de entrada, com excessao do arquivo de chuva-observada.
    Retorna: True/False (se e' integro), numero (da linha com o erro - 0 significa sem erro)
    """
    #   Contar numero de linhas
    numero_linhas = contarLinhas(diretorio_arquivo)
    
    #   Verificar se ele possui o mesmo numero de termos que o numero de intervalos de tempo de chuva
    if numero_linhas < 2:
        return False, 0
        
    #   Verificar se todos os valores sao de fato valores.... 
    arquivo_leitura_dados = open(diretorio_arquivo,'r')
    
    #   Verificar o arquivo de chuva dado: esta verificacao sera' movida para uma funcao de integridade no inicio do processamento
    for linha_arquivo in range(numero_linhas):
        #   Ler a linha e substituir virgulas por ponto
        conteudo_linha = arquivo_leitura_dados.readline().split(";")
        
        #   Se nao houver 3 items, erro: "cota; volume;\n"
        if len(conteudo_linha) == 3:
            #   Pego o conteudo das strings
            cota   = conteudo_linha[0].replace(",",".")
            volume = conteudo_linha[1].replace(",",".")
            
            #   Tentar transformar o conteudo da cota em numero flutante
            try: float(cota)
            except: arquivo_leitura_dados.close(); return False, (linha_arquivo+1)
            
            #   Tentar transformar o conteudo do volume em numero flutante
            try: float(volume)
            except: arquivo_leitura_dados.close(); return False, (linha_arquivo+1)
            
            #   O primeiro valor DEVE ser zero
            if linha_arquivo == 0:
                if (not float(cota) == 0.0) or (not float(volume) == 0.0):
                    arquivo_leitura_dados.close(); return False, 0
        
        #   Nao term 3 valores, tem menos ou mais
        else:
            arquivo_leitura_dados.close(); return False, (linha_arquivo+1)
            
    #   Se chegou ate' aqui, e' porque esta' tudo certo
    arquivo_leitura_dados.close()
    #   Se chegou ate' aqui, retorne verdadeiro
    return True, 0
#----------------------------------------------------------------------
def lerSerieObservada(diretorio_arquivo, numero_linhas_arquivo):
    """Le os valores dos arquivos TXT e joga numa lista para ser retornada"""
    #   Declarar
    serie_observada = array([0.0 for ii in range(numero_linhas_arquivo)], float64)
    
    #   Verificar se todos os valores sao de fato valores.... 
    arquivo_leitura_dados = open(diretorio_arquivo,'r')
    
    for linha in range(numero_linhas_arquivo):
        #   Ler a linha e substituir virgulas por ponto
        conteudo_linha = arquivo_leitura_dados.readline().split(";")
        conteudo_linha = conteudo_linha[0].replace(",",".")
        
        serie_observada[linha] = float(conteudo_linha)
    #   Gibe gibe!
    return serie_observada
#----------------------------------------------------------------------
def lerArquivoEntrada(diretorio_arquivo_entrada):
    """Le o arquivo de entrada e armazena as informacoes"""
    #   Diretorio do arquivo de entrada
    diretorio_pasta_entrada = path.dirname(diretorio_arquivo_entrada)
    print ("\n\tLendo dados de entrada.")
    #   Abrir o arquivo de entrada
    arquivo_entrada = open(diretorio_arquivo_entrada, mode='r', buffering=-1, encoding='utf-8')
    #   A primeira linha le-se manualmente
    conteudo_linha = arquivo_entrada.readline().split(";") # so' leio, mas nao faco nada com isso....
    
    #   Ler linhas ate' que a primeira coisa que o modelo le e' "INICIO" - isto possibilita criar um cabecalho com quantas linhas o usuario desejar
    while not conteudo_linha[0] == "INICIO":
        #   Leia outra linha....
        conteudo_linha = arquivo_entrada.readline().split(";")
    
    #   Assim que o modelo le "INICIO" no inicio da linha, comeca a armazenar o conteudo.
    if conteudo_linha[0] == "INICIO":
        #   Parametros gerais da simulacao - valem para todas as operacoes e chuvas a serem calculadas
        numero_intervalos_tempo       = int(conteudo_linha[1]) # (nInt)
        duracao_intervalo_tempo       = int(conteudo_linha[2]) # (DT)
        numero_chuvas                 = int(conteudo_linha[3]) # (nCh)
        numero_intervalos_tempo_chuva = int(conteudo_linha[4]) # (nIntCh)
        numero_operacoes              = int(conteudo_linha[5]) # (nop)
        
        #   Variaveis da logica do programa - controlam os processos e a maneira como o programa vai resolver as operacoes hidrologicas
        entradas_operacoes = [None for ii in range(numero_operacoes)] # (entrOp) 0: nao precisa de outra operacao; >0: representa o numero da op de entrada dessa operacao
        codigos_operacoes  = [None for ii in range(numero_operacoes)] # (cdgOH) # 1->CHUVA-VAZAO; 2->PULS; 3->MKC; 4->JUNCAO;
        nomes_operacoes    = ["".encode('utf-8') for ii in range(numero_operacoes)] # (nomesOp) # Recebe o nome das operacoes hidrologicas -> plotagem dos graficos
        
        #   Variaveis das chuvas IDFs
        parametro_a   = [None for ii in range(numero_chuvas)] # (idfA)
        parametro_b   = [None for ii in range(numero_chuvas)] # (idfB)
        parametro_c   = [None for ii in range(numero_chuvas)] # (idfC)
        parametro_d   = [None for ii in range(numero_chuvas)] # (idfD)
        tipo_idf      = [None for ii in range(numero_chuvas)] # (tpIDF)
        posicao_pico  = [None for ii in range(numero_chuvas)] # (posPico)
        tempo_retorno = [None for ii in range(numero_chuvas)] # (TR)
        limites_idf   = [None for ii in range(numero_chuvas)] # (limIDF)

        #   Variaveis para chuvas OBS
        diretorios_chuvas_observadas = [None for ii in range(numero_chuvas)] # (dirCh)
        
        #   Variaveis das operacoes hidrologicas
                
        #   Chuva-Vazao
        coeficiente_cn    = [None for ii in range(numero_operacoes)] # (CN)
        area_km2          = [None for ii in range(numero_operacoes)] # (area)
        tc_horas          = [None for ii in range(numero_operacoes)] # (TC)
        chuvas_entrada_pq = [None for ii in range(numero_operacoes)] # (nChuPQ)
        
        #   Chuva-vazao e Muskingum-Cunge
        diferenca_cota_m     = [None for ii in range(numero_operacoes)] # (difCota)
        comprimento_canal_km = [None for ii in range(numero_operacoes)] # (compCanal)
        
        #   PULS
        curvas_cota_volume    = [[None, None] for ii in range(numero_operacoes)] # (CCV)
        estruturas_puls       = [None for ii in range(numero_operacoes)] # (estruPULS)
        cotas_iniciais_puls_m = [None for ii in range(numero_operacoes)] # (cotaInPULS)
        vazoes_by_pass_m3s    = [None for ii in range(numero_operacoes)] # (byPasses)
        
        #   MUSKINGUM-CUNGE
        largura_canal_m        = [None for ii in range(numero_operacoes)] # (largCanal)
        coeficiente_rugosidade = [None for ii in range(numero_operacoes)] # (nMann)
        
        #   JUNCAO - Nao tem nenhuma
        
        #   HIDROGRAMA
        diretorios_hidrogramas_observados = [None for ii in range(numero_operacoes)] # (dirHidro)
        
        #   DERIVACAO
        tipo_derivacao  = [None for ii in range(numero_operacoes)] # tpDeriv
        valor_derivacao = [None for ii in range(numero_operacoes)] # vlDeriv
        saida_derivacao = [None for ii in range(numero_operacoes)] # sdDeriv
    
    
    #   Determinar quantos blocos de linhas serao lidos
    numero_blocos = (numero_chuvas + numero_operacoes) #saber quantos blocos de linhas deverei ler... cada bloco pode ser uma chuva ou uma operacao
    
    #   Atualizar barra de progresso
    atualizarBarraProgresso(0, numero_blocos)
    
    #   Loop da leitura de dados
    for ii in range(numero_blocos): #botar barra de progresso para leitura do arquivo de entrada
        #   Ler e quebrar a linha em blocos
        conteudo_linha = arquivo_entrada.readline().split(";") #lera' "CHUVA" ou "OPERACAO" e a chuva que corresponde
        
        #   Tirar os espacos em branco do diretorio informado, se houver
        while conteudo_linha[0][0] == " ":
            conteudo_linha[0] = conteudo_linha[0][1:]

        #*--------------------------------- Ler CHUVA ---------------------------------*#
        
        #   Ler CHUVA
        if conteudo_linha[0] == "CHUVA": #e' pra colocar chuva observada ou idf
            #   Armazenar o numero da chuva. Reduz-se 1 pois Python comeca a contar em zero
            numero_chuva_correspondente = (int(conteudo_linha[1]) - 1)
            #   Ler e quebrar a proxima linha em blocos
            conteudo_linha = arquivo_entrada.readline().split(";") #ler IDF e parametros ou OBS
            
            #   Tirar os espacos em branco do diretorio informado, se houver
            while conteudo_linha[0][0] == " ":
                conteudo_linha[0] = conteudo_linha[0][1:]
            
            #   Caso for chuva IDF
            if conteudo_linha[0] == "IDF":
                #   Armazenar as variaveis
                tipo_idf[numero_chuva_correspondente]      = (int(conteudo_linha[1]))
                posicao_pico[numero_chuva_correspondente]  = (float(conteudo_linha[2]))
                tempo_retorno[numero_chuva_correspondente] = (int(conteudo_linha[3]))
                parametro_a[numero_chuva_correspondente]   = float(conteudo_linha[4])
                parametro_b[numero_chuva_correspondente]   = float(conteudo_linha[5])
                parametro_c[numero_chuva_correspondente]   = float(conteudo_linha[6])
                parametro_d[numero_chuva_correspondente]   = float(conteudo_linha[7])
                limites_idf[numero_chuva_correspondente]   = int(conteudo_linha[8])
            
            #   Caso for chuva OBSERVADA
            elif conteudo_linha[0] == "OBS": 
                #   Substituir a \ por /
                conteudo_linha[1] = conteudo_linha[1].replace("\\","/")
                
                #   Tirar os espacos em branco do diretorio informado, se houver
                while conteudo_linha[1][0] == " ":
                    conteudo_linha[1] = conteudo_linha[1][1:]
                
                #   Verificar se o conteudo[1] e' o diretorio ou o nome do arquivo presente na mesma pasta
                if (path.isfile(conteudo_linha[1].encode()) == True):
                    #   Armazenar o diretorio do arquivo com a informacao da 
                    diretorios_chuvas_observadas[numero_chuva_correspondente] = conteudo_linha[1].encode()  #diretorio armazenado, abra ele agora.
                
                #   E' so' um nome, portanto, deve-se combinar o diretorio da pasta ao nome do arquivo
                else:
                    #   Armazenar o diretorio do arquivo com a informacao da 
                    diretorios_chuvas_observadas[numero_chuva_correspondente] = (diretorio_pasta_entrada + "/".encode() + conteudo_linha[1].encode())  #diretorio armazenado, abra ele agora.
        
        #*--------------------------------- Ler OPERACAO ---------------------------------*#
        
        #   Ler OPERACAO
        elif conteudo_linha[0] == "OPERACAO": #e' uma operacao hidrologica
            #   Armazenar o numero da operacao
            numero_operacao = (int(conteudo_linha[1]) -1) #guarda a ordem que as operacoes sao entradas no programa.... e' o valor seguido de "OPERACAO;"
            
            #   CASO o usuario informar o nome/local da operacao, armazene-o
            if len(conteudo_linha) > 3: # > 3 pois o terceiro elemento da linha quando o usuario nao insere nome algum e' "\n" e isso estava ocasionando problemas.
                #   Armazenar o local/nome da operacao
                nomes_operacoes[numero_operacao] = conteudo_linha[2].encode('utf-8') #o nome e' o terceiro termo da linha
                
            #   Ler a proxima linha para saber qual operacao que o usuario esta' entrando
            conteudo_linha = arquivo_entrada.readline().split(";") #ler qual operacao (PQ, PULS....) e qual e' a chuva que ela utiliza
                
            #   Tirar os espacos em branco do diretorio informado, se houver
            while conteudo_linha[0][0] == " ":
                conteudo_linha[0] = conteudo_linha[0][1:]
                
            #*--------------------------------- Ler PQ ---------------------------------*#
            #   Caso for operacao de CHUVA-VAZAO
            if conteudo_linha[0] == "PQ":
                #   Colocar o codigo 1 (PQ) na variavel de controle de operacoes
                codigos_operacoes[numero_operacao] = 1
                #   Digo que essa operacao nao precisa de outra operacao para funcionar
                entradas_operacoes[numero_operacao] = 0
                #   Determinar o numero da chuva que sera' utilizada na operacao
                operacao_usa_chuva = (int(conteudo_linha[1]) -1) #guarda o numero que nos diz qual chuva sera' usada nesta operacao
                #   Armazenar o numero da chuva que entra nesta operacao
                chuvas_entrada_pq[numero_operacao] = operacao_usa_chuva
                #   Ler e quebrar a proxima linha
                conteudo_linha = arquivo_entrada.readline().split(";") #le qual sera o algoritmo de separacao de escoamento utilizado (1:CN-SCS, se CN do LADO o valor do CN)
                
                #   Armazene o valor de CN
                coeficiente_cn[numero_operacao] = float(conteudo_linha[1])
                
                #   Continue lendo esta operacao chuva-vazao
                conteudo_linha = arquivo_entrada.readline().split(";") #le qual sera' o algoritmo de propagacao do escoamento superficial e valores de tc
                
                #   Armazene a area da bacia em km2
                area_km2[numero_operacao] = float(conteudo_linha[1])
                
                #   Tirar os espacos em branco do diretorio informado, se houver
                while conteudo_linha[2][0] == " ":
                    conteudo_linha[2] = conteudo_linha[2][1:]
                
                #   Caso o segundo termo da linha for "KIRPICH", o usuario quer calcular o tempo de concentracao da bacia pela equacao de Kirpich
                if conteudo_linha[2] == "KIRPICH":
                    #   Armazenar os valores requeridos pela equacao de Kirpich
                    diferenca_cota_m[numero_operacao]     = float(conteudo_linha[3])
                    comprimento_canal_km[numero_operacao] = float(conteudo_linha[4])
                    
                    tc_horas[numero_operacao] = calcular_TC_Kirpich(diferenca_cota_m[numero_operacao], comprimento_canal_km[numero_operacao])
                
                #   Caso o segundo termo nao for "KIRPICH", apenas armazene o valor do TC (em HORAS)
                else:
                    #   Armazenar o tempo de concentracao (horas)
                    tc_horas[numero_operacao] = float(conteudo_linha[2])
                        
            #*--------------------------------- Ler PULS ---------------------------------*#
            #   Caso for operacao de PULS
            elif conteudo_linha[0] == "PULS":
                #   Colocar o codigo 2 (PULS) na variavel de controle de operacoes
                codigos_operacoes[numero_operacao] = 2
                #   Digo que essa operacao precisa de outra operacao para funcionar
                entradas_operacoes[numero_operacao] = int(conteudo_linha[1])
                #   Armazenar as cotas iniciais
                cotas_iniciais_puls_m[numero_operacao] = float(conteudo_linha[2]) # em metros
                #   Armazeno as vazoes do by-pass
                vazoes_by_pass_m3s[numero_operacao] = float(conteudo_linha[3]) # em m3/s
                #   Esta variavel e' auxiliar, e' resetada cada operacao. Ela guarda a informacao de cada estrutura em [...], e de cada operacao em [[,,,],[,,,]]
                estruturas_desta_operacao = [["",0,0,0,0] for jj in range(int(conteudo_linha[4]))] # variavel que deve ser resetada a cada nova operacao puls
                
                #   Loop para ler as estruturas de determinada operacao
                for estrutura in range(int(conteudo_linha[4])):
                    #   Ler a estrutura
                    conteudo_linha = arquivo_entrada.readline().split(";")          #ler cada estrutura
                    #   Tirar os espacos em branco do diretorio informado, se houver
                    while conteudo_linha[0][0] == " ":
                        conteudo_linha[0] = conteudo_linha[0][1:]
                    #   Armazenar a informacao
                    estruturas_desta_operacao[estrutura][0] = (conteudo_linha[0])        #Armazenar "VERTEDOR" ou "ORIFICIO"
                    #   Caso VERTEDOR
                    if conteudo_linha[0] == "VERTEDOR":
                        estruturas_desta_operacao[estrutura][1] = (float(conteudo_linha[1])) #Armazenar coeficiente da estrutura
                        estruturas_desta_operacao[estrutura][2] = (float(conteudo_linha[2])) #Armazenar informacoes da estrutura
                        estruturas_desta_operacao[estrutura][3] = (float(conteudo_linha[3])) #Armazenar informacoes da estrutura
                        estruturas_desta_operacao[estrutura][4] = (float(conteudo_linha[4])) #Armazenar informacoes da estrutura
                    #   Caso ORIFICIO
                    elif conteudo_linha[0] == "ORIFICIO":
                        estruturas_desta_operacao[estrutura][1] = (float(conteudo_linha[1])) #Armazenar coeficiente da estrutura
                        estruturas_desta_operacao[estrutura][2] = (float(conteudo_linha[2])) #Armazenar informacoes da estrutura
                        estruturas_desta_operacao[estrutura][3] = (float(conteudo_linha[3])) #Armazenar informacoes da estrutura
                        #estruturas_desta_operacao[estrutura][4] = NESSE CASO (orificios circulares) será sempre ZERO

                #   Armazenar toda a informacao das estruturas em uma sublista de estruturas_puls
                estruturas_puls[numero_operacao] = (estruturas_desta_operacao) #ORGANIZADA DE MANEIRA QUE CADA TERMO E' UMA OPERACAO, E CADA LISTA DENTRO DE CADA TERMO E' UMA ESTRUTURA
                # Exemplo: 3 operacoes: A primeira com 3 estruturas. A segunda com 1 estrutura. A terceira com 2 estruturas     #
                #estruturas_puls = [ [ [,,,],[,,,],[,,,] ], [ [,,,] ], [ [,,,],[,,,] ] ]  <--- Estrutura da variavel            #
                #                    (                   ), (       ), (             )   <--- Conteudo de cada OPERACAO         #
                #                      (,,,),(,,,),(,,,)      (,,,)      (,,,),(,,,)   <--- Conteudo de cada ESTRUTURA          #
                #################################################################################################################
                
                #   Continue a ler o arquivo de entrada: Curva cota-volume
                conteudo_linha = arquivo_entrada.readline().split(";") #ler o diretorio do arquivo de cota-vazao
                
                #   Substituir a \ por /
                conteudo_linha[0] = conteudo_linha[0].replace("\\","/")
            
                #   Tirar os espacos em branco do diretorio informado, se houver
                while conteudo_linha[0][0] == " ":
                    conteudo_linha[0] = conteudo_linha[0][1:]
                
                #   Verificar se o conteudo[0] e' o diretorio ou o nome do arquivo presente na mesma pasta
                if (path.isfile(conteudo_linha[0].encode()) == True):
                    #   Armazenar o diretorio do arquivo com a informacao da cota-volume
                    diretorio_curva_cotavolume = conteudo_linha[0].encode()  #diretorio armazenado, abra ele agora.
                
                #   E' so' um nome, portanto, deve-se combinar o diretorio da pasta ao nome do arquivo
                else:
                    #   Armazenar o diretorio do arquivo com a informacao da cota-volume
                    diretorio_curva_cotavolume = (diretorio_pasta_entrada + "/".encode() + conteudo_linha[0].encode())  #diretorio armazenado, abra ele agora.
                
                #   Contar quantas linhas tem o arquivo da curva cota-volume
                numero_linhas    = sum(1 for linha in open(diretorio_curva_cotavolume,'r'))      #contar o numero de linhas do arquivo da curva cota-volume
                #   Criar uma variavel temporaria que armazenara o conteudo da linha
                curva_provisoria = [[0.0 for i3 in range(numero_linhas)] for i4 in range(2)]     #cria uma lista com 2 termos, cada um deles com numero_linhas linhas.
                #   Abra o arquivo
                arquivo_curva    = open(diretorio_curva_cotavolume, 'r')                         #abrir o arquivo para le-lo.
                
                #   Loop para ler linhas do arquivo da curva cota-volume
                for linha in range(numero_linhas):
                    #   Ler e quebrar a linha
                    conteudo_curva = arquivo_curva.readline().split(";")    #ler a linha e dividir 
                    #   Armazenar o conteudo
                    curva_provisoria[0][linha] = float(conteudo_curva[0])   #valores de cota
                    curva_provisoria[1][linha] = float(conteudo_curva[1])   #valores de volume
                
                #   Fechar o arquivo da curva cota-volume
                arquivo_curva.close() #fechar o arquivo -> poupar memoria.
                #   Armazenar a curva na variavel que sera' retornada mais tarde
                curvas_cota_volume[numero_operacao] = (curva_provisoria) ##################################################################################################
                #curvas_cota_volume = [ [ [...],[...] ], [ [...],[...] ], [ [...],[...] ], ... ]                                                                          #
                #                       (             ), (             ), (             )  <--- Conteudo de cada curva cota-volume, cada puls com seu (    )              #
                #                         (...),(...)      (...),(...)      (...),(...)    <--- Conteudo das curvas, o primeiro (...) e' cota, o segundo (...) e' volume. #
                ###########################################################################################################################################################
                
            #*--------------------------------- Ler MKC ---------------------------------*#
            #   Caso for operacao de MKC
            elif conteudo_linha[0] == "MKC":  #OPERACAO DE MUSKINGUM-CUNGE!!
                #   Colocar o codigo 3 (MKC) na variavel de controle de operacoes
                codigos_operacoes[numero_operacao] = 3
                #   Digo que essa operacao precisa de outra operacao para funcionar
                entradas_operacoes[numero_operacao] = int(conteudo_linha[1])
                #   Armazenar as demais informacoes da operacao
                diferenca_cota_m[numero_operacao]       = float(conteudo_linha[2]) #armazenar a diferenta de cota do canal em metros.
                comprimento_canal_km[numero_operacao]   = float(conteudo_linha[3]) #armazenar o comprimento do canal em quilometros.
                largura_canal_m[numero_operacao]        = float(conteudo_linha[4]) #armazenar a largura canal em metros.
                coeficiente_rugosidade[numero_operacao] = float(conteudo_linha[5]) #armazenar o coeficiente de rugosidade de manning.
            
            #*--------------------------------- Ler JUNCAO ---------------------------------*#
            #   Caso for operacao de JUNCAO
            elif conteudo_linha[0] == "JUN":  #OPERACAO DE JUN
                #   Colocar o codigo 4 (JUN) na variavel de controle de operacoes
                codigos_operacoes[numero_operacao] = 4
                
                #   Adicionar os hidrogramas como listas 
                indices_hidrogramas_juncao = []
                for operacao_da_juncao in range(1, len(conteudo_linha)-1): # -1 pois: e' -2 (primeiro valor e' "JUN;" o ultimo sera' "\n" ou "") mas e' +1 pq e' indice.
                    #   Adicionar na lista provisoria
                    indices_hidrogramas_juncao.append(int(conteudo_linha[operacao_da_juncao]))
                
                #   Digo que essa operacao precisa de outra operacao para funcionar
                entradas_operacoes[numero_operacao] = indices_hidrogramas_juncao
            
            #*--------------------------------- Ler HIDROGRAMA ---------------------------------*#
            #   Caso for operacao de leitura de hidrogramas
            elif conteudo_linha[0] == "HIDROGRAMA": 
                #   Colocar o codigo 5 (HIDROGRAMA) na variavel de controle de operacoes
                codigos_operacoes[numero_operacao] = 5
                
                #   Substituir a \ por /
                conteudo_linha[1] = conteudo_linha[1].replace("\\","/")
                
                #   Tirar os espacos em branco do diretorio informado, se houver
                while conteudo_linha[1][0] == " ":
                    conteudo_linha[1] = conteudo_linha[1][1:]
                    
                #   Verificar se o conteudo[1] e' o diretorio ou o nome do arquivo presente na mesma pasta
                if (path.isfile(conteudo_linha[1].encode()) == True):
                    #   Armazenar o diretorio do arquivo de entrada
                    diretorios_hidrogramas_observados[numero_operacao] = conteudo_linha[1].encode('utf-8')
                
                #   E' so' um nome, portanto, deve-se combinar o diretorio da pasta ao nome do arquivo
                else:
                    #   Armazenar o diretorio do arquivo de entrada
                    diretorios_hidrogramas_observados[numero_operacao] = (diretorio_pasta_entrada + "/".encode() + conteudo_linha[1].encode())
                
                #   Digo que essa operacao nao precisa de outra operacao para funcionar
                entradas_operacoes[numero_operacao] = 0
            
            
            #*--------------------------------- Ler DERIVACAO ---------------------------------*#
            #   Caso for operacao de DERIVACAO
            elif conteudo_linha[0] == "DERIVACAO":
                #   Colocar o codigo 6 (DERIVACAO) na variavel de controle de operacoes
                codigos_operacoes[numero_operacao] = 6
                
                #   Ver o hidrograma de entrada
                entradas_operacoes[numero_operacao] = int(conteudo_linha[1])
                
                #   Tirar os espacos em branco do diretorio informado, se houver
                while conteudo_linha[2][0] == " ":
                    conteudo_linha[2] = conteudo_linha[2][1:]
                
                #   Ver o tipo de derivacao
                
                #   Se for CONSTANTE
                if conteudo_linha[2] == "CONSTANTE":
                    tipo_derivacao[numero_operacao] = 1
                #   Se for PORCENTAGEM    
                elif conteudo_linha[2] == "PORCENTAGEM":
                    tipo_derivacao[numero_operacao] = 2
                #   Se for HIDROGRAMA
                else:
                    tipo_derivacao[numero_operacao] = 3
                
                #   Ver o valor da derivacao
                valor_derivacao[numero_operacao] = float(conteudo_linha[3])
                
                #   Tirar os espacos em branco do diretorio informado, se houver
                while conteudo_linha[4][0] == " ":
                    conteudo_linha[4] = conteudo_linha[4][1:]
                
                #   Ver o tipo de saida
                
                #   Se for PRINCIPAL
                if conteudo_linha[4] == "PRINCIPAL":
                    saida_derivacao[numero_operacao] = 1
                #   Se for DERIVADO
                else:
                    saida_derivacao[numero_operacao] = 2
            
        #   Atualizar barra de progresso
        atualizarBarraProgresso(ii+1, numero_blocos)
        
    #   Fazer o retorno das variaveis
    return numero_intervalos_tempo, duracao_intervalo_tempo, numero_chuvas, numero_intervalos_tempo_chuva, numero_operacoes, entradas_operacoes, codigos_operacoes, nomes_operacoes, parametro_a, parametro_b, parametro_c, parametro_d, limites_idf, tipo_idf, posicao_pico, tempo_retorno, diretorios_chuvas_observadas, coeficiente_cn, area_km2, tc_horas, chuvas_entrada_pq, diferenca_cota_m, comprimento_canal_km, curvas_cota_volume, estruturas_puls, cotas_iniciais_puls_m, vazoes_by_pass_m3s, largura_canal_m, coeficiente_rugosidade, diretorios_hidrogramas_observados, tipo_derivacao, valor_derivacao, saida_derivacao
#----------------------------------------------------------------------
def determinarDiretoriosPlotagens(isFolder, diretorio_do_software):
    """Retornar [diretorios_arquivos_entrada] e [diretorio_saida], ambos com len >= 1 e encoded"""
    #   Testar se e' um arquivo ou uma pasta como entrada...
    if isFolder == False:
        #   Lendo arquivo de entrada ---> diretorio_saida == diretorio de entrada
        diretorios_arquivos_entrada = gerenciarLeituraPlotagens(diretorio_do_software)
        #   Corrigir erro
        if not diretorios_arquivos_entrada == [None]:
            #   Determinar o(s) diretorio(s) de saida
            diretorio_saida = [diretorios_arquivos_entrada[0].split(b".")[0]]
        #   Corrigir erro
        else: 
            diretorio_saida = [None]
            
    #   Trata-se de uma pasta...
    else:
        #   Ja retorna a lista
        diretorio_pasta_entrada, arquivos_da_pasta = gerenciarLeituraPastaPlotagens(diretorio_do_software)

        #   Corrigir erro
        if not diretorio_pasta_entrada == None:
            #   Criar a lista dos diretorios dos arquivos.
            diretorios_arquivos_entrada = [diretorio_pasta_entrada + "/".encode() + arquivos_da_pasta[ii] for ii in range(len(arquivos_da_pasta))]
            #   Determinar o(s) diretorio(s) de saida
            diretorio_saida = [diretorios_arquivos_entrada[ii].split(b".")[0] for ii in range(len(diretorios_arquivos_entrada))]
        #   Corrigir erro
        else: 
            diretorios_arquivos_entrada = [None]
            diretorio_saida = [None]
    
    #   "gimme gimme!"
    return diretorios_arquivos_entrada, diretorio_saida
#----------------------------------------------------------------------
def gerenciarLeituraPlotagens(diretorio_do_software):
    """"""
    #   Abra o arquivo... Se 'diretorio_arquivo_entrada' == None, o arquivo nao e' txt.
    diretorio_arquivo_entrada = procurarArquivo(diretorio_do_software)
    
    #   Se um diretorio foi detectado, e' um arquivo txt.
    if not diretorio_arquivo_entrada == None:
        #   Selecionar extensao
        extensao_arquivo = diretorio_arquivo_entrada.decode().split("/")[-1].split(".")[-1]
        
        #   Verificar se um arquivo ohy foi selecionado
        if (extensao_arquivo == "ohy") or (extensao_arquivo == "OHY"):
            #   Identificar o tipo de arquivo
            codigo_arquivo = identificarCodigoArquivoSaida(diretorio_arquivo_entrada)
            #   Continuo so' se for um arquivo identificado
            if codigo_arquivo > 0:
                #   integridade_entrada guarda os resultados dos testes de integridade
                integridade_entrada = False
                #   Faca o teste de integridade do arquivo, isto vou deixar para depois.
                integridade_entrada = checarIntegridadeArquivoSaida(diretorio_arquivo_entrada, codigo_arquivo)
                
                #   Se o arquivo for integro (nao possuir erros), continue
                if integridade_entrada == True:
                    #   Retorne o diretorio
                    return [diretorio_arquivo_entrada]
                #   Arquivo ruim
                else:
                    print ("\n\tArquivo de entrada com problemas. Cheque seu arquivo de entrada.\n")
                    return [None]
            #   Codigo arquivo nao identificado
            else:
                #   O Erro ja foi informado
                return [None]
        #   Formato incorreto
        else:
            print ("\n\tExtensao do arquivo de entrada e' incompativel.\n")
            mensagensIntegridadePlotagens(1, '')
            return [None]
    #   Se NAO for dado um arquivo de entrada
    else:
        print ("\n\tNenhum arquivo selecionado.\n")
        mensagensIntegridadePlotagens(2, '')
        return [None]
#----------------------------------------------------------------------
def gerenciarLeituraPastaPlotagens(diretorio_do_software):
    """"""
    #   Abra o arquivo... Se 'diretorio_arquivo_entrada' == None, o arquivo nao e' txt.
    diretorio_pasta_entrada = procurarPasta(diretorio_do_software)
    
    #   Se um diretorio foi detectado, e' um arquivo txt.
    if not diretorio_pasta_entrada == None:
        #   Listar os arquivos presentes nesta pasta... Nome.extensao
        arquivos_da_pasta = listdir(diretorio_pasta_entrada) 
        #   Variavel Auxiliar
        arquivos_deletados = 0
        
        #   Loop para tirar os arquivos de saida (ohy) dos diretorios de entrada
        for numero_arquivo in range(len(arquivos_da_pasta)):
            #   Selecionar extensao
            extensao_arquivo = arquivos_da_pasta[numero_arquivo - arquivos_deletados].decode().split(".")[-1]
            #   Testar extensao
            if (not extensao_arquivo == "ohy") and (not extensao_arquivo == "OHY"):
                #   Delete o arquivo da lista
                del arquivos_da_pasta[numero_arquivo - arquivos_deletados]
                #   Somar um...
                arquivos_deletados += 1
        
        #   Se nao sobrou nenhum arquivo na lista, e' porque nenhum deles e' valido
        if len(arquivos_da_pasta) == 0:
            print ("\n\tNenhum dos arquivos da pasta possui o formato valido.\n")
            mensagensIntegridadePlotagens(3, '')
            return None, None

        #   Loop principal... de arquivo em arquivo
        for indice_arquivo, nome_arquivo in enumerate(arquivos_da_pasta):
            #   Especificar arquivo
            diretorio_arquivo_entrada = (diretorio_pasta_entrada + "/".encode() + nome_arquivo)
            #   Selecionar extensao
            extensao_arquivo = nome_arquivo.decode().split(".")[-1]
            
            #   Verificar se um arquivo ohy foi selecionado
            if (extensao_arquivo == "ohy") or (extensao_arquivo == "OHY"):
                #   Identificar o tipo de arquivo
                codigo_arquivo = identificarCodigoArquivoSaida(diretorio_arquivo_entrada)
                #   Continuo so' se for um arquivo identificado
                if codigo_arquivo > 0:
                    #   integridade_entrada guarda os resultados dos testes de integridade
                    integridade_entrada = False
                    #   Faca o teste de integridade do arquivo, isto vou deixar para depois.
                    integridade_entrada = checarIntegridadeArquivoSaida(diretorio_arquivo_entrada, codigo_arquivo)
                    
                    #   Se o arquivo for integro (nao possuir erros), continue
                    if integridade_entrada == True:
                        #   Testar se e' o ultimo loop
                        if (indice_arquivo + 1) == len(arquivos_da_pasta):
                            #   Retorne o diretorio
                            return diretorio_pasta_entrada, arquivos_da_pasta
                    #   Arquivo ruim
                    else:
                        print ("\n\tArquivo '%s' com problemas.\n\tCheque seu arquivo de entrada.\n" %(nome_arquivo.decode()))
                        return None, None
                #   Codigo arquivo nao identificado
                else:
                    #   O Erro ja foi informado
                    return None, None
            #   Formato incorreto
            else:
                print ("\n\tO formato do arquivo '%s' nao adequado.\n" %(nome_arquivo.decode()))
                mensagensIntegridadePlotagens(4, nome_arquivo.decode())
                return None, None
    #   Se NAO for dado um arquivo de entrada
    else:
        print ("\n\tNenhuma pasta selecionada.\n")
        mensagensIntegridadePlotagens(5, '')
        return None, None
#----------------------------------------------------------------------
def identificarCodigoArquivoSaida(diretorio_arquivo):
    """Le parcialmente o arquivo de saida a fim de identificar qual e'"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline()         #"\u000A"
    arquivo_entrada.readline()         #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline()         #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline()         #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline()         #"\u000A"
    arquivo_entrada.readline()         #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline()         #"\u000A"
    arquivo_entrada.readline()         # "Número total de simulações hidrológicas  = %d\u000A"
    linha = arquivo_entrada.readline() # "Número de simulações ???????????         = %d\u000A"
    
    #   Feche o arquivo
    arquivo_entrada.close() 
    
    #   E' PQ
    if linha[21:23] == "Ch":
        return 1
    #   E' PULS
    elif linha[21:23] == "Pu":
        return 2
    #   E' MKC
    elif linha[21:23] == "Mu":
        return 3
    #   E' JUN
    elif linha[21:23] == "Ju":
        return 4
    #   E' Leitura
    elif linha[21:23] == "hi":
        return 5
    #   E' Derivacao
    elif linha[23:25] == "de":
        return 6
    #   Erro: Operacao nao identificada
    else:
        #   Mensagem de erro
        mensagensIntegridadePlotagens(6, diretorio_arquivo.decode())
        return False
#----------------------------------------------------------------------
def checarIntegridadeArquivoSaida(diretorio_arquivo, codigo_arquivo):
    """Checa integridade dos arquivos de saida para as plotagens"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline() #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline() #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() # "Número total de simulações hidrológicas  = %d\u000A"
    
    
    #   PQ
    if codigo_arquivo == 1:
        linha = arquivo_entrada.readline() # "Número de simulações Chuva-Vazão         = %d\u000A"
        #   Armazenar o numero de hidrogramas
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(1,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(2,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nHid = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
        #   Armazenar o numero de intervalos de tempo
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(3,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(4,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nInt = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Número de intervalos de tempo com chuva  = %d\u000A"
        #   Armazenar o numero de intervalos de tempo com chuva
        try: int(linha.split("=")[-1][1:-1])
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(5,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(6,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nIntCh = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
        #   Armazenar o dt
        try: int(linha.split("=")[-1][1:-1])
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(7,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(8,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        DT = int(linha.split("=")[-1][1:-1])
        
        #   Declarar variaveis cuja informacao e' conhecida
        indChuvas = [None for ii in range(nHid)]
        
        #   Seguir lendo
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES CHUVA-VAZÃO ---- \u000A"
        
        #   Loop para ler ;) 
        for ii in range(nHid):
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "Hidrograma %d:%s\u000A"
            linha = arquivo_entrada.readline() # "\u0009Calculada a partir da chuva de projeto: %d\u000A"
            #   Armazenar o indice
            try: int(linha.split(":")[-1][1:-1]) - 1
            except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(9,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
            if int(linha.split(":")[-1][1:-1]) - 1 < 0: 
                arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(10,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
            indChuvas[ii] = int(linha.split(":")[-1][1:-1]) - 1
            arquivo_entrada.readline() # "\u0009       Coeficiente CN = %10.4f [  -  ]\u000A"
            arquivo_entrada.readline() # "\u0009        Área da bacia = %10.4f [ km² ]\u000A"
            arquivo_entrada.readline() # "\u0009Tempo de concentração = %10.4f [horas]\u000A"
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- VAZÕES DE PICO (m³/s) E VOLUMES ESCOADOS (m³) ----\u000A"
        
        #   Aqui nao tem nenhuma informacao relevante para o grafico
        for ii in range(nHid): #    Sao nHid grupos cada um com 5 linhas
            for jj in range(5): #   Sao 5 linhas em cada grupo
                arquivo_entrada.readline() #    Apenas leia pra passar adiante mesmo
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- CHUVAS DE PROJETO (mm) ---- \u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "      dt   Chuva 1   Chuva 2   Chuva 3 ...... Chuva N\u000A"
        
        #   Declarar a matriz das chuvas ordenadas
        nChOrd = max(indChuvas) + 1
        
        #   Loop para ler 
        for jj in range(nIntCh):
            #   Ler a linha: Corpo da tabela
            linha = arquivo_entrada.readline()
            #   Para cada chuva...
            for ii in range(nChOrd):
                if ii < 9:
                    try: float(linha[(ii*10 + 8):(ii*10 + 18)])
                    except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(11,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                    if float(linha[(ii*10 + 8):(ii*10 + 18)]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(12,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                elif ii < 99:
                    try: float(linha[((ii-9)*11 + 98):((ii-9)*11 + 109)])
                    except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(11,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                    if float(linha[((ii-9)*11 + 98):((ii-9)*11 + 109)]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(12,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                else:
                    try: float(linha[((ii-99)*12 + 1088):((ii-99)*12 + 1100)])
                    except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(11,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                    if float(linha[((ii-99)*12 + 1088):((ii-99)*12 + 1100)]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(12,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- CHUVAS EFETIVAS (mm) ---- \u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "      dt   Chuva 1   Chuva 2   Chuva 3 ...... Chuva N\u000A"
        
        #   Loop para ler: Porem nao ha' nada de interessante aqui para o grafico
        for jj in range(nIntCh):
            #   Ler a linha: Corpo da tabela, nao e' necessario armazenar nada, nao ha' nada interessante para o grafico
            arquivo_entrada.readline()
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- HIDROGRAMAS CHUVA-VAZAO (m³/s) ----\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "      dt   Hidrograma 1   Hidrograma 2   .....   Hidrograma N\u000A"
        
        #   Loop para ler 
        for jj in range(nInt):
            #   Ler a linha: Corpo da tabela
            linha = arquivo_entrada.readline()
            #   Para cada chuva...
            for ii in range(nHid):
                if ii < 9:
                    try: float(linha[(ii*15 + 8):(ii*15 + 23)])
                    except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(13,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                    if float(linha[(ii*15 + 8):(ii*15 + 23)]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(14,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                elif ii < 99:
                    try: float(linha[((ii-9)*16 + 143):((ii-9)*16 + 159)])
                    except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(13,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                    if float(linha[((ii-9)*16 + 143):((ii-9)*16 + 159)]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(14,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                else:
                    try: float(linha[((ii-99)*17 + 1583):((ii-99)*17 + 1600)])
                    except: arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(13,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                    if float(linha[((ii-99)*17 + 1583):((ii-99)*17 + 1600)]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadePlotagensPQ(14,jj+1,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
    
    
    #   PULS
    elif codigo_arquivo == 2:
        linha = arquivo_entrada.readline() # "Número de simulações Puls                = %d\u000A"
        #   Armazenar o numero de hidrogramas
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(1,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(2,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nHid = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
        #   Armazenar o numero de intervalos de tempo
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(3,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(4,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nInt = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
        #   Armazenar o dt
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(5,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(6,0,diretorio_arquivo.decode().split("/")[-1]); return False
        DT = int(linha.split("=")[-1][1:-1])
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES DE PROPAGAÇÃO DE PULS ---- \u000A"
        arquivo_entrada.readline() # "\u000A"
        
        #   Loop de leitura
        for jj in range(nHid):
            arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
            arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A"
            arquivo_entrada.readline() # "Hidrograma de entrada oriundo de uma operação de ...\u000A"
            arquivo_entrada.readline() # "Pico de vazão de saída = %14.5f [m³/s]\u000A"%(max(hidrogramas_saida_puls[indice_saida]))
            arquivo_entrada.readline() # "Cota máxima do reservatório = %14.5f [m]\u000A"%(max(cotas_montante_saida_puls[indice_saida])))
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "      dt Hidro_Entrada Hidrogr_Saida Cotas_Reserv.\u000A"
            
            #   Loop de leitura dos hidrogramas
            for ii in range(nInt):
                linha = arquivo_entrada.readline() # Ler corpo da tabela
                try: float(linha[8:22])
                except: arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(7,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                if float(linha[8:22]) < 0:
                    arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(8,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                try: float(linha[22:36])
                except: arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(9,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                if float(linha[22:36]) < 0:
                    arquivo_entrada.close(); mensagensIntegridadePlotagensPULS(10,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
        
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
            arquivo_entrada.readline() # "\u000A"
    
    
    #   MKC
    elif codigo_arquivo == 3:
        linha = arquivo_entrada.readline() # "Número de simulações Muskingum-Cunge     = %d\u000A"
        #   Armazenar o numero de hidrogramas
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(1,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(2,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nHid = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
        #   Armazenar o numero de intervalos de tempo
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(3,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(4,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nInt = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
        #   Armazenar o dt
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(5,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(6,0,diretorio_arquivo.decode().split("/")[-1]); return False
        DT = int(linha.split("=")[-1][1:-1])
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES DE PROPAGAÇÃO DE MUSKINGUM-CUNGE ---- \u000A"
        arquivo_entrada.readline() # "\u000A"
        
        #   Loop de leitura
        for jj in range(nHid):
            arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
            arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A"
            arquivo_entrada.readline() # "Hidrograma de entrada oriundo de uma operação de ...\u000A"
            arquivo_entrada.readline() # "Pico de vazão de saída = %14.5f [m³/s]\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "      dt Hidro_Entrada Hidrogr_Saida\u000A"
            
            #   Loop de leitura dos hidrogramas
            for ii in range(nInt):
                linha = arquivo_entrada.readline() # Ler corpo da tabela
                try: float(linha[8:22])
                except: arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(7,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                if float(linha[8:22]) < 0:
                    arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(8,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                try: float(linha[22:36])
                except: arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(9,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                if float(linha[22:36]) < 0:
                    arquivo_entrada.close(); mensagensIntegridadePlotagensMKC(10,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
        
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
            arquivo_entrada.readline() # "\u000A"
    
    
    #   JUN
    elif codigo_arquivo == 4:
        linha = arquivo_entrada.readline() # "Número de simulações Junções             = %d\u000A"
        #   Armazenar o numero de hidrogramas
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(1,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(2,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nHid = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
        #   Armazenar o numero de intervalos de tempo
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(3,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(4,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nInt = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
        #   Armazenar o dt
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(5,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(6,0,0,diretorio_arquivo.decode().split("/")[-1]); return False
        DT = int(linha.split("=")[-1][1:-1])
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES DE PROPAGAÇÃO DE MUSKINGUM-CUNGE ---- \u000A"
        arquivo_entrada.readline() # "\u000A"
        
        #   Loop de leitura
        for jj in range(nHid):
            arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
            
            #   Variavel contadora de hidrogramas de entrada
            contHid = 0
            linha = arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A"
            #   While para contar o numero de hidrogramas de entrada: 
            #   Ele lera' tambem a vazao de pico gracas 'a forma que fora feita a condicao do if
            #   Entao contHid contara' 1 a mais
            #   While para contar o numero de hidrogramas de entrada + pico
            while not linha == "\n":
                contHid += 1
                linha = arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A"
                
            arquivo_entrada.readline() # "      dt Hidro_Entrada Hidro_Entrada .... Hidrogr_Saida\u000A"
            
            #   Loop de leitura das linhas
            for ii in range(nInt):
                linha = arquivo_entrada.readline() # Ler corpo da tabela
                #   Loop coluna
                #   Como contHid leu tambem o pico, ele e' 1 a mais do que o numero de hidrogramas de entrada, CONTUDO...
                #   Como o range do Python nao inclui o ultimo valor, acaba dando tudo certo: somar um a mais e contar um a menos, resulta no valor correto
                for kk in range(contHid):
                    try: float(linha[((kk*14) + 8):((kk*14) + 22)])
                    except: arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(7,ii+1,kk+1,diretorio_arquivo.decode().split("/")[-1]); return False
                    if float(linha[((kk*14) + 8):((kk*14) + 22)]) < 0:
                        arquivo_entrada.close(); mensagensIntegridadePlotagensJUN(8,ii+1,kk+1,diretorio_arquivo.decode().split("/")[-1]); return False
        
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
            arquivo_entrada.readline() # "\u000A"
    
    
    #   Leitura de hidrogramas
    elif codigo_arquivo == 5:
        linha = arquivo_entrada.readline() # "Número de leitura de hidrogramas         = %d\u000A"
        #   Armazenar o numero de leituras de hidrogramas
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(1,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(2,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nHid = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
        #   Armazenar o numero de intervalos de tempo
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(3,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(4,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nInt = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
        #   Armazenar o dt
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(5,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(6,0,diretorio_arquivo.decode().split("/")[-1]); return False
        DT = int(linha.split("=")[-1][1:-1])
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS LEITURAS DE HIDROGRAMAS ---- \u000A"
        arquivo_entrada.readline() # "\u000A"
    
        #   Loop de leitura
        for jj in range(nHid):
            arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
            arquivo_entrada.readline() # "\u0009Hidrograma de entrada fornecido pelo usuário.\u000A"
            arquivo_entrada.readline() # "\u0009Diretório: '%s'\u000A"
            arquivo_entrada.readline() # "\u0009Pico de vazão de saída = %.5f [m³/s]\u000A"
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "      dt, Hidro_Entrada\u000A"
            
            #   Loop de leitura dos hidrogramas
            for ii in range(nInt):
                linha = arquivo_entrada.readline() # Ler corpo da tabela
                try: float(linha[8:22])
                except: arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(7,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                if float(linha[8:22]) < 0:
                    arquivo_entrada.close(); mensagensIntegridadePlotagensHIDRO(8,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
            
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
            arquivo_entrada.readline() # "\u000A"
    
    
    #   Derivacoes
    elif codigo_arquivo == 6:
        linha = arquivo_entrada.readline() # "Número de operações de derivação         = %d\u000A"
        #   Armazenar o numero de derivacoes
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(1,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(2,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nHid = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
        #   Armazenar o numero de intervalos de tempo
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(3,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(4,0,diretorio_arquivo.decode().split("/")[-1]); return False
        nInt = int(linha.split("=")[-1][1:-1])
        
        linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
        #   Armazenar o dt
        try: int(linha.split("=")[-1][1:-1]) 
        except: arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(5,0,diretorio_arquivo.decode().split("/")[-1]); return False
        if int(linha.split("=")[-1][1:-1]) <= 0: 
            arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(6,0,diretorio_arquivo.decode().split("/")[-1]); return False
        DT = int(linha.split("=")[-1][1:-1])
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS DERIVAÇÕES ---- \u000A"
        arquivo_entrada.readline() # "\u000A"
        
        #   Loop de leitura
        for jj in range(nHid):
            arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
            arquivo_entrada.readline() # "\u0009Número do hidrograma de entrada = %d\u000A"
            arquivo_entrada.readline() # "\u0009Hidrograma de entrada oriundo de uma operação ...\u000A"
            arquivo_entrada.readline() # "\u0009Tipo de derivação: ...\u000A"
            arquivo_entrada.readline() # "\u0009Valor derivado (m³/s) = %.2f\u000A" OU "\u0009Valor porcentual derivado (%%) = %.2f\u000A" OU "\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"
            arquivo_entrada.readline() # "\u0009Hidrograma de saída: Curso principal\u000A" OU "\u0009Hidrograma de saída: Derivado\u000A"
            arquivo_entrada.readline() # "\u0009Pico de vazão de saída = %14.5f [m³/s]\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "      dt Hidro_Entrada Hidrogr_Saida\u000A"
        
            #   Loop de leitura dos hidrogramas
            for ii in range(nInt):
                linha = arquivo_entrada.readline() # Ler corpo da tabela
                try: float(linha[8:22])
                except: arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(7,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                if float(linha[8:22]) < 0:
                    arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(8,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                try: float(linha[22:36])
                except: arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(9,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
                if float(linha[22:36]) < 0:
                    arquivo_entrada.close(); mensagensIntegridadePlotagensDERIVACAO(10,ii+1,diretorio_arquivo.decode().split("/")[-1]); return False
        
            arquivo_entrada.readline() # "\u000A"
            arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
            arquivo_entrada.readline() # "\u000A"
    
    
    #   Feche o arquivo
    arquivo_entrada.close()
    
    #   Se chegou aqui, retorne True
    return True
#----------------------------------------------------------------------
def lerArquivoSaidaPQ(diretorio_arquivo):
    """Le o arquivo de saida das operacoes de Chuva-vazao"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline() #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline() #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() # "Número total de simulações hidrológicas  = %d\u000A"
    
    linha = arquivo_entrada.readline() # "Número de simulações Chuva-Vazão         = %d\u000A"
    #   Armazenar o numero de hidrogramas
    nHid = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
    #   Armazenar o numero de intervalos de tempo
    nInt = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Número de intervalos de tempo com chuva  = %d\u000A"
    #   Armazenar o numero de intervalos de tempo com chuva
    nIntCh = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
    #   Armazenar o dt
    DT = int(linha.split("=")[-1][1:-1])
    
    #   Declarar variaveis cuja informacao e' conhecida
    hidrogramas = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    titulos     = [""   for ii in range(nHid)]
    indChuvas   = [None for ii in range(nHid)]
    
    #   Seguir lendo
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES CHUVA-VAZÃO ---- \u000A"
    
    #   Loop para ler ;) 
    for ii in range(nHid):
        arquivo_entrada.readline()         # "\u000A"
        linha = arquivo_entrada.readline() # "Hidrograma %d:%s\u000A"
        #   Armazenar o local
        titulos[ii] = linha.split(":")[-1][0:-1]
        linha = arquivo_entrada.readline() # "\u0009Calculada a partir da chuva de projeto: %d\u000A"
        #   Armazenar o indice
        indChuvas[ii] = int(linha.split(":")[-1][1:-1]) - 1
        arquivo_entrada.readline() # "\u0009       Coeficiente CN = %10.4f [  -  ]\u000A"
        arquivo_entrada.readline() # "\u0009        Área da bacia = %10.4f [ km² ]\u000A"
        arquivo_entrada.readline() # "\u0009Tempo de concentração = %10.4f [horas]\u000A"
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- VAZÕES DE PICO (m³/s) E VOLUMES ESCOADOS (m³) ----\u000A"
    
    #   Aqui nao tem nenhuma informacao relevante para o grafico
    for ii in range(nHid): #    Sao nHid grupos cada um com 5 linhas
        for jj in range(5): #   Sao 5 linhas em cada grupo
            arquivo_entrada.readline() #    Apenas leia pra passar adiante mesmo
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- CHUVAS DE PROJETO (mm) ---- \u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "      dt   Chuva 1   Chuva 2   Chuva 3 ...... Chuva N\u000A"
    
    #   Declarar a matriz das chuvas ordenadas
    nChOrd = max(indChuvas) + 1
    chuvasOrd = array([[0.0 for ii in range(nIntCh)] for jj in range(nChOrd)], float64)
    chuvasEfe = array([[0.0 for ii in range(nIntCh)] for jj in range(nHid)], float64)
    
    #   Loop para ler 
    for jj in range(nIntCh):
        #   Ler a linha: Corpo da tabela
        linha = arquivo_entrada.readline()
        #   Para cada chuva...
        for ii in range(nChOrd):
            if ii < 9:
                chuvasOrd[ii][jj] = float(linha[(ii*10 + 8):(ii*10 + 18)])
            elif ii < 99:
                chuvasOrd[ii][jj] = float(linha[((ii-9)*11 + 98):((ii-9)*11 + 109)])
            else:
                chuvasOrd[ii][jj] = float(linha[((ii-99)*12 + 1088):((ii-99)*12 + 1100)])
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- CHUVAS EFETIVAS (mm) ---- \u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "      dt   Chuva 1   Chuva 2   Chuva 3 ...... Chuva N\u000A"
    
    #   Loop para ler: Porem nao ha' nada de interessante aqui para o grafico
    for jj in range(nIntCh):
        #   Ler a linha: Corpo da tabela
        linha = arquivo_entrada.readline()
        #   Para cada chuva...
        for ii in range(nHid):
            if ii < 9:
                chuvasEfe[ii][jj] = float(linha[(ii*10 + 8):(ii*10 + 18)])
            elif ii < 99:
                chuvasEfe[ii][jj] = float(linha[((ii-9)*11 + 98):((ii-9)*11 + 109)])
            else:
                chuvasEfe[ii][jj] = float(linha[((ii-99)*12 + 1088):((ii-99)*12 + 1100)])
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- HIDROGRAMAS CHUVA-VAZAO (m³/s) ----\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "      dt   Hidrograma 1   Hidrograma 2   .....   Hidrograma N\u000A"
    
    #   Loop para ler 
    for jj in range(nInt):
        #   Ler a linha: Corpo da tabela
        linha = arquivo_entrada.readline()
        #   Para cada chuva...
        for ii in range(nHid):
            if ii < 9:
                hidrogramas[ii][jj] = float(linha[(ii*15 + 8):(ii*15 + 23)])
            elif ii < 99:
                hidrogramas[ii][jj] = float(linha[((ii-9)*16 + 143):((ii-9)*16 + 159)])
            else:
                hidrogramas[ii][jj] = float(linha[((ii-99)*17 + 1583):((ii-99)*17 + 1600)])
    
    #   Feche o arquivo
    arquivo_entrada.close()        
    
    #   Return
    return hidrogramas, chuvasOrd, chuvasEfe, indChuvas, DT, titulos
#----------------------------------------------------------------------
def lerArquivoSaidaPULS(diretorio_arquivo):
    """Le o arquivo de saida das operacoes de Puls"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline() #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline() #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() # "Número total de simulações hidrológicas  = %d\u000A"
    
    linha = arquivo_entrada.readline() # "Número de simulações Puls                = %d\u000A"
    #   Armazenar o numero de hidrogramas
    nHid = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
    #   Armazenar o numero de intervalos de tempo
    nInt = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
    #   Armazenar o dt
    DT = int(linha.split("=")[-1][1:-1])
    
    #   Declarar variaveis cuja informacao e' conhecida
    hidrogramas_entrada = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    hidrogramas_saida   = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    titulos = ["" for ii in range(nHid)]
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES DE PROPAGAÇÃO DE PULS ---- \u000A"
    arquivo_entrada.readline() # "\u000A"
    
    #   Loop de leitura
    for jj in range(nHid):
        linha = arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
        #   Armazenar o local
        titulos[jj] = linha.split(":")[-1][0:-1]
        arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A" OU "\u0009Hidrograma de entrada fornecido pelo usuário.\u000A"
        arquivo_entrada.readline() # "Hidrograma de entrada oriundo de uma operação de ...\u000A" OU "\u0009Diretório: '%s'\u000A"
        arquivo_entrada.readline() # "Pico de vazão de saída = %14.5f [m³/s]\u000A"%(max(hidrogramas_saida_puls[indice_saida]))
        arquivo_entrada.readline() # "Cota máxima do reservatório = %14.5f [m]\u000A"%(max(cotas_montante_saida_puls[indice_saida])))
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "      dt, Hidro_Entrada, Hidrogr_Saida, Cotas_Reserv.\u000A"
        
        #   Loop de leitura dos hidrogramas
        for ii in range(nInt):
            linha = arquivo_entrada.readline() # Ler corpo da tabela
            hidrogramas_entrada[jj][ii] = float(linha[8:22])
            hidrogramas_saida[jj][ii] = float(linha[22:36])
    
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
    
    #   Feche o arquivo
    arquivo_entrada.close()
    
    #   retornar
    return hidrogramas_entrada, hidrogramas_saida, DT, titulos
#----------------------------------------------------------------------
def lerArquivoSaidaMKC(diretorio_arquivo):
    """Le o arquivo de saida das operacoes Muskingum-Cunge"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline() #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline() #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() # "Número total de simulações hidrológicas  = %d\u000A"
    
    linha = arquivo_entrada.readline() # "Número de simulações Muskingum-Cunge     = %d\u000A"
    #   Armazenar o numero de hidrogramas
    nHid = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
    #   Armazenar o numero de intervalos de tempo
    nInt = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
    #   Armazenar o dt
    DT = int(linha.split("=")[-1][1:-1])
    
    #   Declarar variaveis cuja informacao e' conhecida
    hidrogramas_entrada = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    hidrogramas_saida   = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    titulos = ["" for ii in range(nHid)]
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES DE PROPAGAÇÃO DE MUSKINGUM-CUNGE ---- \u000A"
    arquivo_entrada.readline() # "\u000A"
    
    #   Loop de leitura
    for jj in range(nHid):
        linha = arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
        #   Armazenar o local
        titulos[jj] = linha.split(":")[-1][0:-1]
        arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A" OU "\u0009Hidrograma de entrada fornecido pelo usuário.\u000A"
        arquivo_entrada.readline() # "Hidrograma de entrada oriundo de uma operação de ...\u000A" OU "\u0009Diretório: '%s'\u000A"
        arquivo_entrada.readline() # "Pico de vazão de saída = %14.5f [m³/s]\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "      dt, Hidro_Entrada, Hidrogr_Saida\u000A"
        
        #   Loop de leitura dos hidrogramas
        for ii in range(nInt):
            linha = arquivo_entrada.readline() # Ler corpo da tabela
            hidrogramas_entrada[jj][ii] = float(linha[8:22])
            hidrogramas_saida[jj][ii] = float(linha[22:36])
    
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
    
    #   Feche o arquivo
    arquivo_entrada.close()
    
    #   retornar
    return hidrogramas_entrada, hidrogramas_saida, DT, titulos
#----------------------------------------------------------------------
def lerArquivoSaidaJUN(diretorio_arquivo):
    """Le o arquivo de saida das juncoes"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline() #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline() #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() # "Número total de simulações hidrológicas  = %d\u000A"
    
    linha = arquivo_entrada.readline() # "Número de simulações Junções             = %d\u000A"
    #   Armazenar o numero de hidrogramas
    nHid = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
    #   Armazenar o numero de intervalos de tempo
    nInt = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
    #   Armazenar o dt
    DT = int(linha.split("=")[-1][1:-1])
    
    #   Declarar variaveis cuja informacao e' conhecida
    titulos = ["" for ii in range(nHid)]
    hidrogramas = [] #  Vou dar append, cada [...] tera' varios [...] sendo o ultimo deles o hidrograma de saida
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS SIMULAÇÕES DE PROPAGAÇÃO DE MUSKINGUM-CUNGE ---- \u000A"
    arquivo_entrada.readline() # "\u000A"
    
    #   Loop de leitura
    for jj in range(nHid):
        linha = arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
        #   Armazenar o local
        titulos[jj] = linha.split(":")[-1][0:-1]
        
        #   Variavel contadora de hidrogramas de entrada
        contHid = 0
        linha = arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A"
        #   While para contar o numero de hidrogramas de entrada: 
        #   Ele lera' tambem a vazao de pico gracas 'a forma que fora feita a condicao do if
        #   Entao contHid contara' 1 a mais
        while not linha == "\n":
            contHid += 1
            linha = arquivo_entrada.readline() # "Número do hidrograma de entrada = %d\u000A"
        
        #   Como terminei de ler no pico, continuo a partir do cabecalho
        arquivo_entrada.readline() # "      dt Hidro_Entrada Hidro_Entrada .... Hidrogr_Saida\u000A"
        
        #   Declarar o arranjo que vai armazenar os valores dessa juncao
        #   Como contHid leu tambem o pico, ele e' 1 a mais do que o numero de hidrogramas de entrada, CONTUDO...
        #   Como o range do Python nao inclui o ultimo valor, acaba dando tudo certo: somar um a mais e contar um a menos, resulta no valor correto
        hidrogramas_operacao = array([[0.0 for ii in range(nInt)] for kk in range(contHid)], float64)
        
        #   Loop de leitura das linhas
        for ii in range(nInt):
            linha = arquivo_entrada.readline() # Ler corpo da tabela
            #   Loop coluna
            for kk in range(contHid):
                hidrogramas_operacao[kk][ii] = float(linha[((kk*14) + 8):((kk*14) + 22)])
        
        #   Juntar tudo em uma unica variavel
        hidrogramas.append(hidrogramas_operacao)
    
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
    
    #   Feche o arquivo
    arquivo_entrada.close()
    
    #   retornar
    return hidrogramas, DT, titulos
#----------------------------------------------------------------------
def lerArquivoSaidaHIDRO(diretorio_arquivo):
    """Le o arquivo de saida das operacoes leitura de hidrogramas"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline() #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline() #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() # "Número total de simulações hidrológicas  = %d\u000A"
    
    linha = arquivo_entrada.readline() # "Número de leitura de hidrogramas         = %d\u000A"
    #   Armazenar o numero de hidrogramas
    nHid = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
    #   Armazenar o numero de intervalos de tempo
    nInt = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
    #   Armazenar o dt
    DT = int(linha.split("=")[-1][1:-1])
    
    #   Declarar variaveis cuja informacao e' conhecida
    hidrogramas_entrada = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    titulos = ["" for ii in range(nHid)]
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # " ---- INFORMAÇÕES DAS LEITURAS DE HIDROGRAMAS ----\u000A"
    arquivo_entrada.readline() # "\u000A"
    
    #   Loop de leitura
    for jj in range(nHid):
        linha = arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
        #   Armazenar o local
        titulos[jj] = linha.split(":")[-1][0:-1]
        arquivo_entrada.readline() # "\u0009Hidrograma de entrada fornecido pelo usuário.\u000A"
        arquivo_entrada.readline() # "\u0009Diretório: '%s'\u000A"
        arquivo_entrada.readline() # "\u0009Pico de vazão de saída = %.5f [m³/s]\u000A"
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "      dt, Hidro_Entrada\u000A"
        
        #   Loop de leitura dos hidrogramas
        for ii in range(nInt):
            linha = arquivo_entrada.readline() # Ler corpo da tabela
            hidrogramas_entrada[jj][ii] = float(linha[8:22])
        
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
    
    #   Feche o arquivo
    arquivo_entrada.close()
    
    #   retornar
    return hidrogramas_entrada, DT, titulos
#----------------------------------------------------------------------
def lerArquivoSaidaDERIVACAO(diretorio_arquivo):
    """Le o arquivo de saida das operacoes derivacoes"""
    #   Abrir o arquivo para ler
    arquivo_entrada = open(diretorio_arquivo, mode='r', buffering=-1, encoding='utf-8')
    
    #   Comecar a leitura: o inicio e' padrao de todos os arquivos
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #"                         MODELO HYDROLIB\u000A"
    arquivo_entrada.readline() #"                     RESULTADOS DA MODELAGEM\u000A"
    arquivo_entrada.readline() #"------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() #" ---- PARAMETROS GERAIS DA SIMULACAO  ----\u000A"
    arquivo_entrada.readline() #"\u000A"
    arquivo_entrada.readline() # "Número total de simulações hidrológicas  = %d\u000A"
    
    linha = arquivo_entrada.readline() # "Número de operações de derivação         = %d\u000A"
    #   Armazenar o numero de hidrogramas
    nHid = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Número de intervalos de tempo            = %d\u000A"
    #   Armazenar o numero de intervalos de tempo
    nInt = int(linha.split("=")[-1][1:-1])
    
    linha = arquivo_entrada.readline() # "Duração do intervalo de tempo (segundos) = %d\u000A"
    #   Armazenar o dt
    DT = int(linha.split("=")[-1][1:-1])
    
    #   Declarar variaveis cuja informacao e' conhecida
    hidrogramas_entrada = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    hidrogramas_saida   = array([[0.0 for ii in range(nInt)] for jj in range(nHid)], float64)
    titulos = ["" for ii in range(nHid)]
    
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
    arquivo_entrada.readline() # "\u000A"
    arquivo_entrada.readline() # "---- INFORMAÇÕES DAS DERIVAÇÕES ---- \u000A"
    arquivo_entrada.readline() # "\u000A"
    
    #   Loop de leitura
    for jj in range(nHid):
        linha = arquivo_entrada.readline() # "Operação hidrológica %d:%s\u000A"
        #   Armazenar o local
        titulos[jj] = linha.split(":")[-1][0:-1]
        arquivo_entrada.readline() # "\u0009Número do hidrograma de entrada = %d\u000A"
        arquivo_entrada.readline() # "\u0009Hidrograma de entrada oriundo de uma operação ...\u000A"
        arquivo_entrada.readline() # "\u0009Tipo de derivação: ...\u000A"
        arquivo_entrada.readline() # "\u0009Valor derivado (m³/s) = %.2f\u000A" OU "\u0009Valor porcentual derivado (%%) = %.2f\u000A" OU "\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"
        arquivo_entrada.readline() # "\u0009Hidrograma de saída: Curso principal\u000A" OU "\u0009Hidrograma de saída: Derivado\u000A"
        arquivo_entrada.readline() # "\u0009Pico de vazão de saída = %14.5f [m³/s]\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "      dt Hidro_Entrada Hidrogr_Saida\u000A"
        
        #   Loop de leitura dos hidrogramas
        for ii in range(nInt):
            linha = arquivo_entrada.readline() # Ler corpo da tabela
            hidrogramas_entrada[jj][ii] = float(linha[8:22])
            hidrogramas_saida[jj][ii] = float(linha[22:36])
            
        arquivo_entrada.readline() # "\u000A"
        arquivo_entrada.readline() # "------------------------------------------------------------------------\u000A"
        arquivo_entrada.readline() # "\u000A"
    
    #   Feche o arquivo
    arquivo_entrada.close()
    
    #   retornar
    return hidrogramas_entrada, hidrogramas_saida, DT, titulos
#----------------------------------------------------------------------