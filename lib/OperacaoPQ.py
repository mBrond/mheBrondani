# -*- coding: utf-8 -*-


#   Import das bibliotecas Python
from os import path
from numpy import array, float64, argmax
#   Import das bibliotecas customizadas
from Utilidades import atualizarBarraProgresso
from Leitura import lerSerieObservada
from Hydrolib import calcular_PrecipitacaoDesacumulada, aplicar_BlocosAlternados
from Hydrolib import calcular_PrecipitacaoEfetiva_CN, calcular_HUT_SCS
from Hydrolib import aplicar_Convolucao, plotar_Hidrogramas_PQ
from Hydrolib import plotar_Hidrogramas_PQ


#----------------------------------------------------------------------
def gerarVariaveisSaidaPQ(codigo_operacoes_hidrologicas, numero_intervalos_tempo, chuvas_entrada_pq, numero_chuvas, numero_intervalos_tempo_chuva, duracao_intervalo_tempo, parametro_a, parametro_b, parametro_c, parametro_d, limites_idf, posicao_pico, tempo_retorno, diretorios_chuvas):
    """Cria a matriz de saida para calcular as operacoes PQ e cria (e calcula aqui mesmo) a matriz de chuvas utilizadas nessas operacoes (chuva-vazao)"""
    #   Contar
    numero_operacoes_pq = codigo_operacoes_hidrologicas.count(1)
    
    #   Variavel que armazena os hidrogramas gerados pelo chuva-vazao ...
    hidrogramas_saida_pq   = array([[0.0 for ii in range(numero_intervalos_tempo)] for y in range(numero_operacoes_pq)], float64)
    precipitacoes_efetivas = array([[0.0 for ii in range(numero_intervalos_tempo_chuva)] for y in range(numero_operacoes_pq)], float64)
    
    #   Contador
    precipitacoes_pq = []
    #   Logica para verificar quantas series de Pord serao necessarias (objetivo: alcancar o menor numero possivel. Se alguma repetir, nao calcularemos de novo);
    for ii in range(len(codigo_operacoes_hidrologicas)):
        #   Ou seja, se for operacao PQ ->E<- ela nao esta' nas numero_pord;
        if ((codigo_operacoes_hidrologicas[ii] == 1) and (not chuvas_entrada_pq[ii] in precipitacoes_pq)): 
            #   aqui eu terei somente UM numero de cada posto que FOR DA OPERACAO PQ
            precipitacoes_pq.append(chuvas_entrada_pq[ii]) 
    
    #   Variavel que armazena valores de precipitacao ordenada: Nao repita chuvas
    precipitacoes_ordenadas = array([[0.0 for ii in range(numero_intervalos_tempo_chuva)] for jj in range(len(precipitacoes_pq))], float64)
    
    if numero_chuvas > 0: print ("\n\tGerando series de chuva.")
    
    #   Inicializar barra: Pra inicializar precisa dar +1 no limite
    atualizarBarraProgresso(0, numero_chuvas)
    
    #   Loop para declaracao das variaveis de chuva das operacoes chuva-vazao
    for chuva in range(numero_chuvas):
        #   Se chuva sintetica
        if diretorios_chuvas[chuva] == None:
            #   Atualizar o indice para pegar a referencia do lugar certo
            indice_idf = precipitacoes_pq[chuva]
            #   E' chuva de IDF, calcular com a funcao;
            precipitacoes_ordenadas[chuva] = calcularChuvasOrdenadas(numero_intervalos_tempo_chuva, duracao_intervalo_tempo, parametro_a[indice_idf], parametro_b[indice_idf], parametro_c[indice_idf], parametro_d[indice_idf], limites_idf[indice_idf], posicao_pico[indice_idf], tempo_retorno[indice_idf])
        
        #   Se chuva observada
        else:
            #   Pegar o diretorio do arquivo de chuva observada
            diretorio_arquivo = diretorios_chuvas[chuva]
            
            #   Ler valores
            precipitacoes_ordenadas[chuva] = lerSerieObservada(diretorio_arquivo, numero_intervalos_tempo_chuva)
        
        #   Atualizar barra
        atualizarBarraProgresso(chuva+1, numero_chuvas)
            
    #   Retorne
    return hidrogramas_saida_pq, precipitacoes_ordenadas, precipitacoes_efetivas
#----------------------------------------------------------------------------------
def calcularChuvasOrdenadas(numero_intervalos_tempo_chuva, duracao_intervalo_tempo, parametro_a, parametro_b, parametro_c, parametro_d, limite_idf, posicao_pico, tempo_retorno):
    """Funcao para criar as variaveis de chuva utilizadas"""
    #   Calcule a precipitacao desacumulada
    precipitacao_sintetica = calcular_PrecipitacaoDesacumulada(numero_intervalos_tempo_chuva, duracao_intervalo_tempo, tempo_retorno, parametro_a, parametro_b, parametro_c, parametro_d, limite_idf)
    #   Transforme-a em ordenada
    precipitacao_sintetica = aplicar_BlocosAlternados(precipitacao_sintetica, numero_intervalos_tempo_chuva, posicao_pico)
    #   Retorne
    return precipitacao_sintetica
#----------------------------------------------------------------------------------
def calcularOperacaoPQ(numero_intervalos_tempo, duracao_intervalo_tempo, numero_intervalos_tempo_chuva, coeficiente_cn, area_km2, tc_horas, precipitacao_ordenada):
    """Funcao para calcular as variaveis de saida de hidrograma"""
    #   Calcular a Precipitacao Efetiva
    precipitacao_efetiva = calcular_PrecipitacaoEfetiva_CN(coeficiente_cn, precipitacao_ordenada, numero_intervalos_tempo_chuva)
    #   Calcular HUT da operacao
    tempo_subida, vazao_pico_hut, tempo_base = calcular_HUT_SCS(tc_horas, area_km2, duracao_intervalo_tempo) #Caracteristicas do HUT para convolucao
    #   Calular Hidrograma da operacao
    hidrograma_resultante = aplicar_Convolucao(tempo_base, vazao_pico_hut, tempo_subida, duracao_intervalo_tempo, numero_intervalos_tempo, numero_intervalos_tempo_chuva, precipitacao_efetiva) #Convolucao para HUT
    #   Retorne
    return hidrograma_resultante, precipitacao_efetiva
