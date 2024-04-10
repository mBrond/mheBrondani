# -*- coding: utf-8 -*-

#   Neste arquivo encontram-se o codigo responsavel pelo "passo-a-passo" que o modelo deve seguir
# para executar um arquivo de entrada; Ou seja, e' onde esta' o codigo do que deve ser
# executado, sendo assim, aqui encontram-se todas as variaveis da simulacao.


################## GLOSSARIO ############################################################################
#                                                                                                       #
#   nInt = numero de intervalos de tempo                                                                #
#   DT = duracao do intervalo de tempo (segundos)                                                       #
#   nCh = numero de chuvas                                                                              #
#   nIntCh = numeros de intervalos de tempo de chuva                                                    #
#   nOp = numero de operacoes hidrologicas                                                              #
#   entrOp = numero da operacao de entrada de cada operacao hidrologica (NAO e' indice!)                #
#   cdgOH = codigos operacoes hidrologicas 1-PQ, 2-PUKS, 3-MKC, 4-JUN, 5-Leitura, 6-Derivacao           #
#   nomesOp = nome da operacao, vai no grafico se ativado                                               #
#   limIDF = limitacao da intensidade de chuva para as chuvas calculadas a partir de IDF (minutos)      #
#   tpIDF = tipo da idf                                                                                 #
#   posPico = posicao do pico de chuva                                                                  #
#   dirCh = None ou diretorio chuva observada                                                           #
#   nChuPQ = INDICE da chuva usada na operacao PQ                                                       #
#   difCota = diferenca de cota - m (kirpich)                                                           #
#   compCanal = comprimento canal MKC                                                                   #
#   CCV = curva cota-volume                                                                             #
#   estruPULS = estruturas da operacao de PULS                                                          #
#   cotaIniPULS = cota inicial do reservatorio PULS                                                     #
#   byPasses = valores de vazao escoada pelo by-pass dos reservatorios off-line                         #
#   largCanal = largura do canal MKC                                                                    #
#   nMann = coeficiente n de manning MKC                                                                #
#   dirHidro = None ou DIRETORIO hidrograma de entrada de leitura de hidrogramas observados             #
#   tpDeriv = Tipo de derivacao: 1-constante, 2-porcentagem, 3-hidrograma                               #
#   vlDeriv = Valor das derivacoes: m³/s ou % ou numero hidrograma                                      #
#   sdDeriv = Tipo de saida da derivacao: 1-principal, ou 2-derivado                                    #
#                                                                                                       #
#########################################################################################################


#   Import das bibliotecas customizadas
from OperacaoPQ import gerarVariaveisSaidaPQ, calcularOperacaoPQ, escreverSaidaPQ, plotarPQ
from OperacaoPULS import gerarVariaveisSaidaPULS, preparacaoPULS, calcularOperacaoPULS, escreverSaidaPULS, plotarPULS
from OperacaoMKC import gerarVariaveisSaidaMKC, preparacaoMKC, calcularOperacaoMKC, escreverSaidaMKC, plotarMKC
from OperacaoJUNCAO import gerarVariaveisSaidaJUNCAO, preparacaoJUNCAO, calcularOperacaoJUNCAO, escreverSaidaJUNCAO, plotarJUN
from OperacaoHIDROGRAMA import gerarVariaveisSaidaHIDROGRAMA, lerOperacaoHIDROGRAMA, escreverSaidaHIDROGRAMA, plotarHIDROGRAMA
from OperacaoDERIVACAO import gerarVariaveisSaidaDERIVACAO, preparacaoDERIVACAO, calcularOperacaoDERIVACAO, escreverSaidaDERIVACAO, plotarDERIVACAO
from Leitura import determinarDiretorios, lerArquivoEntrada, checarLogicaCircular
from Leitura import determinarDiretoriosPlotagens, identificarCodigoArquivoSaida
from Leitura import lerArquivoSaidaPQ, lerArquivoSaidaPULS, lerArquivoSaidaMKC, lerArquivoSaidaJUN, lerArquivoSaidaHIDRO, lerArquivoSaidaDERIVACAO
from Utilidades import atualizarBarraProgresso, organizarIndices, corrigirCaracteres, criarPasta


#----------------------------------------------------------------------
def iniciarProcessamento(isFolder, diretorio_do_software):
    """Funcao "controle". Gerencia leitura e inicia a simulacao."""
    #   Gerar as variaveis necessarias para iniciar o processamento
    diretorios_arquivos_entrada, diretorio_saida = determinarDiretorios(isFolder, diretorio_do_software)
    
    #   Ver se algo foi selecionado
    if not diretorios_arquivos_entrada[0] == None:
        #   Loop de arquivos
        for indice_arquivo, diretorio_arquivo in enumerate(diretorios_arquivos_entrada):
            #   Ver se e' um diretorio de arquivo mesmo
            if not diretorio_arquivo == None:
                #   Selecionar ultimo nome
                nome_arquivo = diretorio_arquivo.split("/".encode())[-1]
                #   Separar o nome do arquivo
                nome_arquivo = nome_arquivo.split(".".encode())[0]
                #   Avisar usuario
                print ("\n\t----------------------------------------------------\n\tArquivo (%d / %d)\n\tNome: %s." %((indice_arquivo+1), (len(diretorios_arquivos_entrada)), (nome_arquivo.decode())))
                #   Mando rodar a simulacao do arquivo
                iniciarSimulacaoArquivo(diretorio_arquivo, diretorio_saida, nome_arquivo)
                #   Avisar usuario
                print ("\tArquivo %s executado com sucesso!\n\t----------------------------------------------------\n" %(nome_arquivo.decode()))
#----------------------------------------------------------------------
def iniciarSimulacaoArquivo(diretorio_arquivo, diretorio_saida, nome_arquivo):
    """"""
    #   Pegar as variaveis de entrada... sao muitas, eu sei.... ¯\_(ツ)_/¯... eu abreveiei o maximo que pude..
    nInt, DT, nCh, nIntCh, nOp, entrOp, cdgOH, nomesOp, idfA, idfB, idfC, idfD, limIDF, tpIDF, posPico, TR, dirCh, CN, area, TC, nChuPQ, difCota, compCanal, CCV, estruPULS, cotaIniPULS, byPasses, largCanal, nMann, dirHidro, tpDeriv, vlDeriv, sdDeriv = lerArquivoEntrada(diretorio_arquivo)
    
    #   Rodar a funcao de organiza a ordem de execucao, a variavel integridade nao e' usada para nada apenas evita bug
    integridade, ordem_execucao = checarLogicaCircular(entrOp)
    
    #   Rodar a funcao que organizar os indices das matrizes de resultados baseadas na ordem de execucao
    indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO = organizarIndices(ordem_execucao, cdgOH)
    
    #   Declarar as variaveis de saida PQ
    hidSaiPQ, chuOrdPQ, chuEfePQ = gerarVariaveisSaidaPQ(cdgOH, nInt, nChuPQ, nCh, nIntCh, DT, idfA, idfB, idfC, idfD, limIDF, posPico, TR, dirCh)
    
    #   Declarar as variaveis de saida PULS
    hidSaiPULS, cotasMontSaiPULS = gerarVariaveisSaidaPULS(cdgOH, nInt)

    #   Declarar as variaveis de saida MKC
    hidSaiMKC = gerarVariaveisSaidaMKC(cdgOH, nInt)
    
    #   Declarar as variaveis de saida JUNCAO
    hidSaiJUN = gerarVariaveisSaidaJUNCAO(cdgOH, nInt)
    
    #   Declarar as variaveis de saida de leitura de hidrogramas
    hidSaiHIDRO = gerarVariaveisSaidaHIDROGRAMA(cdgOH, nInt)
    
    #   Declarar as variaveis de saida das derivacoes
    hidSaiDERIVACAO = gerarVariaveisSaidaDERIVACAO(cdgOH, nInt)
    
    #   Avisar usuario
    print ("\n\tCalculando operacoes hidrologicas.")
    
    #   Inicializar barra
    atualizarBarraProgresso(0, nOp)
    
    #   Loop para rodar operacoes
    for ii, indOp in enumerate(ordem_execucao):
        
        #   Para PQ
        if cdgOH[indOp] == 1:
            #   Determinar indices
            indiceSaida = indSaiPQ.index(indOp) # Exclusivo para a variavel de saida; len(indSaiX) <= nOp
            indiceChuva = nChuPQ[indOp] # Por nChuPQ ter len == nOp, a determina do indice e' diferente
            #   Calcular o hidrograma de saida 
            hidSaiPQ[indiceSaida], chuEfePQ[indiceSaida] = calcularOperacaoPQ(nInt, DT, nIntCh, CN[indOp], area[indOp], TC[indOp], chuOrdPQ[indiceChuva])
        
        #   Para Puls
        elif cdgOH[indOp] == 2:
            #   Determinar indices
            indiceSaida = indSaiPULS.index(indOp) # Exclusivo para a variavel de saida; len(indSaiX) <= nOp
            #   Pegar o hidrograma de entrada
            hidAux = preparacaoPULS(nInt, entrOp[indOp], indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO)
            #   Calcule a operacao de Puls
            hidSaiPULS[indiceSaida], cotasMontSaiPULS[indiceSaida] = calcularOperacaoPULS(hidAux, byPasses[indOp], cotaIniPULS[indOp], estruPULS[indOp], CCV[indOp], DT, nInt)
        
        #   Para MKC
        elif cdgOH[indOp] == 3:
            #   Determinar indices
            indiceSaida = indSaiMKC.index(indOp) # Exclusivo para a variavel de saida; len(indSaiX) <= nOp
            #   Pegar o hidrograma de entrada
            hidAux = preparacaoMKC(nInt, entrOp[indOp], indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO)
            #   Calcule a operacao de MKC
            hidSaiMKC[indiceSaida] = calcularOperacaoMKC(hidAux, DT, nInt, difCota[indOp], compCanal[indOp], largCanal[indOp], nMann[indOp])
        
        #   Para JUNCAO
        elif cdgOH[indOp] == 4:
            #   Determinar indices
            indiceSaida = indSaiJUN.index(indOp) # Exclusivo para a variavel de saida; len(indSaiX) <= nOp
            #   Pegar os hidrogramas de entrada
            hidAux = preparacaoJUNCAO(nInt, entrOp[indOp], indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO)
            #   Calcular a operacao de JUNCAO
            hidSaiJUN[indiceSaida] = calcularOperacaoJUNCAO(hidAux, nInt)
        
        #   Para leitura de hidrogramas
        elif cdgOH[indOp] == 5:
            #   Determinar indices
            indiceSaida = indSaiHIDRO.index(indOp) # Exclusivo para a variavel de saida; len(indSaiX) <= nOp
            #   Ler a operacao de leitura de hidrogramas
            hidSaiHIDRO[indiceSaida] = lerOperacaoHIDROGRAMA(nInt, dirHidro[indOp])
        
        #   Para Derivacoes
        elif cdgOH[indOp] == 6:
            #   Determinar indices
            indiceSaida = indSaiDERIVACAO.index(indOp) # Exclusivo para a variavel de saida; len(indSaiX) <= nOp
            #   Pegar os hidrogramas de entrada
            hidAux, hidAux2 = preparacaoDERIVACAO(nInt, entrOp[indOp], indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO, tpDeriv[indOp], vlDeriv[indOp])
            #   Calcular a operacao de DERIVACAO
            hidSaiDERIVACAO[indiceSaida] = calcularOperacaoDERIVACAO(nInt, hidAux, tpDeriv[indOp], vlDeriv[indOp], sdDeriv[indOp], hidAux2)
        
        #   Barra de progresso
        atualizarBarraProgresso(ii+1, nOp)
        
    #   Loop para escrever os arquivos de saida
    #   Avisar usuario
    print ("\n\tEscrevendo o(s) arquivo(s) de saida.\n")
    #   Para PQ (propagacao chuva-vazao)
    if 1 in cdgOH:
        #   Gerar arquivo de saida...
        escreverSaidaPQ(nInt, DT, nIntCh, nOp, cdgOH, CN, area, TC, nChuPQ, chuOrdPQ, hidSaiPQ, chuEfePQ, diretorio_saida, nome_arquivo, nomesOp)
    
    #   Para PULS (propagacao de reservatorios de PULS)
    if 2 in cdgOH:
        #   Gerar arquivo de saida...
        escreverSaidaPULS(nInt, DT, nOp, cdgOH, entrOp, indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, cotasMontSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO, diretorio_saida, nome_arquivo, nomesOp)
    
    #   Para MKC (propagacao de canais Muskingum-Cunge)
    if 3 in cdgOH:
        #   Gerar arquivo de saida...
        escreverSaidaMKC(nInt, DT, nOp, cdgOH, entrOp, indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO, diretorio_saida, nome_arquivo, nomesOp)
    
    #   Para JUN (Juncao)
    if 4 in cdgOH:
        #   Gerar arquivo de saida...
        escreverSaidaJUNCAO(nInt, DT, nOp, cdgOH, entrOp, indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO, diretorio_saida, nome_arquivo, nomesOp)
    
    #   Para leitura de hidrogramas
    if 5 in cdgOH:
        #   Gerar arquivo de saida...
        escreverSaidaHIDROGRAMA(nInt, DT, nOp, cdgOH, dirHidro, entrOp, indSaiHIDRO, hidSaiHIDRO, diretorio_saida, nome_arquivo, nomesOp)
    
    #   Para derivacao
    if 6 in cdgOH:
        #   Gerar arquivo de saida...
        escreverSaidaDERIVACAO(nInt, DT, nOp, cdgOH, entrOp, indSaiPQ, indSaiPULS, indSaiMKC, indSaiJUN, indSaiHIDRO, indSaiDERIVACAO, hidSaiPQ, hidSaiPULS, hidSaiMKC, hidSaiJUN, hidSaiHIDRO, hidSaiDERIVACAO, tpDeriv, vlDeriv, sdDeriv, diretorio_saida, nome_arquivo, nomesOp)
#----------------------------------------------------------------------
def iniciarGraficos(isFolder, diretorio_do_software, resolucao):
    """Funcao "controle". Gerencia leitura e inicia a plotagem dos graficos."""
    #   Gerar as variaveis necessarias para iniciar o processamento
    diretorios_arquivos_entrada, diretorio_saida = determinarDiretoriosPlotagens(isFolder, diretorio_do_software)
    
    #   Ver se algo foi selecionado
    if not diretorios_arquivos_entrada[0] == None:
        #   Loop de arquivos
        for indice_arquivo, diretorio_arquivo in enumerate(diretorios_arquivos_entrada):
            #   Ver se e' um diretorio de arquivo mesmo
            if not diretorio_arquivo == None:
                #   Selecionar ultimo nome
                nome_arquivo = diretorio_arquivo.split("/".encode())[-1]
                #   Separar o nome do arquivo
                nome_arquivo = nome_arquivo.split(".".encode())[0]
                #   Avisar usuario
                print ("\n\t----------------------------------------------------\n\tPlotando arquivo (%d / %d)\n\tNome: %s." %((indice_arquivo+1), (len(diretorios_arquivos_entrada)), (nome_arquivo.decode())))
                #   Mando rodar a simulacao do arquivo
                iniciarPlotagemArquivo(diretorio_arquivo, diretorio_saida[indice_arquivo], resolucao)
                #   Avisar usuario
                print ("\tArquivo %s plotado com sucesso!\n\t----------------------------------------------------\n" %(nome_arquivo.decode()))
#----------------------------------------------------------------------
def iniciarPlotagemArquivo(diretorio_arquivo, diretorio_saida, resolucao):
    """"""
    #   Comece identificando o codigo do arquivo em questao
    codigo_arquivo = identificarCodigoArquivoSaida(diretorio_arquivo)
    
    #   Eu SEI que codigo_arquivo sera' > 0, essa verificacao ja' foi feita
    
    #   Se for PQ
    if codigo_arquivo == 1:
        hidrogramas, chuvasOrd, chuvasEfe, indChuvas, DT, titulos = lerArquivoSaidaPQ(diretorio_arquivo)
        numPlots = len(hidrogramas)
    
    #   Se for PULS
    elif codigo_arquivo == 2:
        hidrogramas_entrada, hidrogramas_saida, DT, titulos = lerArquivoSaidaPULS(diretorio_arquivo)
        numPlots = len(hidrogramas_entrada)
    
    #   Se for MKC
    elif codigo_arquivo == 3:
        hidrogramas_entrada, hidrogramas_saida, DT, titulos = lerArquivoSaidaMKC(diretorio_arquivo)
        numPlots = len(hidrogramas_entrada)
    
    #   Se for JUN
    elif codigo_arquivo == 4:
        hidrogramas, DT, titulos = lerArquivoSaidaJUN(diretorio_arquivo)
        numPlots = len(hidrogramas)
    
    #   Se for leitura
    elif codigo_arquivo == 5:
        hidrogramas_entrada, DT, titulos = lerArquivoSaidaHIDRO(diretorio_arquivo)
        numPlots = len(hidrogramas_entrada)
    
    #   Se for derivacao
    elif codigo_arquivo == 6:
        hidrogramas_entrada, hidrogramas_saida, DT, titulos = lerArquivoSaidaDERIVACAO(diretorio_arquivo)
        numPlots = len(hidrogramas_entrada)
    
    #   Independente do codigo, terei que SEMPRE corrigir os titulos
    for ii, titulo in enumerate(titulos):
        titulos[ii] = corrigirCaracteres(titulo)
        
    #   Vou criar a pasta de saida onde salvar-se-ao os graficos
    criarPasta(diretorio_saida)
    
    #   PLOTAR OS PQs
    if codigo_arquivo == 1:
        #   Inicializar barra
        atualizarBarraProgresso(0, numPlots)
        #   Plotar 1 grafico para cada operacao/hidrograma
        for ii, hidrograma in enumerate(hidrogramas):
            #   Mandar os argumentos necessarios para a outra funcao
            plotarPQ(hidrograma, chuvasOrd[indChuvas[ii]], chuvasEfe[ii], DT, diretorio_saida.decode(), titulos[ii], (ii+1), resolucao)
            #   Barra de progresso
            atualizarBarraProgresso(ii+1, numPlots)
    
    #   PLOTAR OS PULS
    elif codigo_arquivo == 2:
        #   Inicializar barra
        atualizarBarraProgresso(0, numPlots)
        #   Plotar 1 grafico para cada operacao/hidrograma
        for ii, hidrograma in enumerate(hidrogramas_entrada):
            #   Mandar os argumentos necessarios para a outra funcao
            plotarPULS(hidrograma, hidrogramas_saida[ii], DT, diretorio_saida.decode(), titulos[ii], (ii+1), resolucao)
            #   Barra de progresso
            atualizarBarraProgresso(ii+1, numPlots)
    
    #   PLOTAR OS MKC
    elif codigo_arquivo == 3:
        #   Inicializar barra
        atualizarBarraProgresso(0, numPlots)
        #   Plotar 1 grafico para cada operacao/hidrograma
        for ii, hidrograma in enumerate(hidrogramas_entrada):
            #   Mandar os argumentos necessarios para a outra funcao
            plotarMKC(hidrograma, hidrogramas_saida[ii], DT, diretorio_saida.decode(), titulos[ii], (ii+1), resolucao)            
            #   Barra de progresso
            atualizarBarraProgresso(ii+1, numPlots)
    
    #   PLOTAR OS JUN
    elif codigo_arquivo == 4:
        #   Inicializar barra
        atualizarBarraProgresso(0, numPlots)
        #   Plotar 1 grafico para cada operacao
        for ii, hidrogramas_jun in enumerate(hidrogramas):
            #   Mandar os argumentos necessarios para a outra funcao
            plotarJUN(hidrogramas_jun[0:-1], hidrogramas_jun[-1], DT, diretorio_saida.decode(), titulos[ii], (ii+1), resolucao)
            #   Barra de progresso
            atualizarBarraProgresso(ii+1, numPlots)
            
    #   PLOTAR AS LEITURAS
    elif codigo_arquivo == 5:
        #   Inicializar barra
        atualizarBarraProgresso(0, numPlots)
        #   Plotar 1 grafico para cada operacao/hidrograma
        for ii, hidrograma in enumerate(hidrogramas_entrada):
            #   Mandar os argumentos necessarios para a outra funcao
            plotarHIDROGRAMA(hidrograma, DT, diretorio_saida.decode(), titulos[ii], (ii+1), resolucao)            
            #   Barra de progresso
            atualizarBarraProgresso(ii+1, numPlots)
            
    #   PLOTAR AS DERIVACOES
    elif codigo_arquivo == 6:
        #   Inicializar barra
        atualizarBarraProgresso(0, numPlots)
        #   Plotar 1 grafico para cada operacao/hidrograma
        for ii, hidrograma in enumerate(hidrogramas_entrada):
            #   Mandar os argumentos necessarios para a outra funcao
            plotarDERIVACAO(hidrograma, hidrogramas_saida[ii], DT, diretorio_saida.decode(), titulos[ii], (ii+1), resolucao)            
            #   Barra de progresso
            atualizarBarraProgresso(ii+1, numPlots)
#----------------------------------------------------------------------