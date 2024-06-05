# -*- coding: utf-8 -*-


#   Import das bibliotecas Python
from os import path
from numpy import array, float64, argmax
#   Import das bibliotecas customizadas
from lib.Leitura import lerSerieObservada
from lib.Hydrolib import plotar_Hidrogramas_Leitura


#----------------------------------------------------------------------
def gerarVariaveisSaidaHIDROGRAMA(codigo_operacoes_hidrologicas, numero_intervalos_tempo):
    #   Contar
    numero_operacoes_hidrograma = codigo_operacoes_hidrologicas.count(5)
    
    #   Variavel que armazena os hidrogramas gerados pelo chuva-vazao ...
    hidrogramas_observados = array([[0.0 for ii in range(numero_intervalos_tempo)] for jj in range(numero_operacoes_hidrograma)], float64)

    #   Retorne
    return hidrogramas_observados
#----------------------------------------------------------------------------------
def lerOperacaoHIDROGRAMA(numero_intervalos_tempo, diretorio_arquivo):
    #   Ler valores
    hidrograma_observado = lerSerieObservada(diretorio_arquivo, numero_intervalos_tempo)
    #   Retorne
    return hidrograma_observado
#----------------------------------------------------------------------------------
def escreverSaidaHIDROGRAMA(numero_intervalos_tempo, duracao_intervalo_tempo, numero_operacoes_hidrologicas, codigo_operacoes_hidrologicas, diretorios_hidrogramas_observados, entradas_operacoes, indices_hidro, hidrogramas_saida_hidro, diretorio_saida, nome_arquivo, nomes_operacoes):
    """Escreva o arquivo de saida para as operacoes de leitura de hidrogramas"""
    #   Preparo arquivo de saida
    diretorio_saida = (diretorio_saida + "/Saida_LEITURA_HIDROGRAMAS_".encode() + nome_arquivo + ".ohy".encode())
    arquivo_saida = open(diretorio_saida, mode='w', buffering=-1, encoding='utf-8')
    
    #   Cabecalho
    arquivo_saida.write("\u000A                         MODELO HYDROLIB\u000A                     RESULTADOS DA MODELAGEM")
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A")

    #   Escrevo os parametros no arquivo de saida
    arquivo_saida.write("\u000A ---- PARAMETROS GERAIS DA SIMULAÇÃO  ----\u000A\u000A")
    arquivo_saida.write("Número total de simulações hidrológicas  = %d\u000A" %(numero_operacoes_hidrologicas))
    arquivo_saida.write("Número de leitura de hidrogramas         = %d\u000A" %(len(hidrogramas_saida_hidro)))
    arquivo_saida.write("Número de intervalos de tempo            = %d\u000A" %(numero_intervalos_tempo))
    arquivo_saida.write("Duração do intervalo de tempo (segundos) = %d\u000A" %(duracao_intervalo_tempo))
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    arquivo_saida.write(" ---- INFORMAÇÕES DAS LEITURAS DE HIDROGRAMAS ---- \u000A\u000A")
    
    #   Loop para escrever as informacoes
    for ii, entrada_operacao in enumerate(entradas_operacoes):
        #   Somente me interessam as operacoes de Leitura
        if codigo_operacoes_hidrologicas[ii] == 5:
            #   Saber qual e' o indice correto para a matriz de saida de dados
            indice_saida = indices_hidro.index(ii)
            #   Cabecalho da operacao
            arquivo_saida.write("Operação hidrológica %d:%s\u000A" %((ii+1), nomes_operacoes[ii].decode('utf-8')))

            #   Oriundo de uma operacao hidrologica qualquer
            arquivo_saida.write("\u0009Hidrograma de entrada fornecido pelo usuário.\u000A")
            arquivo_saida.write("\u0009Diretório: '%s'\u000A" %(diretorios_hidrogramas_observados[ii].decode('utf-8')))
            #   Escrever vazao de pico de saida
            arquivo_saida.write("\u0009Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_hidro[indice_saida])))
            #   Cabecalho
            arquivo_saida.write("      dt Hidro_Entrada\u000A")
            #   Corpo
            for jj in range(numero_intervalos_tempo):
                arquivo_saida.write("%8d%14.5f\u000A" %((jj+1), hidrogramas_saida_hidro[indice_saida][jj]))
            #   Finalizacao
            arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    #   Feche o arquivo...
    arquivo_saida.close()
#----------------------------------------------------------------------------------
def plotarHIDROGRAMA(hidrograma_entrada, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """Chama a funcao de plotagem da Hydrolib"""
    plotar_Hidrogramas_Leitura(hidrograma_entrada, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao)
#----------------------------------------------------------------------------------