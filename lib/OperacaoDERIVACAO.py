# -*- coding: utf-8 -*-


#   Import das bibliotecas Python
from os import path
from numpy import array, float64, argmax
#   Import das bibliotecas customizadas
from lib.Hydrolib import aplicar_Derivacao_Constante
from lib.Hydrolib import aplicar_Derivacao_Porcentagem
from lib.Hydrolib import aplicar_Derivacao_Hidrograma
from lib.Hydrolib import plotar_Hidrogramas_Derivacao


#----------------------------------------------------------------------
def gerarVariaveisSaidaDERIVACAO(codigo_operacoes_hidrologicas, numero_intervalos_tempo):
    """Cria a matriz de saida para calcular as operacoes DERIVACAO"""
    #   Contar
    numero_operacoes_hidrograma = codigo_operacoes_hidrologicas.count(5)
    
    #   Variavel que armazena os hidrogramas
    hidrogramas_saida_derivacao = array([[0.0 for ii in range(numero_intervalos_tempo)] for jj in range(numero_operacoes_hidrograma)], float64)

    #   Retorne
    return hidrogramas_saida_derivacao
#----------------------------------------------------------------------------------
def preparacaoDERIVACAO(numero_intervalos_tempo, entrada_operacao, indices_pq, indices_puls, indices_mkc, indices_jun, indices_hidro, indices_derivacao, hidrogramas_saida_pq, hidrogramas_saida_puls, hidrogramas_saida_mkc, hidrogramas_saida_jun, hidrogramas_observados, hidrogramas_saida_derivacao, tipo_derivacao, valor_derivacao):
    """Funcao para pegar o hidrograma de entrada para rodar o DERIVACAO"""
    #   Declarar
    hidrograma_usado_nesta_derivacao    = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    hidrograma_retirado_nesta_derivacao = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    
    #   Ver se e' oriunda da operacao de PQ
    if (entrada_operacao - 1) in indices_pq:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_pq.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_nesta_derivacao = hidrogramas_saida_pq[indHid]
    
    #   Ver se e' oriunda da operacao de PULS
    elif (entrada_operacao - 1) in indices_puls:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_puls.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_nesta_derivacao = hidrogramas_saida_puls[indHid]
        
    #   Ver se e' oriunda da operacao de MKC
    elif (entrada_operacao - 1) in indices_mkc:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_mkc.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_nesta_derivacao = hidrogramas_saida_mkc[indHid]
    
    #   Ver se e' oriunda da operacao de JUNC
    elif (entrada_operacao - 1) in indices_jun:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_jun.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_nesta_derivacao = hidrogramas_saida_jun[indHid]
        
    #   Ver se e' oriunda da operacao de leitura de hidrogramas
    elif (entrada_operacao - 1) in indices_hidro:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_hidro.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_nesta_derivacao = hidrogramas_observados[indHid]
    
    #   Ver se e' oriunda da operacao de DERIVACAO
    elif (entrada_operacao - 1) in indices_derivacao:
        #   Faz parte dessa operacao, pegar o indice
        indHid = indices_derivacao.index(entrada_operacao - 1)
        #   Pegar seus valores
        hidrograma_usado_nesta_derivacao = hidrogramas_saida_derivacao[indHid]
    
    #   Agora para caso a derivacao e' feita com base em outro hidrograma
    if tipo_derivacao == 3:
        #   Identificar de onde vem o hidrograma
        #   Ver se e' oriunda da operacao de PQ
        if (valor_derivacao - 1) in indices_pq:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_pq.index(valor_derivacao - 1)
            #   Pegar seus valores
            hidrograma_retirado_nesta_derivacao = hidrogramas_saida_pq[indHid]
        
        #   Ver se e' oriunda da operacao de PULS
        elif (valor_derivacao - 1) in indices_puls:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_puls.index(valor_derivacao - 1)
            #   Pegar seus valores
            hidrograma_retirado_nesta_derivacao = hidrogramas_saida_puls[indHid]
            
        #   Ver se e' oriunda da operacao de MKC
        elif (valor_derivacao - 1) in indices_mkc:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_mkc.index(valor_derivacao - 1)
            #   Pegar seus valores
            hidrograma_retirado_nesta_derivacao = hidrogramas_saida_mkc[indHid]
        
        #   Ver se e' oriunda da operacao de JUNC
        elif (valor_derivacao - 1) in indices_jun:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_jun.index(valor_derivacao - 1)
            #   Pegar seus valores
            hidrograma_retirado_nesta_derivacao = hidrogramas_saida_jun[indHid]
            
        #   Ver se e' oriunda da operacao de leitura de hidrogramas
        elif (valor_derivacao - 1) in indices_hidro:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_hidro.index(valor_derivacao - 1)
            #   Pegar seus valores
            hidrograma_retirado_nesta_derivacao = hidrogramas_observados[indHid]
        
        #   Ver se e' oriunda da operacao de DERIVACAO
        elif (valor_derivacao - 1) in indices_derivacao:
            #   Faz parte dessa operacao, pegar o indice
            indHid = indices_derivacao.index(valor_derivacao - 1)
            #   Pegar seus valores
            hidrograma_retirado_nesta_derivacao = hidrogramas_saida_derivacao[indHid]
        
    return hidrograma_usado_nesta_derivacao, hidrograma_retirado_nesta_derivacao
#----------------------------------------------------------------------------------
def calcularOperacaoDERIVACAO(numero_intervalos_tempo, hidrograma_entrada, tipo_derivacao, valor_derivacao, saida_derivacao, hidrograma_retirado):
    """Funcao para calcular as variaveis de saida de hidrograma"""
    #   Derivacao constante
    if tipo_derivacao == 1:
        hidrograma_resultante = aplicar_Derivacao_Constante(numero_intervalos_tempo, hidrograma_entrada, valor_derivacao, saida_derivacao)
    #   Derivacao em porcentagem
    elif tipo_derivacao == 2:
        hidrograma_resultante = aplicar_Derivacao_Porcentagem(numero_intervalos_tempo, hidrograma_entrada, valor_derivacao, saida_derivacao)
    #   Derivacao em hidrograma
    else:
        hidrograma_resultante = aplicar_Derivacao_Hidrograma(numero_intervalos_tempo, hidrograma_entrada, hidrograma_retirado, saida_derivacao)
    
    #   Retornar hidrograma de saida
    return hidrograma_resultante
#----------------------------------------------------------------------------------
def escreverSaidaDERIVACAO(numero_intervalos_tempo, duracao_intervalo_tempo, numero_operacoes_hidrologicas, codigo_operacoes_hidrologicas, entradas_operacoes, indices_pq, indices_puls, indices_mkc, indices_jun, indices_hidro, indices_derivacao, hidrogramas_saida_pq, hidrogramas_saida_puls, hidrogramas_saida_mkc, hidrogramas_saida_jun, hidrogramas_saida_hidro, hidrogramas_saida_derivacao, tipo_derivacao, valor_derivacao, saida_derivacao, diretorio_saida, nome_arquivo, nomes_operacoes, prf):
    """Escreva o arquivo de saida para as operacoes de derivacao"""
    #   Preparo arquivo de saida
    diretorio_saida = (diretorio_saida + "/Saida_DERIVACAO_".encode() + nome_arquivo + ".ohy".encode())
    arquivo_saida = open(diretorio_saida, mode='w', buffering=-1, encoding='utf-8')
    
    #   Cabecalho
    arquivo_saida.write("\u000A                         MODELO HYDROLIB\u000A                     RESULTADOS DA MODELAGEM")
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A")

    #   Escrevo os parametros no arquivo de saida
    arquivo_saida.write("\u000A ---- PARAMETROS GERAIS DA SIMULAÇÃO  ----\u000A\u000A")
    arquivo_saida.write("Número total de simulações hidrológicas  = %d\u000A" %(numero_operacoes_hidrologicas))
    arquivo_saida.write("Número de operações de derivação         = %d\u000A" %(len(hidrogramas_saida_derivacao)))
    arquivo_saida.write("Número de intervalos de tempo            = %d\u000A" %(numero_intervalos_tempo))
    arquivo_saida.write("Duração do intervalo de tempo (segundos) = %d\u000A" %(duracao_intervalo_tempo))
    arquivo_saida.write("Fator de pico                            = %d\u000A" %(prf))
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    arquivo_saida.write(" ---- INFORMAÇÕES DAS DERIVAÇÕES ---- \u000A\u000A")
    
    #   Loop para escrever as informacoes
    for ii, entrada_operacao in enumerate(entradas_operacoes):
        #   Somente me interessam as operacoes de Derivacao
        if codigo_operacoes_hidrologicas[ii] == 6:
            #   Saber qual e' o indice correto para a matriz de saida de dados
            indice_saida = indices_derivacao.index(ii)
            #   Cabecalho da operacao
            arquivo_saida.write("Operação hidrológica %d:%s\u000A" %((ii+1), nomes_operacoes[ii].decode('utf-8')))
            #   Oriundo de uma operacao hidrologica qualquer
            arquivo_saida.write("\u0009Número do hidrograma de entrada = %d\u000A" %(entrada_operacao))
            
            #   Ver se e' oriunda da operacao de PQ
            if (entrada_operacao - 1) in indices_pq:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_pq.index(entrada_operacao - 1)
                #   Se for oriundo de chuva-vazao
                arquivo_saida.write("\u0009Hidrograma de entrada oriundo de uma operação de chuva-vazão.\u000A")
                
                #   Avaliar o tipo de derivacao
                
                #   Derivacao constante
                if tipo_derivacao[ii] == 1:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Constante\u000A")
                    arquivo_saida.write("\u0009Valor derivado (m³/s) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Derivacao de procentagem
                elif tipo_derivacao[ii] == 2:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Porcentual\u000A")
                    arquivo_saida.write("\u0009Valor porcentual derivado (%%) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                    
                #   Derivacao de hidrograma
                else:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Hidrograma\u000A")
                    arquivo_saida.write("\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"%(int(valor_derivacao[ii])))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Escrever vazao de pico de saida
                arquivo_saida.write("\u0009Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_derivacao[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Escrever a saida
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_pq[indice_entrada][jj], hidrogramas_saida_derivacao[indice_saida][jj]))
            
            
            #   Ver se e' oriunda da operacao de PULS
            elif (entrada_operacao - 1) in indices_puls:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_puls.index(entrada_operacao - 1)
                #   Se for oriundo de outro PULS
                arquivo_saida.write("\u0009Hidrograma de entrada oriundo de uma operação de propagação de reservatórios de Puls.\u000A")
                
                #   Avaliar o tipo de derivacao
                
                #   Derivacao constante
                if tipo_derivacao[ii] == 1:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Constante\u000A")
                    arquivo_saida.write("\u0009Valor derivado (m³/s) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Derivacao de procentagem
                elif tipo_derivacao[ii] == 2:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Porcentual\u000A")
                    arquivo_saida.write("\u0009Valor porcentual derivado (%%) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                    
                #   Derivacao de hidrograma
                else:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Hidrograma\u000A")
                    arquivo_saida.write("\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"%(int(valor_derivacao[ii])))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Escrever vazao de pico de saida
                arquivo_saida.write("\u0009Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_derivacao[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Escrever a saida
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_puls[indice_entrada][jj], hidrogramas_saida_derivacao[indice_saida][jj]))
            
            
            #   Ver se e' oriunda da operacao de MKC
            elif (entrada_operacao - 1) in indices_mkc:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_mkc.index(entrada_operacao - 1)
                #   Se for oriundo de MKC
                arquivo_saida.write("\u0009Hidrograma de entrada oriundo de uma operação de propagação de canais de Muskingum-Cunge.\u000A")
                
                #   Avaliar o tipo de derivacao
                
                #   Derivacao constante
                if tipo_derivacao[ii] == 1:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Constante\u000A")
                    arquivo_saida.write("\u0009Valor derivado (m³/s) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Derivacao de procentagem
                elif tipo_derivacao[ii] == 2:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Porcentual\u000A")
                    arquivo_saida.write("\u0009Valor porcentual derivado (%%) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                    
                #   Derivacao de hidrograma
                else:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Hidrograma\u000A")
                    arquivo_saida.write("\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"%(int(valor_derivacao[ii])))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Escrever vazao de pico de saida
                arquivo_saida.write("\u0009Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_derivacao[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Escrever a saida
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_mkc[indice_entrada][jj], hidrogramas_saida_derivacao[indice_saida][jj]))
            
            
            #   Ver se e' oriunda da operacao de JUNC
            elif (entrada_operacao - 1) in indices_jun:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_jun.index(entrada_operacao - 1)
                #   Se for oriundo de JUNCAO
                arquivo_saida.write("\u0009Hidrograma de entrada oriundo de uma operação de junção entre hidrogramas.\u000A")
                
                #   Avaliar o tipo de derivacao
                
                #   Derivacao constante
                if tipo_derivacao[ii] == 1:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Constante\u000A")
                    arquivo_saida.write("\u0009Valor derivado (m³/s) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Derivacao de procentagem
                elif tipo_derivacao[ii] == 2:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Porcentual\u000A")
                    arquivo_saida.write("\u0009Valor porcentual derivado (%%) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                    
                #   Derivacao de hidrograma
                else:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Hidrograma\u000A")
                    arquivo_saida.write("\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"%(int(valor_derivacao[ii])))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Escrever vazao de pico de saida
                arquivo_saida.write("\u0009Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_derivacao[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Escrever a saida
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_jun[indice_entrada][jj], hidrogramas_saida_derivacao[indice_saida][jj]))
            
            
            #   Ver se e' oriunda da operacao de LEITURA
            elif (entrada_operacao - 1) in indices_hidro:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_hidro.index(entrada_operacao - 1)
                #   Se for oriundo de LEITURA
                arquivo_saida.write("\u0009Hidrograma de entrada oriundo de um arquivo de texto.\u000A")
                
                #   Avaliar o tipo de derivacao
                
                #   Derivacao constante
                if tipo_derivacao[ii] == 1:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Constante\u000A")
                    arquivo_saida.write("\u0009Valor derivado (m³/s) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Derivacao de procentagem
                elif tipo_derivacao[ii] == 2:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Porcentual\u000A")
                    arquivo_saida.write("\u0009Valor porcentual derivado (%%) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                    
                #   Derivacao de hidrograma
                else:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Hidrograma\u000A")
                    arquivo_saida.write("\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"%(int(valor_derivacao[ii])))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Escrever vazao de pico de saida
                arquivo_saida.write("\u0009Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_derivacao[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Escrever a saida
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_hidro[indice_entrada][jj], hidrogramas_saida_derivacao[indice_saida][jj]))
            
            
            #   Ver se e' oriunda da operacao de DERIVACAO
            elif (entrada_operacao - 1) in indices_derivacao:
                #   Faz parte dessa operacao, pegar o indice
                indice_entrada = indices_derivacao.index(entrada_operacao - 1)
                #   Se for oriundo de DERIVACAO
                arquivo_saida.write("\u0009Hidrograma de entrada oriundo de uma operação de derivação.\u000A")
            
                #   Avaliar o tipo de derivacao
                
                #   Derivacao constante
                if tipo_derivacao[ii] == 1:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Constante\u000A")
                    arquivo_saida.write("\u0009Valor derivado (m³/s) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Derivacao de procentagem
                elif tipo_derivacao[ii] == 2:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Porcentual\u000A")
                    arquivo_saida.write("\u0009Valor porcentual derivado (%%) = %.2f\u000A"%(valor_derivacao[ii]))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                    
                #   Derivacao de hidrograma
                else:
                    #   Cabecalho
                    arquivo_saida.write("\u0009Tipo de derivação: Hidrograma\u000A")
                    arquivo_saida.write("\u0009Número do hidrograma utilizado como derivação (-) = %d\u000A"%(int(valor_derivacao[ii])))
                    #   Qual saida?
                    #   == 1: Hidrograma principal
                    if saida_derivacao[ii] == 1:
                        arquivo_saida.write("\u0009Hidrograma de saída: Curso principal\u000A")
                    #   == 2: Hidrograma derivado
                    else:
                        arquivo_saida.write("\u0009Hidrograma de saída: Derivado\u000A")
                
                #   Escrever vazao de pico de saida
                arquivo_saida.write("\u0009Pico de vazão de saída = %.5f [m³/s]\u000A\u000A"%(max(hidrogramas_saida_derivacao[indice_saida])))
                #   Cabecalho
                arquivo_saida.write("      dt Hidro_Entrada Hidrogr_Saida\u000A")
                #   Escrever a saida
                for jj in range(numero_intervalos_tempo):
                    arquivo_saida.write("%8d%14.5f%14.5f\u000A" %((jj+1), hidrogramas_saida_derivacao[indice_entrada][jj], hidrogramas_saida_derivacao[indice_saida][jj]))
            
            #   Finalizacao
            arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    #   Feche o arquivo...
    arquivo_saida.close()
#----------------------------------------------------------------------------------
def plotarDERIVACAO(hidrograma_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """Chama a funcao de plotagem da Hydrolib"""
    plotar_Hidrogramas_Derivacao(hidrograma_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao)
#----------------------------------------------------------------------------------