#---------------------------------------------------------------------------------- 
def escreverSaidaPQ(numero_intervalos_tempo, duracao_intervalo_tempo, numero_intervalos_tempo_chuva, numero_operacoes_hidrologicas, codigo_operacoes_hidrologicas, coeficiente_cn, area_km2, tc_horas, chuvas_entrada_pq, precipitacoes_ordenadas, hidrogramas_saida_pq, precipitacoes_efetivas, diretorio_saida, nome_arquivo, nomes_operacoes):
    """Escreva o arquivo de saida para as operacoes de PQ"""
    #   Preparo arquivo de saida
    diretorio_saida = (diretorio_saida + "/Saida_PQ_".encode() + nome_arquivo + ".ohy".encode())
    arquivo_saida = open(diretorio_saida, mode='w', buffering=-1, encoding='utf-8')

    #   Cabecalho
    arquivo_saida.write("\u000A                         MODELO HYDROLIB\u000A                     RESULTADOS DA MODELAGEM")
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A")

    #   Escrevo os parametros no arquivo de saida
    arquivo_saida.write("\u000A ---- PARAMETROS GERAIS DA SIMULAÇÃO  ----\u000A\u000A")
    arquivo_saida.write("Número total de simulações hidrológicas  = %d\u000A" %(numero_operacoes_hidrologicas))
    arquivo_saida.write("Número de simulações Chuva-Vazão         = %d\u000A" %(len(hidrogramas_saida_pq)))
    arquivo_saida.write("Número de intervalos de tempo            = %d\u000A" %(numero_intervalos_tempo))
    arquivo_saida.write("Número de intervalos de tempo com chuva  = %d\u000A" %(numero_intervalos_tempo_chuva))
    arquivo_saida.write("Duração do intervalo de tempo (segundos) = %d\u000A" %(duracao_intervalo_tempo))
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    arquivo_saida.write(" ---- INFORMAÇÕES DAS SIMULAÇÕES CHUVA-VAZÃO ---- \u000A")
    #   faz parte do cabecalho do programa
    for ii, codigo in enumerate(codigo_operacoes_hidrologicas):
        #   Se o codigo dizer que e' PQ....
        if codigo == 1:
            arquivo_saida.write("\u000AHidrograma %d:%s\u000A" %((ii+1), nomes_operacoes[ii].decode('utf-8')))
            arquivo_saida.write("\u0009Calculada a partir da chuva de projeto: %d\u000A" %(chuvas_entrada_pq[ii] + 1))
            arquivo_saida.write("\u0009       Coeficiente CN = %10.4f [  -  ]\u000A" %(coeficiente_cn[ii]))
            arquivo_saida.write("\u0009        Área da bacia = %10.4f [ km² ]\u000A" %(area_km2[ii]))
            arquivo_saida.write("\u0009Tempo de concentração = %10.4f [horas]\u000A" %(tc_horas[ii]))
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    
    arquivo_saida.write(" ---- VAZÕES DE PICO (m³/s) E VOLUMES ESCOADOS (m³) ----\u000A")
    
    #   :)
    for ii, hidrograma in enumerate(hidrogramas_saida_pq):
        #   Declarar/resetar
        volume_hidrograma = 0.
        #   Calcular o volume
        for jj in range(numero_intervalos_tempo-1):
            #   Metodo dos retangulos
            volume_hidrograma += (((hidrograma[jj] + hidrograma[jj+1])/2.) * duracao_intervalo_tempo)
        #   Demais informacoes
        arquivo_saida.write("\u000AHidrograma %d:%s\u000A" %((ii+1), nomes_operacoes[ii].decode('utf-8')))
        arquivo_saida.write("\u0009Vazão de pico   = %.4f [m³/s]\u000A" %(max(hidrograma)))
        arquivo_saida.write("\u0009Posicao do pico = %d (em %d segundos)\u000A" %((argmax(hidrograma)+1), (argmax(hidrograma)*duracao_intervalo_tempo)))
        arquivo_saida.write("\u0009Volume escoado  = %.4f [m³]\u000A" %(volume_hidrograma))
        
        
    #   Deixar espaco em branco apos \u000A
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    arquivo_saida.write(" ---- CHUVAS DE PROJETO (mm) ---- \u000A\u000A")
    #   Precisa ser declarada
    string_aux = "      dt"
    #   Organizacao do arquivo de saida: ATENCAO! O FOR E' DIFERENTE DO CORPO
    for ii in range(1, (len(precipitacoes_ordenadas) + 1)):
        #   1 a 9
        if ii < 10:    #    "   Chuva 1"
            string_aux += ("   Chuva%2d"%(ii))
        #   10 a 99
        elif ii < 100: #    "   Chuva 10"
            string_aux += ("   Chuva%3d"%(ii))
        #   100 ou mais
        else:          #    "   Chuva 100"
            string_aux += ("   Chuva%4d"%(ii))
    
    #   Organizacao do arquivo de saida
    arquivo_saida.write(string_aux)
    arquivo_saida.write("\u000A")
    
    #   Loop para escrever a chuva
    for jj in range(numero_intervalos_tempo_chuva):
        #   Escrever o intervalo na esquerda do arquivo
        arquivo_saida.write("%8d" %int(jj+1))
        #   Loop para esrever a chuva: ATENCAO! O FOR E' DIFERENTE DO CABECALHO
        for ii in range(len(precipitacoes_ordenadas)):
            #   1 a 9
            if ii < 9: # Aqui e' indice!
                arquivo_saida.write("%10.4f" %(precipitacoes_ordenadas[ii][jj]))
            #   10 a 99
            elif ii < 99: # Aqui e' indice!
                arquivo_saida.write("%11.4f" %(precipitacoes_ordenadas[ii][jj]))
            #   100 ou mais
            else: # Aqui e' indice!
                arquivo_saida.write("%12.4f" %(precipitacoes_ordenadas[ii][jj]))
        #   Nova linha
        arquivo_saida.write("\u000A")
    
    
    #   Deixar espaco em branco apos \u000A
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    arquivo_saida.write(" ---- CHUVAS EFETIVAS (mm) ---- \u000A\u000A")
    #   Precisa ser declarada
    string_aux = "      dt"
    #   Organizacao do arquivo de saida: ATENCAO! O FOR E' DIFERENTE DO CORPO
    for ii in range(1, (len(precipitacoes_efetivas) + 1)):
        #   1 a 9
        if ii < 10:    #    "  Chuva 1"
            string_aux += ("   Chuva%2d"%(ii))
        #   10 a 99
        elif ii < 100: #    "  Chuva 10"
            string_aux += ("   Chuva%3d"%(ii))
        #   100 ou mais
        else:          #    "  Chuva 100"
            string_aux += ("   Chuva%4d"%(ii))

    #   Organizacao do arquivo de saida
    arquivo_saida.write(string_aux)
    arquivo_saida.write("\u000A")
    
    #   Loop para escrever a chuva
    #   Apesar da variavel "precipitacoes_efetivas" terem "numero_intervalos_tempo" termos, escreveremos somente ate' "numero_intervalos_tempo_chuva" pois o excedente e' ZERO.
    for jj in range(numero_intervalos_tempo_chuva): 
        #   Escrever o intervalo na esquerda do arquivo
        arquivo_saida.write("%8d" %int(jj+1))
        #   Loop para esrever a chuva: ATENCAO! O FOR E' DIFERENTE DO CABECALHO
        for ii in range(len(precipitacoes_efetivas)):
            #   1 a 9
            if ii < 9: # Aqui e' indice!
                arquivo_saida.write("%10.4f" %(precipitacoes_efetivas[ii][jj]))
            #   10 a 99
            elif ii < 99: # Aqui e' indice!
                arquivo_saida.write("%11.4f" %(precipitacoes_efetivas[ii][jj]))
            #   100 ou mais
            else: # Aqui e' indice!
                arquivo_saida.write("%12.4f" %(precipitacoes_efetivas[ii][jj]))
                
        #   Nova linha
        arquivo_saida.write("\u000A")


    #   Deixar espaco em branco
    arquivo_saida.write("\u000A------------------------------------------------------------------------\u000A\u000A")
    arquivo_saida.write(" ---- HIDROGRAMAS CHUVA-VAZÃO (m³/s) ----\u000A\u000A")
    #   Precisa ser declarada
    string_aux = "      dt"
    #   Organizacao do arquivo de saida: ATENCAO! O FOR E' DIFERENTE DO CORPO
    for ii in range(1, (len(hidrogramas_saida_pq) + 1)):
        #   1 a 9
        if ii < 10:    #    "  Hidrograma 1"
            string_aux += ("   Hidrograma%2d"%(ii))
        #   10 a 99
        elif ii < 100: #    "  Hidrograma 10"
            string_aux += ("   Hidrograma%3d"%(ii))
        #   100 ou mais
        else:          #    "  Hidrograma 100"
            string_aux += ("   Hidrograma%4d"%(ii))

    #   Organizacao do arquivo de saida
    arquivo_saida.write(string_aux)
    arquivo_saida.write("\u000A")
    
    #   Loop para escrever o hidrograma
    for jj in range(numero_intervalos_tempo):
        #   Escrever o intervalo na esquerda do arquivo
        arquivo_saida.write("%8d" %(jj+1))
        #   Loop para escrever o hidrograma: ATENCAO! O FOR E' DIFERENTE DO CABECALHO
        for ii in range(len(hidrogramas_saida_pq)):
            #   1 a 9
            if ii < 9: # Aqui e' indice!
                arquivo_saida.write("%15.5f" %(hidrogramas_saida_pq[ii][jj]))
            #   10 a 99
            elif ii < 99: # Aqui e' indice!
                arquivo_saida.write("%16.5f" %(hidrogramas_saida_pq[ii][jj]))
            #   100 ou mais
            else: # Aqui e' indice!
                arquivo_saida.write("%17.5f" %(hidrogramas_saida_pq[ii][jj]))
        #   Nova linha
        arquivo_saida.write("\u000A")
    #   Feche o arquivo
    arquivo_saida.close()
#----------------------------------------------------------------------
def plotarPQ(hidrograma, precipitacao_ordenada, precipitacao_efetiva, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """Chama a funcao de plotagem da Hydrolib"""
    plotar_Hidrogramas_PQ(hidrograma, precipitacao_ordenada, precipitacao_efetiva, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao)