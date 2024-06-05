# -*- coding: utf-8 -*-


#   Import das bibliotecas Python
from os import path
from numpy import array, float64
#   Import das bibliotecas customizadas
from lib.Hydrolib import somar_Hidrogramas
from lib.Hydrolib import plotar_somar_Hidrogramas


#----------------------------------------------------------------------
def gerarVariaveisSaidaJUNCAO(codigo_operacoes_hidrologicas, numero_intervalos_tempo):
    """Cria a matriz de saida para calcular as operacoes JUN"""
    #   Contar
    numero_operacoes_juncao = codigo_operacoes_hidrologicas.count(4)
    
    #   Variavel que armazena os hidrogramas gerados pelo chuva-vazao ...
    hidrogramas_saida_juncao = array([[0.0 for ii in range(numero_intervalos_tempo)] for jj in range(numero_operacoes_juncao)], float64)

    #   Retorne
    return hidrogramas_saida_juncao
#----------------------------------------------------------------------------------
def preparacaoJUNCAO(numero_intervalos_tempo, entradas_operacao, indices_pq, indices_puls, indices_mkc, indices_jun, indices_hidro, indices_derivacao, hidrogramas_saida_pq, hidrogramas_saida_puls, hidrogramas_saida_mkc, hidrogramas_saida_jun, hidrogramas_observados, hidrogramas_saida_derivacao):
    """Funcao para pegar o hidrograma de entrada para rodar o JUN"""
    #   Declarar
    hidrogramas_usados_nesta_juncao = array([[0.0 for ii in range(numero_intervalos_tempo)]for numero_hidrogramas in range(len(entradas_operacao))], float64)

    #   Iterar as operacoes: Lembrando que nao ha' como "juntar" hidrogramas observados
    for ii, numero_operacao in enumerate(entradas_operacao):
        #   Ver se e' oriunda da operacao de PQ
        if (numero_operacao - 1) in indices_pq:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_pq.index(numero_operacao - 1)
            #   Pegar seus valores
            hidrogramas_usados_nesta_juncao[ii] = hidrogramas_saida_pq[indHid]
        
        #   Ver se e' oriunda da operacao de PULS
        elif (numero_operacao - 1) in indices_puls:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_puls.index(numero_operacao - 1)
            #   Pegar seus valores
            hidrogramas_usados_nesta_juncao[ii] = hidrogramas_saida_puls[indHid]
            
        #   Ver se e' oriunda da operacao de MKC
        elif (numero_operacao - 1) in indices_mkc:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_mkc.index(numero_operacao - 1)
            #   Pegar seus valores
            hidrogramas_usados_nesta_juncao[ii] = hidrogramas_saida_mkc[indHid]
        
        #   Ver se e' oriunda da operacao de JUNC
        elif (numero_operacao - 1) in indices_jun:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_jun.index(numero_operacao - 1)
            #   Pegar seus valores
            hidrogramas_usados_nesta_juncao[ii] = hidrogramas_saida_jun[indHid]
            
        #   Ver se e' oriunda da operacao de leitura de hidrogramas
        elif (numero_operacao - 1) in indices_hidro:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_hidro.index(numero_operacao - 1)
            #   Pegar seus valores
            hidrogramas_usados_nesta_juncao[ii] = hidrogramas_observados[indHid]
            
        #   Ver se e' oriunda da operacao de DERIVACAO
        elif (entrada_operacao - 1) in indices_derivacao:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_derivacao.index(entrada_operacao - 1)
            #   Pegar seus valores
            hidrogramas_usados_nesta_juncao[ii] = hidrogramas_saida_derivacao[indHid]
        
    return hidrogramas_usados_nesta_juncao
#----------------------------------------------------------------------------------
def calcularOperacaoJUNCAO(hidrogramas_entrada, numero_intervalos_tempo):
    """Funcao para calcular as variaveis de saida de hidrograma"""
    #   Aplicar JUNCAO
    hidrograma_resultante = somar_Hidrogramas(numero_intervalos_tempo, hidrogramas_entrada)
    #   Retornar hidrograma de saida
    return hidrograma_resultante
#----------------------------------------------------------------------------------
def escreverSaidaJUNCAO(numero_intervalos_tempo, duracao_intervalo_tempo, numero_operacoes_hidrologicas, codigo_operacoes_hidrologicas, entradas_operacoes, indices_pq, indices_puls, indices_mkc, indices_jun, indices_hidro, indices_derivacao, hidrogramas_saida_pq, hidrogramas_saida_puls, hidrogramas_saida_mkc, hidrogramas_saida_jun, hidrogramas_saida_hidro, hidrogramas_saida_derivacao, diretorio_saida, nome_arquivo, nomes_operacoes):
    """Escreva o arquivo de saida para as operacoes de juncoes"""
    #   Preparo arquivo de saida
    diretorio_saida = (diretorio_saida + "/Saida_JUN_".encode() + nome_arquivo + ".ohy".encode())
    arquivo_saida = open(diretorio_saida, mode='w', buffering=-1, encoding='utf-8')
    
    #   Cabecalho
    arquivo_saida.write("\u000A                         MODELO HYDROLIB\u000A                     RESULTADOS DA MODELAGEM")
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A")
    
    #   Escrevo os parametros no arquivo de saida
    arquivo_saida.write("\u000A ---- PARAMETROS GERAIS DA SIMULAÇÃO  ----\u000A\u000A")
    arquivo_saida.write("Número total de simulações hidrológicas  = %d\u000A" %(numero_operacoes_hidrologicas))
    arquivo_saida.write("Número de simulações Junções             = %d\u000A" %(len(hidrogramas_saida_jun)))
    arquivo_saida.write("Número de intervalos de tempo            = %d\u000A" %(numero_intervalos_tempo))
    arquivo_saida.write("Duração do intervalo de tempo (segundos) = %d\u000A" %(duracao_intervalo_tempo))
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    arquivo_saida.write(" ---- INFORMAÇÕES DAS SIMULAÇÕES DE JUNÇÃO ---- \u000A\u000A")
    
    #   Loop para escrever as informacoes
    for ii, entradas_juncao in enumerate(entradas_operacoes):
        #   Somente me interessam as operacoes de JUN
        if codigo_operacoes_hidrologicas[ii] == 4:
            #   Saber qual e' o indice correto para a matriz de saida de dados
            indice_saida = indices_jun.index(ii)
            #   Cabecalho da operacao
            arquivo_saida.write("Operação hidrológica %d:%s\u000A" %((ii+1), nomes_operacoes[ii].decode('utf-8')))
            
            #   Criar a matriz que juntara' os resultados
            hidrogramas_entrada = [[0. for nint_tempo in range(numero_intervalos_tempo)] for numero_hidrogramas in range(len(entradas_juncao))]
            
            #    loop para comecar a copiar os valores
            for kk, entrada_operacao in enumerate(entradas_juncao):
                #   Oriundo de uma operacao hidrologica qualquer
                arquivo_saida.write("Número do hidrograma de entrada = %d\u000A" %(entrada_operacao))
                
                #   Ver se e' oriunda da operacao de PQ
                if (entrada_operacao - 1) in indices_pq:
                    #   Faz parte dessa operacao, pegar o indice
                    indice_entrada = indices_pq.index(entrada_operacao - 1)
                    #   Pegar os valores
                    hidrogramas_entrada[kk] = hidrogramas_saida_pq[indice_entrada]
                
                #   Ver se e' oriunda da operacao de PULS
                elif (entrada_operacao - 1) in indices_puls:
                    #   Faz parte dessa operacao, pegar o indice
                    indice_entrada = indices_puls.index(entrada_operacao - 1)
                    #   Pegar os valores
                    hidrogramas_entrada[kk] = hidrogramas_saida_puls[indice_entrada]
                
                #   Ver se e' oriunda da operacao de MKC
                elif (entrada_operacao - 1) in indices_mkc:
                    #   Faz parte dessa operacao, pegar o indice
                    indice_entrada = indices_mkc.index(entrada_operacao - 1)
                    #   Pegar os valores
                    hidrogramas_entrada[kk] = hidrogramas_saida_mkc[indice_entrada]
                
                #   Ver se e' oriunda da operacao de JUNC
                elif (entrada_operacao - 1) in indices_jun:
                    #   Faz parte dessa operacao, pegar o indice
                    indice_entrada = indices_jun.index(entrada_operacao - 1)
                    #   Pegar os valores
                    hidrogramas_entrada[kk] = hidrogramas_saida_jun[indice_entrada]
                    
                #   Ver se e' oriunda de uma operacao de leitura
                elif (entrada_operacao - 1) in indices_hidro:
                    #   Faz parte dessa operacao, pegar o indice
                    indice_entrada = indices_hidro.index(entrada_operacao - 1)
                    #   Pegar os valores
                    hidrogramas_entrada[kk] = hidrogramas_saida_hidro[indices_entrada]
                    
                #   Ver se e' oriunda de uma operacao de leitura
                elif (entrada_operacao - 1) in indices_derivacao:
                    #   Faz parte dessa operacao, pegar o indice
                    indice_entrada = indices_derivacao.index(entrada_operacao - 1)
                    #   Pegar os valores
                    hidrogramas_entrada[kk] = hidrogramas_saida_derivacao[indices_entrada]
            
            #   Escrever o pico de vazao de saida
            arquivo_saida.write("Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_jun[indice_saida])))
            
            #   Escrever no arquivo de saida
            #   Cabecalho
            aux = ("      dt")
            for jj in range(len(hidrogramas_entrada)):
                aux += (" Hidro_Entrada")
            aux += (" Hidrogr_Saida\u000A")
            #   Escrever o cabecalho no arquivo
            arquivo_saida.write("%s"%(aux))
            
            #   Corpo
            for jj in range(numero_intervalos_tempo):
                arquivo_saida.write("%8d"%(jj+1))
                for kk in range(len(hidrogramas_entrada)):
                    arquivo_saida.write("%14.5f" %(hidrogramas_entrada[kk][jj]))
                arquivo_saida.write("%14.5f\u000A" %(hidrogramas_saida_jun[indice_saida][jj]))
            
            #   Finalizacao
            arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    #   Feche o arquivo...
    arquivo_saida.close()
#----------------------------------------------------------------------
def plotarJUN(hidrogramas_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """Chama a funcao de plotagem da Hydrolib"""
    plotar_somar_Hidrogramas(hidrogramas_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao)