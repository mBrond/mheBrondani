# -*- coding: utf-8 -*-


#   Import das bibliotecas Python
from os import path
from numpy import array, float64
#   Import das bibliotecas customizadas
from Hydrolib import aplicar_MuskingumCunge
from Hydrolib import plotar_Hidrogramas_MKC
from Leitura import lerSerieObservada


#----------------------------------------------------------------------
def gerarVariaveisSaidaMKC(codigo_operacoes_hidrologicas, numero_intervalos_tempo):
    """Cria a matriz de saida para calcular as operacoes MKC"""
    #   Contar
    numero_operacoes_mkc = codigo_operacoes_hidrologicas.count(3)
    
    #   Variavel que armazena os hidrogramas gerados
    hidrogramas_saida_mkc = array([[0.0 for i in range(numero_intervalos_tempo)] for y in range(numero_operacoes_mkc)], float64)

    #   Retorne
    return hidrogramas_saida_mkc
#----------------------------------------------------------------------------------
def preparacaoMKC(numero_intervalos_tempo, entrada_operacao, indices_pq, indices_puls, indices_mkc, indices_jun, indices_hidro, indices_derivacao, hidrogramas_saida_pq, hidrogramas_saida_puls, hidrogramas_saida_mkc, hidrogramas_saida_jun, hidrogramas_observados, hidrogramas_saida_derivacao):
    """Funcao para pegar o hidrograma de entrada para rodar o MKC"""
    #   Declarar
    hidrograma_usado_neste_mkc = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    
    #   Ver se e' oriunda da operacao de PQ
    if (entrada_operacao - 1) in indices_pq:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_pq.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_neste_mkc = hidrogramas_saida_pq[indHid]
    
    #   Ver se e' oriunda da operacao de PULS
    elif (entrada_operacao - 1) in indices_puls:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_puls.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_neste_mkc = hidrogramas_saida_puls[indHid]
        
    #   Ver se e' oriunda da operacao de MKC
    elif (entrada_operacao - 1) in indices_mkc:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_mkc.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_neste_mkc = hidrogramas_saida_mkc[indHid]
    
    #   Ver se e' oriunda da operacao de JUNC
    elif (entrada_operacao - 1) in indices_jun:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_jun.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_neste_mkc = hidrogramas_saida_jun[indHid]
        
    #   Ver se e' oriunda da operacao de leitura de hidrogramas
    elif (entrada_operacao - 1) in indices_hidro:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_hidro.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_neste_mkc = hidrogramas_observados[indHid]
        
    #   Ver se e' oriunda da operacao de DERIVACAO
    elif (entrada_operacao - 1) in indices_derivacao:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_derivacao.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_neste_mkc = hidrogramas_saida_derivacao[indHid]
    
    return hidrograma_usado_neste_mkc
#----------------------------------------------------------------------------------
def calcularOperacaoMKC(hidrograma_entrada, duracao_intervalo_tempo, numero_intervalos_tempo, diferenca_cota, comprimento_canal, largura_canal, coef_rugosidade):
    """Funcao para calcular as variaveis de saida de hidrograma"""
    #   Aplicar MKC
    hidrograma_resultante = aplicar_MuskingumCunge(hidrograma_entrada, numero_intervalos_tempo, duracao_intervalo_tempo, diferenca_cota, comprimento_canal, largura_canal, coef_rugosidade)
    #   Retornar hidrograma de saida
    return hidrograma_resultante
#----------------------------------------------------------------------------------
def escreverSaidaMKC(numero_intervalos_tempo, duracao_intervalo_tempo, numero_operacoes_hidrologicas, codigo_operacoes_hidrologicas, entradas_operacoes, indices_pq, indices_puls, indices_mkc, indices_jun, indices_hidro, indices_derivacao, hidrogramas_saida_pq, hidrogramas_saida_puls, hidrogramas_saida_mkc, hidrogramas_saida_jun, hidrogramas_saida_hidro, hidrogramas_saida_derivacao, diretorio_saida, nome_arquivo, nomes_operacoes):
    """Escreva o arquivo de saida para as operacoes de MKC"""
    #   Preparo arquivo de saida
    diretorio_saida = (diretorio_saida + "/Saida_MKC_".encode() + nome_arquivo + ".ohy".encode())
    arquivo_saida = open(diretorio_saida, mode='w', buffering=1, encoding='utf-8')

    #   Cabecalho
    arquivo_saida.write("\u000A                         MODELO HYDROLIB\u000A                     RESULTADOS DA MODELAGEM")
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A")

    #   Escrevo os parametros no arquivo de saida
    arquivo_saida.write("\u000A ---- PARAMETROS GERAIS DA SIMULAÇÃO  ----\u000A\u000A")
    arquivo_saida.write("Número total de simulações hidrológicas  = %d\u000A" %(numero_operacoes_hidrologicas))
    arquivo_saida.write("Número de simulações Muskingum-Cunge     = %d\u000A" %(len(hidrogramas_saida_mkc)))
    arquivo_saida.write("Número de intervalos de tempo            = %d\u000A" %(numero_intervalos_tempo))
    arquivo_saida.write("Duração do intervalo de tempo (segundos) = %d\u000A" %(duracao_intervalo_tempo))
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    arquivo_saida.write(" ---- INFORMAÇÕES DAS SIMULAÇÕES DE PROPAGAÇÃO DE MUSKINGUM-CUNGE ---- \u000A\u000A")
    
    #   Loop para escrever as informacoes
    for ii, entrada_operacao in enumerate(entradas_operacoes):
        #   Somente me interessam as operacoes de MKC
        if codigo_operacoes_hidrologicas[ii] == 3:
            #   Saber qual e' o indice correto para a matriz de saida de dados
            indice_saida = indices_mkc.index(ii)
            #   Cabecalho da operacao
            arquivo_saida.write("Operação hidrológica %d:%s\u000A" %((ii+1), nomes_operacoes[ii].decode('utf-8')))
            
            #   Oriundo de uma operacao hidrologica qualquer
            arquivo_saida.write("Número do hidrograma de entrada = %d\u000A" %(entrada_operacao))
            
            #   Ver se e' oriunda da operacao de PQ
            if (entrada_operacao - 1) in indices_pq:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_pq.index(entrada_operacao - 1)
                #   Se for oriundo de chuva-vazao
                arquivo_saida.write("Hidrograma de entrada oriundo de uma operação de chuva-vazão.\u000A")
                #   Escrever vazao de pico de saida
                arquivo_saida.write("Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Corpo
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_pq[indice_entrada][jj], hidrogramas_saida_mkc[indice_saida][jj]))
            
            #   Ver se e' oriunda da operacao de PULS
            elif (entrada_operacao - 1) in indices_puls:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_puls.index(entrada_operacao - 1)
                #   Se for oriundo de outro PULS
                arquivo_saida.write("Hidrograma de entrada oriundo de uma operação de propagação de reservatórios de Puls.\u000A")
                #   Escrever vazao de pico de saida
                arquivo_saida.write("Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Corpo
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_puls[indice_entrada][jj], hidrogramas_saida_mkc[indice_saida][jj]))
            
            #   Ver se e' oriunda da operacao de MKC
            elif (entrada_operacao - 1) in indices_mkc:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_mkc.index(entrada_operacao - 1)
                #   Se for oriundo de MKC
                arquivo_saida.write("Hidrograma de entrada oriundo de uma operação de propagação de canais de Muskingum-Cunge.\u000A")
                #   Escrever vazao de pico de saida
                arquivo_saida.write("Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Corpo
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %( (jj+1), hidrogramas_saida_mkc[indice_entrada][jj], hidrogramas_saida_mkc[indice_saida][jj] ))
            
            #   Ver se e' oriunda da operacao de JUNC
            elif (entrada_operacao - 1) in indices_jun:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_jun.index(entrada_operacao - 1)
                #   Se for oriundo de JUNCAO
                arquivo_saida.write("Hidrograma de entrada oriundo de uma operação de junção entre hidrogramas.\u000A")
                #   Escrever vazao de pico de saida
                arquivo_saida.write("Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Corpo
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_jun[indice_entrada][jj], hidrogramas_saida_mkc[indice_saida][jj]))
                    
            #   Ver se e' oriunda da operacao de LEITURA
            elif (entrada_operacao - 1) in indices_hidro:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_hidro.index(entrada_operacao - 1)
                #   Se for oriundo de arquivo de texto
                arquivo_saida.write("Hidrograma de entrada oriundo de um arquivo de texto.\u000A")
                #   Escrever vazao de pico de saida
                arquivo_saida.write("Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Corpo
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_hidro[indice_entrada][jj], hidrogramas_saida_mkc[indice_saida][jj]))
                    
            #   Ver se e' oriunda da operacao de DERIVACAO
            elif (entrada_operacao - 1) in indices_derivacao:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_derivacao.index(entrada_operacao - 1)
                #   Se for oriundo de DERIVACAO
                arquivo_saida.write("Hidrograma de entrada oriundo de uma operação de derivação.\u000A")
                #   Escrever vazao de pico de saida
                arquivo_saida.write("Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_mkc[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida Cotas_Reserv.\u000A")
                #   Corpo
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_derivacao[indice_entrada][jj], hidrogramas_saida_mkc[indice_saida][jj]))
                    
            #   Finalizacao
            arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    #   Feche o arquivo...
    arquivo_saida.close()
#----------------------------------------------------------------------
def plotarMKC(hidrograma_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """Chama a funcao de plotagem da Hydrolib"""
    plotar_Hidrogramas_MKC(hidrograma_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao)