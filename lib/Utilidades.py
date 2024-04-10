# -*- coding: utf-8 -*-

#   Neste arquivos ficam as funcoes utilitarias necessarias para o funcionamento do modelo
#   Aqui voce encontrara' funcoes de diversas partes do codigo, como uma especie de "caixa de ferramentas"
#   Neste arquivo estao funcoes de centralizacao, contagem de linhas, ordenanoes de operacoes e todas as mensagens de erro.
#   Decidiu-se por coloca'-las em um ifs ao inves de uma lista para poupar memoria.


#   Import das bibliotecas Python
import errno
from sys import stdout, exit
from os import path, makedirs, remove
from tkinter import messagebox

#-----------------------------------------------------------------------
def centralizarJanela(janela):
    """
    centraliza uma janela tkinter
    parametro janela : root ou Toplevel que sera' centralizada
    """
    janela.update_idletasks()
    #   Largura da janela
    largura = janela.winfo_width()
    #   Largura do frame
    largura_frame = janela.winfo_rootx() - janela.winfo_x()
    #   Largura total
    largura_janela = largura + 2 * largura_frame
    #   Altura da janela
    altura = janela.winfo_height()
    #   Altura do titulo
    altura_titulo = janela.winfo_rooty() - janela.winfo_y()
    #   Altura total
    altura_janela = altura + altura_titulo + largura_frame
    x = janela.winfo_screenwidth() // 2 - largura_janela // 2
    y = int(janela.winfo_screenheight()*0.90) // 2 - altura_janela // 2
    janela.geometry('{}x{}+{}+{}'.format(largura, altura, x, y))
    janela.deiconify()
#-----------------------------------------------------------------------
def criarPasta(diretorio):
    """Cria uma pasta no diretorio desejado"""
    try:
        #   Faca a pasta
        makedirs(diretorio)
    #   Errou!
    except OSError as exception:
        #   Mostrar apenas se o erro for diferente de "ja existe"
        if exception.errno != errno.EEXIST:
            #   Mostre
            raise
#-----------------------------------------------------------------------
def deletarArquivoAntigo(diretorio_pasta, nome_arquivo, extensao):
    """
    Deleta o arquivo de texto no diretorio especificado.
    
    diretorio_pasta = string
    nome_arquivo = string
    """
    #   Verificar se o arquivo existe
    if (path.isfile(diretorio_pasta + "/".encode() + nome_arquivo + ".".encode() + extensao) == True):
        #   Tente deletar o arquivo
        try:
            #   Delete o arquivo antigo
            remove(diretorio_pasta + "/".encode() + nome_arquivo + ".".encode() + extensao)

        #   Ocorreu um erro...
        except:
            #   Avise o usuario que o arquivo antigo NAO foi deletado
            mensagensManejoArquivos(1, nome_arquivo.decode(), extensao.decode())
            exit()
#-----------------------------------------------------------------------
def escreverArquivoEntrada(diretorio_do_software, strings_arquivo):
    """Escreve o arquivo de entrada gerado pelo usuario no ambiente auxiliar"""
    #    preparo arquivo de saida
    SaidaMHEAuxiliar, fileExtension = path.splitext(diretorio_do_software + "/Entrada/Arquivo_entrada".encode())
    SaidaMHEAuxiliar               += ".hyd".encode()
    SaidaMHEAuxiliar                = open(SaidaMHEAuxiliar, 'w')
    
    #   Escrever strings
    for ii in range(len(strings_arquivo)):
        SaidaMHEAuxiliar.write(strings_arquivo[ii])
    #   Feche
    SaidaMHEAuxiliar.close()
#-----------------------------------------------------------------------
def atualizarBarraProgresso(n, nmax):
    """Desenha uma barra de progresso na tela do cmd"""
    #   Evitar divisao por zero
    if nmax > 0:
        #   proporcoes
        progresso = int((float(n)/(nmax))*50)
        faltante = 50 - progresso
        #   inicio
        b = "\t|"
        #   progresso
        for i in range(progresso):
            b += "#"
        #   faltante
        for i2 in range(faltante):
            b += " "
        #   fim
        if progresso < 50:
            b += "|"
        else:
            b += "|\n"
        #   escreva barra
        stdout.write(b + "\r")
#-----------------------------------------------------------------------
def contarLinhas(diretorio_arquivo):
    """Conta as linhas de um arquivo de texto cujo diretorio e' informado em diretorio_arquivo"""
    numero_linhas = sum(1 for linha in open(diretorio_arquivo,'r'))
    return numero_linhas
#-----------------------------------------------------------------------
def organizarIndices(ordem_execucao, codigo_operacoes_hidrologicas):
    """Funcao que cria os indices para as matrizes de hidrogramas."""
    #   codigo_operacoes_hidrologicas =  1->CHUVA-VAZAO; 2->PULS; 3->MKC; 4->JUNCAO; 5->HIDROGRAMA; Nao esta' ordenada; Tem len() == nop
    #   ordem_execucao = INDICES das operacoes ordenados conforme ordem de execucao; Tem len() == nop

    #   Declarar variaveis
    indices_saida_pq        = []
    indices_saida_puls      = []
    indices_saida_mkc       = []
    indices_saida_jun       = []
    indices_saida_hidro     = []
    indices_saida_derivacao = []
    
    #   Ordenar os codigos
    for indice_entrada, indice_ordenado in enumerate(ordem_execucao):
        #   Se a operacao for PQ
        if codigo_operacoes_hidrologicas[indice_entrada] == 1:
            #   Preencho a variavel
            indices_saida_pq.append(indice_ordenado)
        #   Se a operacao for PULS
        elif codigo_operacoes_hidrologicas[indice_entrada] == 2:
            #   Preencho a variavel
            indices_saida_puls.append(indice_ordenado)
        #   Se a operacao for MKC
        elif codigo_operacoes_hidrologicas[indice_entrada] == 3:
            #   Preencho a variavel
            indices_saida_mkc.append(indice_ordenado)
        #   Se a operacao for JUN
        elif codigo_operacoes_hidrologicas[indice_entrada] == 4:
            #   Preencho a variavel
            indices_saida_jun.append(indice_ordenado)
        #   Se a operacao for leitura de hidrograma
        elif codigo_operacoes_hidrologicas[indice_entrada] == 5:
            indices_saida_hidro.append(indice_ordenado)
        #   Se a operacao for DERIVACAO
        elif codigo_operacoes_hidrologicas[indice_entrada] == 6:
            indices_saida_derivacao.append(indice_ordenado)
            
    return indices_saida_pq, indices_saida_puls, indices_saida_mkc, indices_saida_jun, indices_saida_hidro, indices_saida_derivacao
#-----------------------------------------------------------------------
def corrigirCaracteres(string):
    """Substitui os acentos para nao dar ruim nas plotagens"""
    #   A
    string = string.replace("Ã","A")
    string = string.replace("Â","A")
    string = string.replace("Á","A")
    string = string.replace("À","A")
    string = string.replace("Ä","A")
    string = string.replace("ã","a")
    string = string.replace("â","a")
    string = string.replace("á","a")
    string = string.replace("à","a")
    string = string.replace("ä","a")
    #   E
    string = string.replace("Ê","E")
    string = string.replace("É","E")
    string = string.replace("È","E")
    string = string.replace("Ë","E")
    string = string.replace("ê","e")
    string = string.replace("é","e")
    string = string.replace("è","e")
    string = string.replace("ë","e")
    #   I
    string = string.replace("Î","I")
    string = string.replace("Í","I")
    string = string.replace("Ì","I")
    string = string.replace("Ï","I")
    string = string.replace("î","i")
    string = string.replace("í","i")
    string = string.replace("ì","i")
    string = string.replace("ï","i")
    #   O
    string = string.replace("Õ","O")
    string = string.replace("Ô","O")
    string = string.replace("Ó","O")
    string = string.replace("Ò","O")
    string = string.replace("Ö","O")
    string = string.replace("õ","o")
    string = string.replace("ô","o")
    string = string.replace("ó","o")
    string = string.replace("ò","o")
    string = string.replace("ö","o")
    #   U
    string = string.replace("Û","U")
    string = string.replace("Ú","U")
    string = string.replace("Ù","U")
    string = string.replace("Ü","U")
    string = string.replace("û","u")
    string = string.replace("ú","u")
    string = string.replace("ù","u")
    string = string.replace("ü","u")
    #   Ç
    string = string.replace("Ç","c")
    string = string.replace("ç","c")
    #   N
    string = string.replace("Ñ","n")
    string = string.replace("ñ","n")
    #   Return
    return string
#-----------------------------------------------------------------------
def mensagensInterfaces(n_mensagem, detalhes):
    """Tem as mensagens de erros do arquivo Modelo_Hidrologico_Ecotecnologias"""
    if n_mensagem == 1: messagebox.showerror("Verifique os dados de entrada!", "Selecione um arquivo de texto (formato: '*.txt').")
    elif n_mensagem == 2: messagebox.showerror("Verifique os dados de entrada!", "O modelo não conseguiu localizar o arquivo selecionado.") 
    elif n_mensagem == 3: messagebox.showinfo("Verifique os dados de entrada!", "Arquivo de entrada não selecionado.\n\nTente novamente.") 
    elif n_mensagem == 4: messagebox.showerror("Verifique os dados de entrada!", detalhes) 
    elif n_mensagem == 5: messagebox.showinfo("Aviso", "Arquivo de entrada gerado com sucesso!\nVerifique o diretório do modelo.\n\nLembrete: É possível criar arquivos de entrada manualmente.")
#-----------------------------------------------------------------------
def mensagensSelecaoArquivos(n_mensagem, detalhes):
    """Tem as mensagens de erros do arquivo Leitura"""
    if n_mensagem == 1: messagebox.showerror("Erro", "Formato de arquivo inválido!\nSelecione um arquivo no formato '*.hyd'.")
    elif n_mensagem == 2: messagebox.showinfo("Aviso", "Nenhum arquivo selecionado. Tente novamente.")
    elif n_mensagem == 3: messagebox.showinfo("Aviso", "Nenhum dos arquivos da pasta selecionada possui o formato adequado.\n\nNenhuma pasta selecionada. Tente novamente.")
    elif n_mensagem == 4: messagebox.showerror("Erro", "O formato do arquivo '%s' é incompatível.\nSelecione um arquivo no formato '*.hyd'." %(detalhes))
    elif n_mensagem == 5: messagebox.showinfo("Aviso", "Nenhuma pasta selecionada. Tente novamente.")
    elif n_mensagem == 6: messagebox.showerror("Erro", "A pasta selecionada ('%s') não existente." %(detalhes))
#-----------------------------------------------------------------------
def mensagensIntegridadeInfoGerais(n_mensagem, linhas_lidas):
    """Tem as mensagens de erros do arquivo Leitura na parte de entrada de informacoes gerais"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas. Verifique o arquivo de entrada.\n\nDica: Não se esqueca dos ponto-e-virgula (;) após cada dado (inclusive o último de cada linha).\n\nExemplo: 'INICIO; 2160; 60; 2; 1440; 7;'\n\nLembre-se de terminar a linha com ponto-e-vírgula..")
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de intervalos de tempo da simulação deve ser um número inteiro.")
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A duração do intervalo de tempo deve ser um número inteiro.")
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de postos de chuvas da simulação deve ser um número inteiro.")
    elif n_mensagem == 5: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de intervalos de tempo das chuvas deve ser um número inteiro.")
    elif n_mensagem == 6: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de operações hidrológicas deve ser um número inteiro.")
    elif n_mensagem == 7: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de intervalos da simulação deve ser maior ou igual ao número de intervalos de tempo com chuva.")
    elif n_mensagem == 8: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de intervalos de tempo da simulação não pode ser zero.")
    elif n_mensagem == 9: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A duração do intervalo de tempo da simulação não pode ser zero.")
    elif n_mensagem == 10: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de intervalos de tempo das chuvas não pode ser zero.")
    elif n_mensagem == 11: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de operações hidrológicas da simulação não pode ser zero.")
#-----------------------------------------------------------------------
def mensagensIntegridadeChuvas(n_mensagem, linhas_lidas, nch, detalhes):
    """Tem as mensagens de erros do arquivo Leitura na parte de entrada de informacoes de chuva"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas para o posto de chuva %d.\n\nExemplo:'CHUVA; 1;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nch))
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número do posto de chuva deve ser inteiro.")
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas para o posto de chuva %d (IDF).\n\nExemplo: 'IDF; 1; 0.5; 10; 823.4; 10.2; 1.42; 0.79; 0;'\n\nLembre-se de terminar a linha com ponto-e-vírgula.." %(nch))
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O tipo da IDF deve ser um número inteiro.")
    elif n_mensagem == 5: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A posição do pico da chuva deve ser um número decimal.")
    elif n_mensagem == 6: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O tempo de retorno deve ser um número inteiro.")
    elif n_mensagem == 7: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro A da IDF deve ser um número decimal.")
    elif n_mensagem == 8: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro B da IDF deve ser um número decimal.")
    elif n_mensagem == 9: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro C da IDF deve ser um número decimal.")
    elif n_mensagem == 10: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro D da IDF deve ser um número decimal.")
    elif n_mensagem == 11: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O limite de intensidade de chuva dos primeiros intervalos de tempo deve ser um número inteiro.\n\nDica: Para desativar o limitante de intensidade da chuva dos primeiros intervalos de tempo utilize zero.")
    elif n_mensagem == 12: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Tipo da IDF '%s' desconhecido.\nTipo(s) conhecido(s): 1" %(detalhes))
    elif n_mensagem == 13: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor da posição do pico deve ser maior ou igual a 0 e menor ou igual a 1.")
    elif n_mensagem == 14: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O tempo de retorno não pode ser zero.")
    elif n_mensagem == 15: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro A da IDF não pode ser zero.")
    elif n_mensagem == 16: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro B da IDF não pode ser zero.")
    elif n_mensagem == 17: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro C da IDF não pode ser zero.")
    elif n_mensagem == 18: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O parâmetro D da IDF não pode ser zero.")
    elif n_mensagem == 19: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O limite de intensidade de chuva dos primeiros intervalos de tempo (em minutos) não pode ser negativo.")
    elif n_mensagem == 20: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas para o posto de chuva %d.\n\nExemplo:'CHUVA; 1;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nch))
    elif n_mensagem == 20: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A extensão do arquivo fornecido para o posto de chuva %d deve ser txt." %(nch))
    elif n_mensagem == 21: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O arquivo fornecido para o posto de chuva %d não foi localizado." %(nch))
    elif n_mensagem == 22: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Tipo de chuva '%s' não definido.\n\nTipos definidos: 'IDF' ou 'OBS'." %(detalhes))
    elif n_mensagem == 23: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Número do posto de chuva incorreto.\nNúmero esperado: %d" %(nch))
#-----------------------------------------------------------------------
def mensagensIntegridadePQ(n_mensagem, linhas_lidas, nop, chuva_numero, nch_declaradas):
    """Tem as mensagens de erros do arquivo Leitura na parte de entrada de informacoes de PQ"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número da operação hidrológica deve ser inteiro.")
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas na operação %d (Chuva-Vazao).\n\nExemplo: 'PQ; 1;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nop))
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número do posto de chuva utilizada nas operações hidrológicas de chuva-vazão deve ser inteiro.")
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Não é possível utilizar o posto de chuva %d na operação %d pois há apenas %d postos de chuva declarados nas informações gerais." %(chuva_numero,nop,nch_declaradas))
    elif n_mensagem == 5: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas ao fornecer o coeficiente CN.\n\nExemplo: 'CN; 83.4;'\n\nLembre-se de terminar a linha com ponto-e-vírgula.")
    elif n_mensagem == 6: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Estrutura da linha incorreta ao inserir o coeficiente CN.\n\nExemplo: 'CN; 75.4;'\n\nLembre-se de terminar a linha com ponto-e-vírgula.")
    elif n_mensagem == 7: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O coeficiente CN deve ser um número decimal.")
    elif n_mensagem == 8: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor de CN deve ser maior que zero e menor ou igual a 100.")
    elif n_mensagem == 9: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas de propagação de escoamento\n\nExemplo: 'HUT; 43.3; 1.73;' ou 'HUT; 43.3; KIRPICH; 40.2; 10.2;'\n\nLembre-se de terminar a linha com ponto-e-vírgula.")
    elif n_mensagem == 10: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Estrutura da linha incorreta ao inserir as informações de propagação de escoamento.\n\nExemplo: 'HUT; 43.3; 1.73;' ou 'HUT; 43.3; KIRPICH; 40.2; 10.2;'\n\nLembre-se de terminar a linha com ponto-e-vírgula.")
    elif n_mensagem == 11: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor da área da bacia deve ser decimal.")
    elif n_mensagem == 12: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor da área da bacia deve ser maior que zero.")
    elif n_mensagem == 13: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A diferença de cota da bacia (m) deve ser um número decimal.")
    elif n_mensagem == 14: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O comprimento do canal (km) deve ser um número decimal.")
    elif n_mensagem == 15: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A diferença de cota da bacia deve ser maior que zero.")
    elif n_mensagem == 16: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O comprimento do canal deve ser maior que zero.")
    elif n_mensagem == 17: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor do tempo de concentração deve ser um número decimal.")
    elif n_mensagem == 18: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor do tempo de concentração deve ser um maior que zero.")
#-----------------------------------------------------------------------
def mensagensIntegridadePULS(n_mensagem, linhas_lidas, nop, hidro_numero, nop_declaradas, detalhes):
    """Tem as mensagens de erros do arquivo Leitura na parte de entrada de informacoes PULS"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas para operação %d (propagação de reservatorios de Puls).\n\nExemplo: 'PULS; 5; 15.0; 5.0; 5;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nop))
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número da operação que originará o hidrograma de entrada desta operação (%d) deve ser inteiro."%(nop))
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número da operação que originará o hidrograma de entrada desta operação (%d) deve ser maior que zero."%(nop))
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Não é possível utilizar o hidrograma oriundo da operação %d na operação %d pois há apenas %d operações hidrológicas declaradas nas informações gerais." %(hidro_numero,nop,nop_declaradas))
    elif n_mensagem == 5: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota inicial do reservatório deve ser um número decimal.")
    elif n_mensagem == 6: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota inicial do reservatório não pode ser negativa.")
    elif n_mensagem == 7: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor de vazão do by-pass deve ser um número decimal.")
    elif n_mensagem == 8: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor de vazão do by-pass não pode ser negativo.")
    elif n_mensagem == 9: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de estruturas de extravasão deve ser um número inteiro.")
    elif n_mensagem == 10: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número de estruturas de extravasão deve ser maior que zero.")
    elif n_mensagem == 11: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas para o vertedor.\n\nExemplo: 'VERTEDOR; 1.5; 20; 15; 22;'\n\nLembre-se de terminar a linha com ponto-e-vírgula.")
    elif n_mensagem == 12: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O coeficiente de descarga do vertedor deve ser um número decimal.")
    elif n_mensagem == 13: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A largura de soleira do vertedor deve ser um número decimal.")
    elif n_mensagem == 14: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota de soleira do vertedor deve ser um número decimal.")
    elif n_mensagem == 15: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota máxima do vertedor deve ser um número decimal.")
    elif n_mensagem == 16: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O coeficiente de descarga do vertedor deve ser maior que zero.")
    elif n_mensagem == 17: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A largura de soleira do vertedor deve ser maior que zero.")
    elif n_mensagem == 18: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota de soleira do vertedor deve ser maior que zero.")
    elif n_mensagem == 19: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota máxima do vertedor deve ser maior que zero.")
    elif n_mensagem == 20: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas para o orifício.\n\nExemplo: 'ORIFICIO; 0.5; 1.0; 5;'\n\nLembre-se de terminar a linha com ponto-e-vírgula.")
    elif n_mensagem == 21: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O coeficiente de descarga do orifício deve ser um número decimal.")
    elif n_mensagem == 22: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A altura/diâmetro do orifício deve ser um número decimal.")
    elif n_mensagem == 23: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota do centro do orifício deve ser um número decimal.")
    elif n_mensagem == 24: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O coeficiente de descarga do orifício deve ser maior que zero.")
    elif n_mensagem == 25: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A altura/diâmetro do orifício deve ser maior que zero.")
    elif n_mensagem == 26: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A cota do centro do orifício deve ser maior que zero.")
    elif n_mensagem == 27: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Estrutura de extravasão '%s' desconhecida.\n\nUtilize: 'VERTEDOR' ou 'ORIFICIO'." %(detalhes))
    elif n_mensagem == 28: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A extensão do arquivo fornecido para a curva cota-volume deve ser txt.")
    elif n_mensagem == 29: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O arquivo fornecido para a curva cota-volume não foi localizado.")
#-----------------------------------------------------------------------
def mensagensIntegridadeMKC(n_mensagem, linhas_lidas, nop, hidro_numero, nop_declaradas):
    """Tem as mensagens de erros do arquivo Leitura na parte de entrada de informacoes MKC"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas na operação %d (Muskingum-Cunge).\n\nExemplo: 'MKC; 1; 400; 20.0; 25.0; 0.040;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nop))
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número da operação que originará o hidrograma de entrada desta operação (%d) deve ser inteiro."%(nop))
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número da operação que originará o hidrograma de entrada desta operação (%d) deve ser maior que zero."%(nop))
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Não é possível utilizar o hidrograma oriundo da operação %d na operação %d pois há apenas %d operações hidrológicas declaradas nas informações gerais." %(hidro_numero,nop,nop_declaradas))
    elif n_mensagem == 5: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A diferença de cota do canal deve ser um número decimal.")
    elif n_mensagem == 6: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O comprimento do canal deve ser um número decimal.")
    elif n_mensagem == 7: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A largura do canal deve ser um número decimal.")
    elif n_mensagem == 8: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O coeficiente de rugosidade médio deve ser um número decimal.")
    elif n_mensagem == 9: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A diferença de cota do canal deve ser maior que zero.")
    elif n_mensagem == 10: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O comprimento do canal deve ser maior que zero.")
    elif n_mensagem == 11: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A largura do canal deve ser maior que zero.")
    elif n_mensagem == 12: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O coeficiente de rugosidade médio deve ser maior que zero.")
#-----------------------------------------------------------------------
def mensagensIntegridadeJUN(n_mensagem, linhas_lidas, nop, hidro_numero, nop_declaradas):
    """Tem as mensagens de erros do arquivo Leitura na parte de entrada de informacoes MKC"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas na operação %d (Junção).\n\nExemplo: 'JUN; 3; 4;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nop))
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Os números das operações que originarão os hidrogramas de entrada desta operação (%d) devem ser inteiros."%(nop))
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Os números das operações que originarão os hidrogramas de entrada desta operação (%d) devem ser maiores que zero."%(nop))
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Não é possível utilizar o hidrograma oriundo da operação %d na operação %d pois há apenas %d operações hidrológicas declaradas nas informações gerais." %(hidro_numero,nop,nop_declaradas))
#-----------------------------------------------------------------------
def mensagensIntegridadeHIDRO(n_mensagem, linhas_lidas, nop, nop_declaradas, detalhes):
    """Tem as mensagens de erro do arquivo Leitura na parte de entrada de hidrogramas observados"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas na operação %d (leitura de hidrograma).\n\nExemplo: 'HIDROGRAMA; C:/.../.../Arquivo_entrada.txt;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nop))
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"A extensão do arquivo fornecido para o hidrograma de entrada para a operação de leitura de hidrograma deve ser txt.")
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Não foi possível encontrar o arquivo de entrada para a operação %d (leitura de hidrograma). Forneça um diretório válido.\n\nDiretório fornecido: '%s'"%(detalhes))
#-----------------------------------------------------------------------
def mensagensIntegridadeDERIVACAO(n_mensagem, linhas_lidas, nop, hidro_numero, nop_declaradas, detalhes):
    """Tem as mensagens de erro do arquivo Leitura na parte de entrada de derivacoes"""
    if n_mensagem == 1: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas na operação %d (Derivação).\n\nExemplo: 'DERIVACAO; 1; CONSTANTE; 3.5; PRINCIPAL;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nop))
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número da operação que originará o hidrograma de entrada desta operação (%d) deve ser inteiro."%(nop))
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O número da operação que originará o hidrograma de entrada desta operação (%d) deve ser maior que zero."%(nop))
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Não é possível utilizar o hidrograma oriundo da operação %d na operação %d pois há apenas %d operações hidrológicas declaradas nas informações gerais." %(hidro_numero,nop,nop_declaradas))
    elif n_mensagem == 5: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Opção de derivação '%s' desconhecida (operação: %d).\n\nOpções disponíveis: 'CONSTANTE;', 'PORCENTAGEM;' ou 'HIDROGRAMA;'." %(detalhes, nop))
    elif n_mensagem == 6: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor de vazão/porcentagem/hidrograma de derivação deve ser um número real.")
    elif n_mensagem == 7: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O valor de vazão/porcentagem/hidrograma de derivação deve ser maior que zero.")
    elif n_mensagem == 8: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Opção de saída '%s' desconhecida (operação: %d). \n\nOpções disponíveis: 'PRINCIPAL;' ou 'DERIVADO;'." %(detalhes, nop))
#-----------------------------------------------------------------------
def mensagensIntegridadeArquivosObservados(n_mensagem, linha, nch, nop, numero_intervalos_tempo_chuva, numero_intervalos_tempo):
    """"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo fornecido","O arquivo fornecido (posto de chuva %d) não possui %d linhas (que é o número de intervalos de tempo com chuva da simulação)." %(nch, numero_intervalos_tempo_chuva))
    elif n_mensagem == 2: messagebox.showerror("Erro no arquivo fornecido","Erro na linha %d.\n\nO arquivo fornecido (posto de chuva %d) não obedece os padrões utilizados pelo programa.\n\nDica: As linhas devem possuir o seguinte padrão: 'valor do dado;'." %(linha, nch))
    elif n_mensagem == 3: messagebox.showerror("Erro no arquivo fornecido","O arquivo fornecido para o hidrograma de entrada (operação %d) não possui %d linhas (que é o número de intervalos de tempo de simulação)." %(nop, numero_intervalos_tempo))
    elif n_mensagem == 4: messagebox.showerror("Erro no arquivo fornecido","Erro na linha %d.\n\nO arquivo fornecido (operação %d) para o hidrograma de entrada não obedece os padrões utilizados pelo programa.\n\nDica: As linhas devem possuir o seguinte padrão: 'valor do dado;'." %(linha, nop))
    elif n_mensagem == 5: messagebox.showerror("Erro no arquivo fornecido","O arquivo fornecido para a curva cota-volume (operação %d) deve conter pelo menos dois pontos sendo o primeiro par ordenado (linha) deve ser 0;0; obrigatoriamente." %(nop))
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo fornecido","Erro na linha %d.\n\nO arquivo fornecido (operação %d) para a curva cota-volume não obedece os padrões utilizados pelo programa.\n\nDica: As linhas devem possuir o seguinte padrão: 'cota; volume;'."%(linha, nop))
#-----------------------------------------------------------------------
def mensagensIntegridadeArquivos(n_mensagem, linhas_lidas, nch, nop, nch_declaradas, nop_declaradas, detalhes):
    """Tem as mensagens de erros do arquivo Leitura"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo de entrada", "Não foi detectado a palavra 'INICIO' no arquivo de entrada.\n\nCertifique-se de que a palavra esteja presente no arquivo de entrada para que o modelo inicie o processo de leitura do mesmo.")
    elif n_mensagem == 2: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Informações incorretas para a operação %d.\n\nExemplo:'OPERACAO; 1;'\n\nLembre-se de terminar a linha com ponto-e-vírgula." %(nop))
    elif n_mensagem == 3: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Tipo de operação '%s' não definida.\n\nTipos definidos: 'PQ', 'PULS', 'MKC' ou 'JUN'." %(detalhes))
    elif n_mensagem == 4: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Número da operação hidrológica incorreto.\nNúmero esperado: %d." %(nop))
    elif n_mensagem == 5: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"Não deixe mais de uma linha em branco no final do arquivo de entrada.")
    elif n_mensagem == 6: messagebox.showerror("Erro na linha: %d" %(linhas_lidas),"O comando '%s' não esta definido no programa.\n\nComandos definidos: 'INICIO', 'CHUVA' e 'OPERACAO'." %(detalhes))
    elif n_mensagem == 7: messagebox.showerror("Erro no arquivo de entrada","Foram declaradas %d posto(s) de chuva nas informações gerais, porem há informação de %d posto(s) de chuva no arquivo de entrada.\n\nRevise o arquivo de entrada." %(nch_declaradas, nch))
    elif n_mensagem == 8: messagebox.showerror("Erro no arquivo de entrada","Foram declaradas %d operações nas informações gerais, porem há informação de %d operação(ões) no arquivo de entrada.\n\nRevise o arquivo de entrada." %(nop_declaradas, nop))
    elif n_mensagem == 9: messagebox.showerror("Erro no arquivo de entrada","A operação %d é saída de duas ou mais operações (o hidrograma de saída de uma operação hidrológica pode somente ser usado como entrada de uma única outra operação hidrológica).\n\nRevise o arquivo de entrada." %(nop))
    elif n_mensagem == 10: messagebox.showerror("Erro no arquivo de entrada","A operação %d utiliza o seu próprio hidrograma de saída como hidrograma de entrada.\n\nRevise o arquivo de entrada."%(nop))
    elif n_mensagem == 11: messagebox.showerror("Erro no arquivo de entrada","Não é possível determinar a ordem de execução da operação hidrológica: %s.\n\nRevise todos os números das operações de entrada." %(detalhes))
    elif n_mensagem == 12: messagebox.showerror("Erro no arquivo de entrada","O número de postos de chuva e/ou operações declaradas é insuficiente para ler todo o conteúdo escrito no arquivo de entrada.\n\nRevise os números de postos de chuva e operações declaradas.")
#-----------------------------------------------------------------------
def mensagensManejoArquivos(n_mensagem, nome_arquivo, extensao):
    """Tem as mensagens referentes ao manejo (criacao e exclusao) de arquivos"""
    if n_mensagem == 1: messagebox.showerror("Erro: Permissão insuficiente.", "Ocorreu um erro ao tentar deletar o arquivo de saída antigo (%s.%s).\n\nCertifique-se de que o mesmo não esteja sendo usado por outro processo.\n\nClique em Ok para finalizar o modelo."%(nome_arquivo, extensao))
#-----------------------------------------------------------------------
def mensagensIntegridadePlotagens(n_mensagem, detalhes):
    """Tem as mensagens referentes aos erros dos arquivos de saida de forma generica."""
    if n_mensagem == 1: messagebox.showerror("Erro", "Formato de arquivo inválido!\nSelecione um arquivo no formato '*.ohy'.")
    elif n_mensagem == 2: messagebox.showinfo("Aviso", "Nenhum arquivo selecionado. Tente novamente.")
    elif n_mensagem == 3: messagebox.showinfo("Aviso", "Nenhum dos arquivos da pasta selecionada possui o formato adequado.\n\nNenhuma pasta selecionada. Tente novamente.")
    elif n_mensagem == 4: messagebox.showerror("Erro", "O formato do arquivo '%s' é incompatível.\nSelecione um arquivo no formato '*.ohy'." %(detalhes))
    elif n_mensagem == 5: messagebox.showinfo("Aviso", "Nenhuma pasta selecionada. Tente novamente.")
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo de entrada", "Não foi possível identificar a operação do arquivo de saída '%s'."%(detalhes))
#-----------------------------------------------------------------------
def mensagensIntegridadePlotagensPQ(n_mensagem, linha, coluna, arquivo):
    """Tem as mensagens referentes aos erros dos arquivos de saida PQ"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo de entrada", "O número de simulações chuva-vazão deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 2: messagebox.showerror("Erro no arquivo de entrada","O número de simulações chuva-vazão deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 3: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 4: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 5: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo com chuva deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo com chuva deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 7: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 8: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 9: messagebox.showerror("Erro no arquivo de entrada","O número do posto de chuva utilizado na operação de chuva-vazão deve ser inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 10: messagebox.showerror("Erro no arquivo de entrada","O número do posto de chuva utilizado na operação de chuva-vazão deve maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 11: messagebox.showerror("Erro no arquivo de entrada","Os valores de chuva ordenada devem ser no formato float. Erro na linha %d coluna %d.\n\nArquivo:'%s'"%(linha,coluna,arquivo))
    elif n_mensagem == 12: messagebox.showerror("Erro no arquivo de entrada","Os valores de chuva ordenada devem ser maior que zero. Erro na linha %d coluna %d.\n\nArquivo:'%s'"%(linha,coluna,arquivo))
    elif n_mensagem == 13: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma devem ser no formato float. Erro na linha %d coluna %d.\n\nArquivo:'%s'"%(linha,coluna,arquivo))
    elif n_mensagem == 14: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma devem ser maior que zero. Erro na linha %d coluna %d.\n\nArquivo:'%s'"%(linha,coluna,arquivo))
#-----------------------------------------------------------------------
def mensagensIntegridadePlotagensPULS(n_mensagem, linha, arquivo):
    """Tem as mensagens referentes aos erros dos arquivos de saida PULS"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo de entrada", "O número de simulações de Puls deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 2: messagebox.showerror("Erro no arquivo de entrada","O número de simulações de Puls deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 3: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 4: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 5: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 7: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser no formato float. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 8: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser maior que zero. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 9: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de saída devem ser no formato float. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 10: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de saída devem ser maior que zero. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
#-----------------------------------------------------------------------
def mensagensIntegridadePlotagensMKC(n_mensagem, linha, arquivo):
    """Tem as mensagens referentes aos erros dos arquivos de saida MKC"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo de entrada", "O número de simulações de Muskingum-Cunge deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 2: messagebox.showerror("Erro no arquivo de entrada","O número de simulações de Muskingum-Cunge deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 3: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 4: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 5: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 7: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser no formato float. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 8: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser maior que zero. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 9: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de saída devem ser no formato float. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 10: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de saída devem ser maior que zero. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
#-----------------------------------------------------------------------
def mensagensIntegridadePlotagensJUN(n_mensagem, linha, coluna, arquivo):
    """Tem as mensagens referentes aos erros dos arquivos de saida JUN"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo de entrada", "O número de simulações de Junção deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 2: messagebox.showerror("Erro no arquivo de entrada","O número de simulações de Junção deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 3: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 4: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 5: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 7: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma devem ser no formato float. Erro no dt %d coluna %d.\n\nArquivo:'%s'"%(linha, coluna,arquivo))
    elif n_mensagem == 8: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma devem ser maior que zero. Erro no dt %d coluna %d.\n\nArquivo:'%s'"%(linha, coluna,arquivo))
#-----------------------------------------------------------------------
def mensagensIntegridadePlotagensHIDRO(n_mensagem, linha, arquivo):
    """Tem as mensagens referentes aos erros dos arquivos de saida leituras de Hidrogramas"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo de entrada", "O número de leituras de hidrogramas deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 2: messagebox.showerror("Erro no arquivo de entrada","O número de leituras de hidrogramas deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 3: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 4: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 5: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 7: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser no formato float. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 8: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser maior que zero. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
#-----------------------------------------------------------------------
def mensagensIntegridadePlotagensDERIVACAO(n_mensagem, linha, arquivo):
    """Tem as mensagens referentes aos erros dos arquivos de saida leituras de Hidrogramas"""
    if n_mensagem == 1: messagebox.showerror("Erro no arquivo de entrada", "O número de derivações deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 2: messagebox.showerror("Erro no arquivo de entrada","O número de derivações deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 3: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 4: messagebox.showerror("Erro no arquivo de entrada","O número de intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 5: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser um número inteiro.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 6: messagebox.showerror("Erro no arquivo de entrada","A duração do intervalos de tempo deve ser maior que zero.\n\nArquivo:'%s'"%(arquivo))
    elif n_mensagem == 7: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser no formato float. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 8: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de entrada devem ser maior que zero. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 9: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de saída devem ser no formato float. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
    elif n_mensagem == 10: messagebox.showerror("Erro no arquivo de entrada","Os valores do hidrograma de saída devem ser maior que zero. Erro no dt %d.\n\nArquivo:'%s'"%(linha,arquivo))
#-----------------------------------------------------------------------