# -*- coding: latin_1 -*-

#Versao: 2022-07-06
#        AAAA-MM-DD
"""
Nome:        Hydrolib.py versao 1.0

Objetivo:    Biblioteca didatica para a estimativa de funcoes hidrologicas, 
             disponivel na Internet como codigo aberto, permitindo um ambiente 
             colaborativo para o desenvolvimento de modelos hidrologicos 
             e sua interacao com ferramentas SIG. 

Authores:    Daniel Allasia <dga@ufsm.br>, Vitor Geller <vitorgg_hz@hotmail.com>
             Rutineia Tassi <rutineia@gmail.com>, Lucas Tassinari <lucascstassinari@gmail.com>
             
Copyright:   (c) Daniel Allasia, Vitor Geller, Rutineia Tassi, Lucas Tassinari

================================================================================
Licenca:

    Este programa/biblioteca e um software livre; voce pode redistribui-lo e/ou 
    modifica-lo dentro dos termos da Licenca Publica Geral GNU como 
    publicada pela Fundacao do Software Livre (FSF); na versao 2 da 
    Licenca, ou (na sua opiniao) qualquer versao.

    Este programa e' distribuido na esperanca de que possa ser util, 
    mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUACAO a qualquer
    MERCADO ou APLICACAO EM PARTICULAR. Veja a 
    Licenca Publica Geral GNU para maiores detalhes.

    Voce deve ter recebido uma copia da Licenca Publica Geral GNU
    junto com este programa, se nao, escreva para a Fundacao do Software
    Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.

================================================================================
Description:


  Os metodos aqui descritos estao basados em diferentes fontes de informacao 
  que sao citados dentro de cada biblioteca

================================================================================
Quadro resumo das funcoes da biblioteca:
    
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                NOME                |                                            DESCRICAO                                                  |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
| calcular_PrecipitacaoDesacumulada  |    Calcula a Intensidade a partir da relacao Intensidade-duracao-frequencia (IDF).                    |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|      aplicar_BlocosAlternados      |    Redistribui a chuva de projeto conforme a metodologia dos blocos alternados.                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |    Aplica o metodo de separacao do escoamento superficial pelo metodo desenvolvido pelo National      |
|  calcular_PrecipitacaoEfetiva_CN   |Resources Conservation Center dos EUA (antigo Soil Conservation Service - SCS), apresentado por        |
|                                    |Collischonn e Tassi, 2013.                                                                             |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|         calcular_TC_Kirpich        |    Estima o tempo de concentracao para pequenas bacias pela equacao de Kirpich (menores que 0.5 km^2).|
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|          calcular_HUT_SCS          |    Calcula parametros do hidrograma unitario triangular sintetico.                                    |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|         aplicar_Convolucao         |    Calcula o hidrograma de projeto a partir de de uma serie de dados de chuva efetiva.                |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|      calcular_VazaoSaida_Puls      |    Calcula a curva de extravasao de um reservatorio a partir de suas estruturas.                      |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|            aplicar_Puls            |    Calcula o hidrograma de saida de um reservatorio a partir de uma simulacao de Puls.                |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|     aplicar_MuskingumCunge         |    Calcula o hidrograma de saida de um canal retangular largo a partir de uma simulacao de            |
|                                    |Muskingum-Cunge.                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|         somar_Hidrogramas          |    Soma n hidrogramas resultando em um unico so'.                                                     |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|     plotar_Hidrogramas_PQ          |    Plota e salva os graficos gerados nas operacoes chuva-vazao.                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|       plotar_Hidrogramas_PULS      |    Plota e salva os graficos gerados nas operacoes de propagacoes de reservatorios de Puls.           |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|     plotar_Hidrogramas_MKC         |    Plota e salva os graficos gerados nas operacoes de propagacoes de canais de Muskingum-Cunge.       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|     plotar_somar_Hidrogramas       |    Plota e salva os graficos gerados nas operacoes de juncoes.                                        |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
"""
#------------------------------------------------------------------------
def calcular_PrecipitacaoDesacumulada(numero_intervalos_tempo_chuva, duracao_intervalo_tempo_s, tempo_retorno_anos, a, b, c, d, limite_minutos):
    """
    Calcula a chuva desacumulada a partir da IDF a seguir:
 
        I [mm/h] = (a*TR^b) / ((t+c)^d)
        
    A funcao retorna a precipitacao desacumulada em uma variavel do tipo array de floats.
        precipitacao_desacumulada = [...]

    Parametros para uso:
        -> numero_intervalos_tempo_chuva: Int que representa o numero de intervalos de tempo COM CHUVA da operacao.
        -> duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        -> tempo_retorno_anos : Int que representa o tempo de retorno [anos].
        -> a,b,c,e: Floats que representam os valores dos parametros da IDF.
        -> limite_minutos: Int que representa o limite das intensidades de chuva iniciais [minutos].
            Exemplo: limite_minutos = 10 -> Se limite_minutos = 10: As intensidades de chuva (em mm/h) dos 10 minutos iniciais da 
                                    chuva serao iguais 'a intensidade de chuva calculada para o intervalo referente aos 10 minutos.
                                    OBS: Note que o numero de intervalos de tempo necessarios para completar os 10 minutos
                                    de chuva varia conforme a duracao do intervalo de tempo estipulado.
    """
    #   Algoritmo original escrito por Lucas Tassinari.
    #   Versao atual do algoritmo escrito por Vitor Geller.
    
    from numpy import array, float64
    
    #   evito divisao inteira
    duracao_intervalo_tempo_s = float(duracao_intervalo_tempo_s)
    tempo_retorno_anos        = float(tempo_retorno_anos)
    
    #   ATENCAO: Calcula-se a chuva ACUMULADA com precipitacao_desacumulada, porem DESACUMULA-SE a variavel no final da funcao
    precipitacao_desacumulada = array([0.0 for ii in range(numero_intervalos_tempo_chuva)], float64)
    
    #   Algoritmo que limita a intensidade dos intervalos iniciais
    for ii in range(numero_intervalos_tempo_chuva):
        #   Implementa-se a funcionalidade de limitacao de intensidades
        if (ii+1) * duracao_intervalo_tempo_s > limite_minutos * 60:
            #   Caso tempo superou o limite estipulado
            precipitacao_desacumulada[ii] = (a*((tempo_retorno_anos)**b))/(((ii+1)*duracao_intervalo_tempo_s/60.+c)**d) * (ii+1) * (duracao_intervalo_tempo_s / 3600.0)
        else:
            #   Caso tempo superou ainda nao limite estipulado: utiliza-se o limite
            precipitacao_desacumulada[ii] = (a*((tempo_retorno_anos)**b))/((limite_minutos+c)**d) * (ii+1) * (duracao_intervalo_tempo_s / 3600.0)
    
    #   Processo de desacumulacao da variavel precipitacao_desacumulada
    for ii in range((numero_intervalos_tempo_chuva-1),0,-1):
        precipitacao_desacumulada[ii] -= precipitacao_desacumulada[ii-1]
    
    #   ATENCAO: A partir dessa linha a precipitacao_desacumulada esta' DESACUMULADA
    
    #   Retorne
    return precipitacao_desacumulada
#------------------------------------------------------------------------
def aplicar_BlocosAlternados(precipitacao_desacumulada, numero_intervalos_tempo_chuva, posicao_pico_porcentdecimal):
    """
    Aplica o metodo dos blocos alternados a partir de uma serie de dados de chuva desacumulada e retorna a precipitacao ordenada.
    
    No metodo dos blocos alternados, os valores incrementais sao reorganizados 
    de forma que o maximo incremento ocorra, aproximadamente, no meio da duracao 
    da chuva total. Os incrementos (ou blocos de chuva) seguintes sao organizados 
    a direita e a esquerda alternadamente, ate preencher toda a duracao, segundo 
    Collischonn e Tassi, 2013.
    
    Esta funcao retorna a chuva ordenada em uma variavel do tipo array de floats.
        precipitacao_ordenada = [...]

    Parametros para uso:
        -> precipitacao_desacumulada: List/array que representa os dados de chuva desacumulada.
            Exemplo: precipitacao_desacumulada = [...] -> Dados de chuva desacumulada [em mm].
            OBS: A variavel precipitacao_desacumulada DEVE estar em ordem DECRESCENTE.
        -> numero_intervalos_tempo_chuva: Int que representa o numero de intervalos de tempo COM CHUVA da operacao.
        -> posicao_pico_porcentdecimal: Int que representa a posicao da maior precipitacao desacumulada em porcentagem decimal.
             Exemplo: posicao_pico_porcentdecimal = 0.5 -> Pico em 50 porcento do tempo da simulacao
                      posicao_pico_porcentdecimal = 0.2 -> Pico em 20 porcento do tempo da simulacao
    """
    #   Algoritmo original escrito por Daniel Allasia.
    #   Versao atual do algoritmo escrito por Vitor Geller.
    
    #   Imports
    from numpy import array, float64
    
    #   Se posicao_pico_porcentdecimal for zero
    if (float(posicao_pico_porcentdecimal) == 0.0):
        indice_pico = 0
    #   Se numero_intervalos_tempo_chuva for par
    elif numero_intervalos_tempo_chuva % 2 == 0:
        indice_pico = (int(posicao_pico_porcentdecimal*numero_intervalos_tempo_chuva)-1)
    #   Se numero_intervalos_tempo_chuva for impar
    elif numero_intervalos_tempo_chuva % 2 == 1:
        indice_pico = int(posicao_pico_porcentdecimal*numero_intervalos_tempo_chuva)
        
    #   Declaracoes
    precipitacao_ordenada = array([0.0 for ii in range(numero_intervalos_tempo_chuva)], float64)
    #   Variavel de posicao necessaria para correto funcionamento do laco for
    indice_pdes = 0
    
    #   Se impar: valor central; Se par: arredondado para baixo; - correspondente ao maior bloco de chuva
    precipitacao_ordenada[indice_pico] = precipitacao_desacumulada[indice_pdes] 
    
    #   Otimizacao: Determinar o numero de iteracoes no FOR: 
    #   Sempre que possivel dois valores serao distribuidos em cada iteracao do FOR, assim, reduz-se o numero de iteracoes necessarias
    if posicao_pico_porcentdecimal < 0.5:
        #   Nem sempre sera' necessario rodar o for ate' o fim: +2 para evitar que falte algum bloco para ser distrubuido
        numero_iteracoes = int((numero_intervalos_tempo_chuva*(1.0-posicao_pico_porcentdecimal))+2) # melhor fazer a mais do que faltar
    else:
        #   Nem sempre sera' necessario rodar o for ate' o fim: +2 para evitar que falte algum bloco para ser distrubuido
        numero_iteracoes = int((numero_intervalos_tempo_chuva*posicao_pico_porcentdecimal)+2) # melhor fazer a mais do que faltar
    
    #   For para distrubuir os blocos de chuva restantes
    #   A mudanca do WHILE para o FOR mostrou-se ser de 20%~40% mais eficiente, dependendo da posicao do pico infomada.
    for indice_ordenacao in range(1, numero_iteracoes):
        #   Comeco loop sempre verificando se e' possivel colocar um valor na direita do pico
        if (indice_pico + indice_ordenacao) < numero_intervalos_tempo_chuva: # Se for == ele nao entra
            #   Aumentar o indice de precipitacao_desacumulada em uma unidade para poder copiar o proximo valor de precipitacao_desacumulada
            indice_pdes += 1  
            #   Entro com o valor na direita
            precipitacao_ordenada[(indice_pico + indice_ordenacao)] = precipitacao_desacumulada[indice_pdes] 
        #   Verifico se e' possivel colocar um valor a esquerda do pico
        if (indice_pico - indice_ordenacao) >= 0: # Aqui pode ser igual, porque trata-se de indice (o primeiro e' zero)
            #   Aumentar o indice de precipitacao_desacumulada em uma unidade para poder copiar o proximo valor de precipitacao_desacumulada
            indice_pdes += 1 
            #   Entro com o valor na esquerda
            precipitacao_ordenada[(indice_pico - indice_ordenacao)] = precipitacao_desacumulada[indice_pdes] 
    
    #   Retorne
    return precipitacao_ordenada
#------------------------------------------------------------------------
def calcular_PrecipitacaoEfetiva_CN(coeficiente_cn, precipitacao_ordenada, numero_intervalos_tempo_chuva):
    """
    Aplica o metodo de separacao do escoamento superficial pelo metodo desenvolvido 
    pelo National Resources Conservation Center dos EUA (antigo Soil Conservation Service - SCS)
    segundo Collischonn e Tassi, 2013.
    
    A funcao retorna a precipitacao efetiva em uma variavel do tipo array de floats.
        precipitacao_efetiva = [...]
        
    Parametros para uso:
        -> coeficiente_cn: Float que representa o parametro adimensional tabelado que varia de 0 a 100.
        -> precipitacao_ordenada: List/array que representa os dados de chuva ordenada.
            Exemplo: precipitacao_ordenada = [...] -> Dados de chuva ordenada [em mm].
        -> numero_intervalos_tempo_chuva: Int que representa o numero de intervalos de tempo COM CHUVA da operacao.
    """
    #   Algoritmo original escrito por Lucas Tassinari 
    #   Versao atual do algoritmo escrito por Vitor Geller.
    
    #   Imports
    from numpy import array, float64
    
    #   Declaracoes:
    precipitacao_efetiva = array([0.0 for ii in range(numero_intervalos_tempo_chuva)], float64)
    #   Correcao de bug: Nao era possivel acumular a propria variavel precipitacao_ordenada devido a maneira que fora usada para acumular (operacao +=)
    #   Isso possivelmente seja um bug do interpretador, fui forcado a declarar uma variavel nova e copiar valor a valor por questoes de eficiencia...
    #   ... pois e' mais rapido declarar uma nova variavel e acumular do que acumular e desacumular a original
    precipitacao_ordenada_acumulada = array([0.0 for ii in range(numero_intervalos_tempo_chuva)], float64)
    #   Armazenamento no solo [mm]
    S = (25400.0 / coeficiente_cn) - 254
    #   Perdas iniciais [mm]
    Ia = 0.2 * S
    
    #   Acumularei a variavel de precipitacao ordenada
    precipitacao_ordenada_acumulada[0] = precipitacao_ordenada[0]
    #   Faco somente ate' numero_intervalos_tempo_chuva, o primeiro ja' esta' feito
    for ii in range(1,numero_intervalos_tempo_chuva):
        #   Processo de acumulacao
        precipitacao_ordenada_acumulada[ii] = precipitacao_ordenada_acumulada[ii-1] + precipitacao_ordenada[ii]
    
    #   Precipitacao efetiva acumulada SCS
    #   ATENCAO: Ao final desse laco a variavel precipitacao_efetiva estara' ACUMULADA, deve-se DESACUMULA'-LA em seguida
    for ii, POrdAcum in enumerate(precipitacao_ordenada_acumulada):
        #   Faco o calculo ate' numero_intervalos_tempo_chuva
        if POrdAcum > Ia:
            #   Aplicacao da equacao do CN: PEfAcum = (POrdAcum - Ia)**2/(POrdAcum - Ia + S)
            precipitacao_efetiva[ii] = ((POrdAcum - Ia) ** 2)/float((POrdAcum - Ia + S))
    
    #   Processo de desacumulacao da variavel precipitacao_efetiva
    #   Faco o calculo a partir do ultimo indice (numero_intervalos_tempo_chuva-1) ate' o segundo indice (1)
    for ii in range((numero_intervalos_tempo_chuva-1),0,-1):
        precipitacao_efetiva[ii] -= precipitacao_efetiva[ii-1]
        
    #   ATENCAO: A partir dessa linha a precipitacao_efetiva esta' DESACUMULADA
    
    #   Retorne
    return precipitacao_efetiva
#------------------------------------------------------------------------
def calcular_TC_Kirpich(diferenca_cota_m, comprimento_canal_km):
    """
    Equacao de Kirpich desenvolvida empiricamente para estimar o tempo de concentracao de pequenas bacias (menores que 0.5 km^2).
    
    A funcao retorna o resultado estimado para o tempo de concentracao em HORAS em uma float.
    
    Parametros para uso:
        -> diferenca_cota_m: Float que representa a diferenca de altitude ao longo do curso d'agua principal [metros].
        -> comprimento_canal_km: Float que representa o comprimento do curso d'agua principal [quilometros].
    """
    #   Algoritmo original escrito por Lucas Tassinari.
    #   Versao atual do algoritmo escrito por Vitor Geller.
    
    #   Tempo de concentracao em HORAS
    return ((57 * ((comprimento_canal_km**3)/diferenca_cota_m)**0.385) / 60.0)
#------------------------------------------------------------------------
def calcular_HUT_SCS(tempo_concentracao_horas, area_km2, duracao_intervalo_tempo_s):
    """
    Retorna valores (Tempo de subida [horas], Vazao de pico [horas] e Tempo de base [horas]) do hidrograma unitario sintetico.
    
    Todas as variaveis retornadas por esta funcao sao do tipo float.
    
    Parametros:
        -> tempo_concentracao_horas: Float que representa o tempo de concentracao da bacia [horas].
        -> area_km2: Float que representa a area da bacia [km^2].
        -> dt: Int que representa a duracao do intervalo de tempo [em segundos].
    """
    #   Algoritmo original escrito por Lucas Tassinari.
    #   Versao atual do algoritmo escrito por Vitor Geller.
    
    Tempo_pico = 0.6 * tempo_concentracao_horas #TC em HORAS!
    tempo_subida_h = Tempo_pico + duracao_intervalo_tempo_s/7200.0 #O dito "Tp" da maioria dos livros. Tempo total de subida, desde origem.
    vazao_pico_hut_m3s = 0.208 * area_km2 / tempo_subida_h  #Vazao de pico em metros cubicos por segundo
    tempo_base_h = 2.67 * tempo_subida_h

    return tempo_subida_h, vazao_pico_hut_m3s, tempo_base_h
#------------------------------------------------------------------------
def aplicar_Convolucao(tempo_base_h, vazao_pico_hut_m3s, tempo_subida_h, duracao_intervalo_tempo_s, numero_intervalos_tempo, numero_intervalos_tempo_chuva, precipitacao_efetiva):
    """
    Calcula o hidrograma de projeto a partir de uma serie de dados de chuva efetiva.
    
    O hidrograma e' retornado em uma variavel do tipo array de floats [em m³/s].
        hidrograma = [...]
    
    Parametros para uso:
        -> tempo_base_h: Float que representa o tempo total do HUT (toda a base do triangulo, da origem ao fim) [horas].
        -> vazao_pico_hut_m3s: Float que representa a vazao de pico do HUT (maior ordenada do triangulo) [m3/s].
        -> tempo_subida_h: Float que representa o tempo total de subida do HUT, desde sua origem [horas].
        -> duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        -> numero_intervalos_tempo: Int que representa o numero de intervalos de tempo da operacao.
        -> numero_intervalos_tempo_chuva: Int que representa o numero de intervalos de tempo COM CHUVA da operacao.
        -> precipitacao_efetiva: List/array que representem os dados de chuva efetiva.
            Exemplo: precipitacao_efetiva = [...] -> Dados de chuva efetiva [em mm].
    """
    #   Algoritmo original escrito por Lucas Tassinari.
    #   Versao atual do algoritmo escrito por Vitor Geller.
    
    from numpy import array, float64
    
    #   Coeficientes das retas que formam o HU Sintetico
    coef_A_subida = float(vazao_pico_hut_m3s) / tempo_subida_h
    #coef_B_subida = 0. # Nao existe: esta' aqui para lembrar o leitor que o HU e' um triangulo e pode ser representado por duas retas
    coef_A_descida = - float(vazao_pico_hut_m3s) / (1.67 * tempo_subida_h)
    coef_B_descida = 2.67 * vazao_pico_hut_m3s / 1.67
    
    #   Determinar quantos termos o HU tera'
    numero_termos_hu = int(tempo_base_h * 3600 / duracao_intervalo_tempo_s)
    
    #   Variavel para armazenar os valores do HUT Sintetico
    hidrograma_unitario = array([0.0 for ii in range(numero_termos_hu)], float64)
    
    #   Preencher os valores do hidrograma unitario: somente aqueles que nos interessam
    #   Por questoes de otimizacao, nao se preenchem os valores nulos
    for ii in range(numero_termos_hu):
        #   Calcular o tempo decorrido em horas; nao calculam-se termos nulos, entao: (ii+1)
        tempo_em_horas = (duracao_intervalo_tempo_s * (ii+1) / 3600.0)
        #   Avaliar qual das retas utilizar.
        if (tempo_em_horas <= tempo_subida_h):
            #   Caiu na reta de subida
            hidrograma_unitario[ii] = coef_A_subida * tempo_em_horas
        #   Curva descendente: Por mais que seja verdadeiro enquanto (tempo_em_horas <= tempo_subida_h), essa condicao nao trigga pois a outra trigga antes
        elif (tempo_em_horas < tempo_base_h):
            #   Caiu na reta de descida
            hidrograma_unitario[ii] = ((coef_A_descida * tempo_em_horas) + coef_B_descida)
    
    #   Variavel que armazena os valores do hidrograma de projeto
    hidrograma = array([0.0 for ii in range(numero_intervalos_tempo)], float64) 
    #   Variaveis auxiliares
    indice_pef = 0 # Armazena o indice das chuvas efetivas
    limite_superior_hu = -1 # Armazena indices do HU
    limite_inferior_hu = -1 # Armazena indices do HU
    
    #   Preparacao para a convolucao
    #   Determinar quantos intervalos do hidrograma devem ser calculados
    if (numero_intervalos_tempo_chuva + numero_termos_hu) > numero_intervalos_tempo:
        #   Como a simulacao termina antes do fim do escoamento, calcula-se somente ate' o fim da simulacao
        numero_intervalos_calculo = int(numero_intervalos_tempo)
    else:
        #   Como o escoamento termina antes que a simulacao, calcula-se ate' o escoamento cessar; CONTUDO, o restante dos intervalos serao todos zero
        numero_intervalos_calculo = int(numero_intervalos_tempo_chuva + numero_termos_hu)
    
    #   Apesar de ser mais complexo, o algoritmo a seguir mostrou-se aproximadamente 90% mais rapido que o antigo
    #   O foco e' realizar somente os calculos que resultam em valores nao nulos
    #   Loop das linhas: inicio na segunda pois a primeira e' sempre zero em funcao do primeiro termo do HU
    for linha in range(1,numero_intervalos_calculo):
        #   Determinar o numero de termos na linha da convolucao
        #   Determinar tambem o indice da primeira chuva efetiva dessa linha da convolucao
        if linha <= numero_termos_hu:
            #   Nos intervalos iniciais, aumenta-se o numero de termos da convolucao por meio do aumento do limite superior
            #   No exemplo didatico apresentado a seguir correspondem aos termos Q(1) e Q(2)
            limite_superior_hu += 1
            #   Nessas condicoes inicia-se sempre do primeiro pulso de chuva
            indice_pef = 0
        #   Ou seja: linha > numero_termos_hu: Todos os termos de HU estao contribuindo no calculo;
        #   No exemplo didatico apresentado a seguir correspondem aos termos Q(3), Q(4) e Q(5)
        else:
            #   Nessas condicoes deve-se calcular o primeiro indice de chuvas a ser utilizado
            #   Se (nint_tempo >= nint_tempo_chuva + numero_termos_hu): max(indice_pef) == nint_tempo_chuva
            #   Se (nint_tempo <  nint_tempo_chuva + numero_termos_hu): max(indice_pef) == nint_tempo - numero_termos_hu
            indice_pef = int(linha - numero_termos_hu)
        
        #   Ajustar a quantidade de valores do HU utilizados nessa linha da convolucao
        if linha > numero_intervalos_tempo_chuva:
            #   Nos intervalos finais, reduz-se o numero de termos da convolucao por meio do aumento do limite inferior
            #   No exemplo didatico apresentado a seguir correspondem aos termos Q(6) e Q(7)
            limite_inferior_hu +=1
        
        #   Loop das colunas: de tras para frente, por isso: (superior, inferior, -1)
        for coluna in range(limite_superior_hu,limite_inferior_hu,-1):
            #   EXEMPLO DIDATICO DA CONVOLUCAO                         | Sobre o funcionamento das variaveis de limite:
            #   Q(1) = Pef1.h1                                         | limite_superior_hu += 1 == 1 termo(s); ordem: 1
            #   Q(2) = Pef1.h2 + Pef2.h1                               | limite_superior_hu += 1 == 2 termo(s); ordem: 2,1
            #   Q(3) = Pef1.h3 + Pef2.h2 + Pef3.h1                     | limite_superior_hu += 1 == 3 termo(s); ordem: 3,2,1
            #   Q(4) =           Pef2.h3 + Pef3.h2 + Pef4.h1           |                         == 3 termo(s); ordem: 3,2,1
            #   Q(5) =                     Pef3.h3 + Pef4.h2 + Pef5.h1 |                         == 3 termo(s); ordem: 3,2,1
            #   Q(6) =                               Pef4.h3 + Pef5.h2 | limite_inferior_hu += 1 == 2 termo(s); ordem: 3,2
            #   Q(7) =                                         Pef5.h3 | limite_inferior_hu += 1 == 1 termo(s); ordem: 3
            #   FONTE: Adaptado de Introduzindo Hidrologia, IPH UFRGS, |
            #   Agosto 2008, p.115, Walter Collischonn, Rutineia Tassi |
            
            #   O proximo comando calcula a linha da convolucao de tras para frente; Exemplo: Para Q3: calcula-se Pef1.h3, em seguida Pef2.h2 e por final Pef3.h1.
            #   Para calcular o hidrograma de projeto (linha da convolucao), multiplica-se cada valor de chuva efetiva pelo valor de HU correspondente.
            hidrograma[linha] += precipitacao_efetiva[indice_pef]*hidrograma_unitario[coluna] 
            #   Atualizar indice de chuvas
            indice_pef += 1
        
    #   Retorna o hidrograma calculado (arranjo e' um vetor com nint_tempo valores)
    return hidrograma
#------------------------------------------------------------------------
def calcular_VazaoSaida_Puls(estruturas_extravasao, curva_cota_m):
    """
    Calcula a curva de extravasao de um reservatorio a partir de suas estruturas.
        
    Ela retorna uma lista que contem duas listas.
        variavel_retornada = [[...],[...]]: 
            -> O primeiro bloco [...] representa as cotas [m] utilizadas para construir a curva de extravasao.
            -> O segundo bloco [...] representa os valores de vazao resultante das extruturas [m3/s].
    
    Parametros para uso:
        -> estruturas_extravasao: Lista que contem a informacao necessaria para calcular a vazao extravasada 
        por cada estrutura.
            -> Esta variavel e' estruturada da seguinte forma:
            estruturas_extravasao = [[...], [...], [...], ...] -> cada bloco [...] representa uma estrutura 
            (nao ha' limite de estruturas), que podem ser:
                Exemplo Vertedor: ["VERTEDOR", 1.5, 10, 25, 30] 
                    -> String informando o tipo da estrutura;
                    -> coeficiente C da estrutura;
                    -> comprimento de soleira (m);
                    -> cota de soleira do vertedor (m).
                    -> cota maxima do vertedor (m);
                Exemplo Orificio: ["ORIFICIO", 0.6, 1.5, 20]
                    -> String informando o tipo da estrutura;
                    -> coeficiente C da estrutura;
                    -> altura/diametro do orificio (m);
                    -> cota do centro do orificio (m).
                -> OBS: A string usada para indicar o nome da estrutura deve ser escrita toda em maiuscula e 
                sem acentos: "VERTEDOR" ou "ORIFICIO"
        
        -> curva_cota_m: Lista que representa as cotas da curva cota-volume.
            Exemplo: curva_cota_m = [ ...... ] -> Valores de cota (m).
            OBS: OS VALORES DE COTA DEVEM ESTAR ORDENADOS DE MODO CRESCENTE (do menor ao maior).
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    from math import acos, sin, pi
    
    #   Criarei a curva de extravasao com algumas cotas notaveis, tais cotas sao escolhidas de modo a evitar alguns bugs e facilitar a programacao
    alturas_calculadas = []
    
    #   Loop para reunir as informacoes de cota de cada estrutura
    for estrutura in estruturas_extravasao:
        #   Se for orificio...
        if estrutura[0] == "ORIFICIO":
            if not (estrutura[3] - (estrutura[2]/2.)) in alturas_calculadas:
                alturas_calculadas.append(estrutura[3] - (estrutura[2]/2.)) #cota do centro do orificio - raio 
        #   Se for vertedor...
        elif estrutura[0] == "VERTEDOR":
            if not estrutura[3] in alturas_calculadas:
                alturas_calculadas.append(estrutura[3]) # Soleira
            if not estrutura[4] in alturas_calculadas:
                alturas_calculadas.append(estrutura[4]) # Cota maxima
    
    #   Adicionar as cotas da curva cota-VOLUME
    for ii, cota in enumerate(curva_cota_m):
        if (not cota in alturas_calculadas):
            alturas_calculadas.append(cota)
    
    #   Ordena-se as alturas em ordem crescente!
    alturas_calculadas.sort() 
    
    #   Cria-se uma variavel de 0s para cada ponto que sera' calculada
    curva_vazao = [0. for ii in range(len(alturas_calculadas))]
    
    #   Loop dos niveis de agua
    for ii, cota_agua in enumerate(alturas_calculadas):
        #   Resetar a variavel em cada novo nivel analisado
        vazao_cota = 0.0
        
        #   Loop iterando estruturas
        for estrutura in estruturas_extravasao: # analisando todas as estruturas com um certo nivel de agua.  
            
            #    Se for vertedor com carga
            if estrutura[0] == "VERTEDOR":
                #    Ver se o vertedor possui carga de agua
                if cota_agua > estrutura[3]:
                    #   p. 398, HIDRAULICA BASICA, 4ed., Rodrigo de Melo Porto
                    #   Descarregadores de Barragens: Qd = Co*L*(Hd**1.5)
                    vazao_cota += (estrutura[1] * estrutura[2] * ((cota_agua - (estrutura[3]))**(1.5)))
            
            #   Se for orificio...
            elif estrutura[0] == "ORIFICIO":
                area_orificio = (pi * estrutura[2]**2)/4.
                #   A fim de resolver uma descontinuidade na funcao de extravasao, resolveu-se fazer essa simplificacao:
                #   Aplicando a equacao dos orificios em cotas y/d >= 0.75 (mesmo que o mesmo nao esteja afogado)
                #   Porem aqui, o orificio sera' resolvido por interpolacao linear ja' a cota de agua esta' abaixo de 75% (y/d < 0.75)
                if (cota_agua < (estrutura[3] + (estrutura[2]/4.))) and (cota_agua > (estrutura[3] - (estrutura[2]/2.))):
                    #   Calcular para y/d = 0.75: Lei dos Orificios: Q = C*Ao*((2*G*H)**0.5)
                    vazao075 = (estrutura[1] * area_orificio * ((2.0 * 9.81 * (estrutura[2]/4.))**0.5))
                    #   Interpolar linearmente para as demais cotas
                    #   vazao(y/d=0.75) * (cota_agua - (cota_centro - D/2) / (D*0.75))
                    vazao_cota += (vazao075) * ((cota_agua - (estrutura[3] - (estrutura[2] / 2.))) / (estrutura[2] * 3. / 4.))
                #   A fim de resolver uma descontinuidade na funcao de extravasao, resolveu-se fazer essa simplificacao:
                #   Aplicando a equacao dos orificios em cotas acima de 75% (y/d >= 0.75)
                #   Portanto, a partir dessa cota considera-se a equacao dos orificios
                elif cota_agua >= (estrutura[3] + (estrutura[2]/4.)):
                    #   p. 355, HIDRAULICA BASICA, 4ed., Rodrigo de Melo Porto
                    #   Lei dos Orificios: Q = C*Ao*((2*G*H)**0.5)
                    vazao_cota += (estrutura[1] * area_orificio * ((2.0 * 9.81 * (cota_agua - (estrutura[3])))**0.5))
                
        #   Feito a verificacao de todas as estruturas, posso armazenar o valor de vazao encontrado e calcular a proxima altura
        curva_vazao[ii] = vazao_cota
    
    return [alturas_calculadas, curva_vazao]
#------------------------------------------------------------------------
def aplicar_Puls(curva_cota_volume, hidrograma_entrada, by_pass, curva_cota_vazao, cota_inicial_m, numero_intervalos_tempo, duracao_intervalo_tempo_s):
    """
    Calcula o hidrograma de saida de um reservatorio a partir de uma simulacao de Puls. 
    
    A funcao retorna dois arrays de floats:
        hidrograma_saida = [...]: Valores do hidrograma de saida do reservatorio [m³/s].
        cota_reservatorio = [...]: Valores de cota do reservatorio [m].
    
    Parametros para uso:
        -> curva_cota_volume: Lista que contem a informacao da curva cota-volume do reservatorio.
            Exemplo: curva_cota_volume = [[...], [...]] -> Em que o primeiro bloco [...] contem somente dados de cota [em metros], 
            e o segundo bloco [...] contem somente dados de volume [10^3 metros³]. Ambas DEVEM estar em ordem CRESCENTE.
            OBS: O primeiro par ordenado deve ser cota 0 e volume 0.
        -> hidrograma_entrada: List/array que contem os dados do hidrograma de entrada do reservatorio.
            Exemplo: hidrograma_entrada = [...] -> Dados de entrada de vazao [em metros^3/s].
        -> by_pass = Float que representa a vazao maxima que passa pelo by-pass [em metros^3/s].
            caso by_pass for igual a zero, significa que nao ha' a presenca de by-pass no reservatorio (reservatorio on-line).
        -> curva_cota_vazao: Lista que contem a informacao da curva cota-vazao de extravasao do reservatorio.
            Exemplo: curva_cota_vazao = [[...], [...]] -> Em que o primeiro bloco [...] contem somente dados de cota [em metros], 
            e o segundo bloco [...] contem somente dados de vazao [metros³/s]. Ambas DEVEM estar em ordem CRESCENTE.
        -> cota_inicial_m: Float que representa a cota inicial do reservatorio.
        -> numero_intervalos_tempo: Int que representa o numero de intervalos de tempo da operacao.
        -> duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [segundos].
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    from numpy import array, float64
    
    #   Optou-se por nao utilizar bibliotecas customizadas para calcular as interpolacoes e
    # extrapolacoes, facilitando o uso da funcao por nao demandar pacotes customizados, porem,
    # sob a pena de demandar um pouco mais de tempo de processamento.
    
    #   Adaptar as cotas da curva cota-VOLUME para possuirem os mesmos valores de cota da curva cota-VAZAO
    for ii, cota in enumerate(curva_cota_vazao[0]):
        if not cota in curva_cota_volume[0]:
            curva_cota_volume[0].append(cota)
            curva_cota_volume[1].append(-1)
            #   Calcular o volume dessa cota por interpolacao linear
            indice_cota = 0
            while cota > curva_cota_volume[0][indice_cota]:
                indice_cota += 1
            #   Calcular o volume por interpolacao linear
            curva_cota_volume[1][-1] = curva_cota_volume[1][indice_cota-1] + (((cota - curva_cota_volume[0][indice_cota-1])*(curva_cota_volume[1][indice_cota] - curva_cota_volume[1][indice_cota-1]))/(curva_cota_volume[0][indice_cota] - curva_cota_volume[0][indice_cota-1]))
    
    #   Reordenar em ordem crescente
    curva_cota_volume[0].sort()
    curva_cota_volume[1].sort()
    
    #   Criar uma tabela que represente a soma (2S/dt+Q)
    S2dtQ             = [0.0 for ii in range(len(curva_cota_vazao[0]))]
    hidrograma_saida  = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    cota_reservatorio = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    volume_reservado  = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    vazoes_by_pass    = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    
    # Uma variavel por vez e' resolvida,
    # sob a pena de termos um codigo maior, porem, mais organizado.
    
    #   Calcular os valores de saida de vazao nas alturas de CCVol: Criar a "tabela" dos valores desconhecidos do metodo
    for ii, cota in enumerate(curva_cota_vazao[0]):
        #   Calcular a vazao de saida
        #   Se cota avaliada esta' abaixo da primeira estrutura de extravasao ou na mesma cota
        if cota <= curva_cota_vazao[0][0]:
            #   Nao ha' vazao de saida: estruturas nao estao operando ainda
            vazao_saida = 0.0
            
        #   Se a cota avaliada esta' em algum valor compreendido pela curva de extravasao
        elif (cota > curva_cota_vazao[0][0]) and (cota <= curva_cota_vazao[0][-1]):
            #   Encontrar o indice
            indice_cota = 0 # Armazena o indice da cota de CCVazao cujo valor e' imediatamente superior 'a cota do laco da CCVol
            while cota > curva_cota_vazao[0][indice_cota]:
                indice_cota += 1
                
            #   Interpole o seu valor
            vazao_saida = curva_cota_vazao[1][indice_cota-1] + (((cota - curva_cota_vazao[0][indice_cota-1])*(curva_cota_vazao[1][indice_cota] - curva_cota_vazao[1][indice_cota-1]))/(curva_cota_vazao[0][indice_cota] - curva_cota_vazao[0][indice_cota-1]))
            
        #   Se a cota avaliada esta' ACIMA dos valores compreendidos pela curva de extravasao
        #   Nao acho que ocorrera', ja' que ambas as curvas sao construidas com valor maximo igual 'a maior cota da CCV
        #   De qualquer forma, deixarei programado para evitar eventuais bugs
        else:
            #   Extrapole o valor, extrapolacao linear
            vazao_saida = curva_cota_vazao[1][-2] + (((cota-curva_cota_vazao[0][-2])*(curva_cota_vazao[1][-1]-curva_cota_vazao[1][-2]))/(curva_cota_vazao[0][-1]-curva_cota_vazao[0][-2]))
        
        #   Construo a tabela que relaciona nivel, volume, vazao de saida e o termo 2S/dt+Q
        S2dtQ[ii] = (((2 * curva_cota_volume[1][ii] * (10**3))/(duracao_intervalo_tempo_s)) + vazao_saida)
    
    #   Condicoes iniciais do reservatorio
    cota_reservatorio[0] = cota_inicial_m
    
    #   Vazao de saida inicial:
    #   Se a cota do reservatorio esta' com valores negativos por algum motivo
    if cota_reservatorio[0] <= curva_cota_vazao[0][0]:
        #   Nao ha' vazao de saida: hidrograma[0] = 0.0
        hidrograma_saida[0] = 0.0
        
    #   Cota inicial do reservatorio entre o min e o max das cotas de extravasao
    elif (cota_reservatorio[0] > curva_cota_vazao[0][0]) and (cota_reservatorio[0] <= curva_cota_vazao[0][-1]):
        #   Encontrar o indice
        indice_cota = 0 # Armazena o indice da cota de CCVazao cujo valor e' imediatamente superior 'a cota do laco da CCVol
        while cota_reservatorio[0] > curva_cota_vazao[0][indice_cota]:
            indice_cota += 1
            
        #   Interpole o seu valor
        hidrograma_saida[0] = curva_cota_vazao[1][indice_cota-1] + (((cota_reservatorio[0]-curva_cota_vazao[0][indice_cota-1])*(curva_cota_vazao[1][indice_cota]-curva_cota_vazao[1][indice_cota-1]))/(curva_cota_vazao[0][indice_cota]-curva_cota_vazao[0][indice_cota-1]))
        
    #   Cota inicial do reservatorio acima do max das cotas de extravasao
    else:
        #   Extrapole o valor, extrapolacao linear
        hidrograma_saida[0] = curva_cota_vazao[1][-2] + (((cota_reservatorio[0]-curva_cota_vazao[0][-2])*(curva_cota_vazao[1][-1]-curva_cota_vazao[1][-2]))/(curva_cota_vazao[0][-1]-curva_cota_vazao[0][-2]))
    
    #   Armazenamento inicial:
    #   Se a cota do reservatorio esta' negativa
    if cota_reservatorio[0] <= curva_cota_volume[0][0]:
        #   Nao ha' volume de saida: volume[0] = 0.0
        volume_reservado[0] = 0.0
        
    #   Cota inicial do reservatorio entre o min e o max das cotas de volume
    elif (cota_reservatorio[0] > curva_cota_volume[0][0]) and (cota_reservatorio[0] <= curva_cota_volume[0][-1]):
        #   Encontrar o indice
        indice_cota = 0 # Armazena o indice da cota de CCVazao cujo valor e' imediatamente superior 'a cota do laco da CCVol
        while cota_reservatorio[0] > curva_cota_volume[0][indice_cota]:
            indice_cota += 1
            
        #   Interpole o seu valor
        volume_reservado[0] = (curva_cota_volume[1][indice_cota-1] + (((cota_reservatorio[0]-curva_cota_volume[0][indice_cota-1])*(curva_cota_volume[1][indice_cota]-curva_cota_volume[1][indice_cota-1]))/(curva_cota_volume[0][indice_cota]-curva_cota_volume[0][indice_cota-1])))
        
    #   Cota inicial do reservatorio acima do max das cotas de volume
    else:
        #   Extrapole o valor, extrapolacao linear
        volume_reservado[0] = (curva_cota_volume[1][-2] + (((cota_reservatorio[0]-curva_cota_volume[0][-2])*(curva_cota_volume[1][-1]-curva_cota_volume[1][-2]))/(curva_cota_volume[0][-1]-curva_cota_volume[0][-2])))
    
    #   Antes de iniciar o calculo do metodo, aplico o by-pass caso haja.
    if float(by_pass) > 0.0:
        #   Loop para os dados
        for ii in range(numero_intervalos_tempo):
            #   Caso a vazao de entrada seja menor que o valor do by-pass
            if hidrograma_entrada[ii] < float(by_pass):
                #   Coloco a vazao para o by-pass
                vazoes_by_pass[ii] = hidrograma_entrada[ii]
                #   Zero o hidrograma
                hidrograma_entrada[ii] = 0.0
                
            #   Caso a vazao de entrada seja igual ou maior que o valor do by-pass
            else:
                #   Coloco a vazao para o by-pass
                vazoes_by_pass[ii] = float(by_pass)
                #   Amorteco o hidrograma de entrada
                hidrograma_entrada[ii] -= float(by_pass)
    
    #   Laco iterativo de Puls
    #   Faco em parcelas pois as cotas das variaveis CCVol e CCVaz nao sao as mesmas
    for ii in range(0, numero_intervalos_tempo-1):
        #   Somo os termos para determinar a "parcela desconhecida" da equacao de Puls
        S2dtQ_intervalo = hidrograma_entrada[ii] + hidrograma_entrada[ii+1] - hidrograma_saida[ii] + (2 * volume_reservado[ii] * (10**3)/duracao_intervalo_tempo_s)
        #   Descubro o valor de cota de reservatorio interpolando S2dtQ_intervalo em S2dtQ
        #   Como o primeiro valor de cota da curva cota_volume e' sempre zero, nao irei verificar <= 0
        if S2dtQ_intervalo <= S2dtQ[-1]:
            #   Encontrar o indice
            indice_cota = 0 # Armazena o indice da cota de CCVazao cujo valor e' imediatamente superior 'a cota do laco da CCVol
            while S2dtQ_intervalo > S2dtQ[indice_cota]:
                indice_cota += 1
                
            #   Interpole o seu valor
            hidrograma_saida[ii+1] = curva_cota_vazao[1][indice_cota-1] + (((S2dtQ_intervalo - S2dtQ[indice_cota-1])*(curva_cota_vazao[1][indice_cota] - curva_cota_vazao[1][indice_cota-1]))/(S2dtQ[indice_cota] - S2dtQ[indice_cota-1]))
            
        #   Caso contrario, se S2dtQ_intervalo for > que o ultimo valor de cota da cota_volume
        else:
            #   Extrapole o valor, extrapolacao linear
            hidrograma_saida[ii+1] = curva_cota_vazao[1][-2] + (((S2dtQ_intervalo - S2dtQ[-2])*(curva_cota_vazao[1][-1] - curva_cota_vazao[1][-2]))/(S2dtQ[-1] - S2dtQ[-2]))
        
        #   Determinar o volume armazenado: ((2S[i+1]/dt + Q[i+1]) - Q[i+1]) * dt/2 = S[i+1]
        volume_reservado[ii+1] = (S2dtQ_intervalo - hidrograma_saida[ii+1]) * (duracao_intervalo_tempo_s / (2 * 10**3))
        
        #   Determinar a cota do reservatorio pq sim, e' daora
        if volume_reservado[ii+1] <= curva_cota_volume[1][-1]:
            #   Encontrar o indice
            indice_cota = 0
            while volume_reservado[ii+1] > curva_cota_volume[1][indice_cota]:
                indice_cota += 1
                
            #   Interpolar
            cota_reservatorio[ii+1] = curva_cota_volume[0][indice_cota-1] + (((volume_reservado[ii+1] - curva_cota_volume[1][indice_cota-1]) * (curva_cota_volume[0][indice_cota] - curva_cota_volume[0][indice_cota-1]))/(curva_cota_volume[1][indice_cota] - curva_cota_volume[1][indice_cota-1]))
            
        #   Caso o reservatorio esta' alem do informado pelo usuario
        else:
            #   Extrapole linearmente considerando os dois ultimos pontos da curva
            cota_reservatorio[ii+1] = curva_cota_volume[0][-2] + (((volume_reservado[ii+1] - curva_cota_volume[1][-2]) * (curva_cota_volume[0][-1] - curva_cota_volume[0][-2]))/(curva_cota_volume[1][-1] - curva_cota_volume[1][-2]))
    
    #   Antes de retornar as variaveis, "devolvo" as vazoes retiradas pelo by-pass
    if float(by_pass) > 0.0:
        #   Loop para os dados
        for ii in range(numero_intervalos_tempo):
            #   Devolvo os valores do by-pass no final da simulacao
            hidrograma_saida[ii] += vazoes_by_pass[ii]
    
    #   Quem nao tem colirio usa oculos escuros B)
    return hidrograma_saida, cota_reservatorio
#------------------------------------------------------------------------
def aplicar_MuskingumCunge(hidrograma_entrada, numero_intervalos_tempo, duracao_intervalo_tempo_s, diferenca_cota_m, comprimento_canal_km, largura_canal_m, rugosidade_manning):
    """
    Calcula o hidrograma de saida de um canal retangular largo a partir de uma simulacao de Muskingum-Cunge.
    
    A funcao retorna dois arrays de floats:
        hidrogramas_trechos = [...]: Valores do hidrograma de saida do canal [m³/s].
    
    Parametros para uso:
        -> hidrograma_entrada = List/array que representa o hidrograma de entrada no canal [m³/s].
        -> numero_intervalos_tempo = Int que representa o numero de intervalos de tempo da simulacao.
        -> duracao_intervalo_tempo_s = Int que representa a duracao do intervalo de tempo [segundos].
        -> diferenca_cota_m = Float que representa a diferenca de cota total do canal [metros]
        -> comprimento_canal_km = Float que representa o comprimento total do canal [quilometros].
        -> largura_canal_m = Float que representa a largura do canal [metros].
        -> rugosidade_manning = Float que representa a rugosidade media do canal [adimensional].
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    from math import ceil
    from numpy import array, float64
    
    #   Determinar a vazao de referencia
    #   p. 164, MODELOS HIDROLOGICOS, 2ed., 2005 Carlos E. M. Tucci
    #   Qref = 2/3 * Qmax
    vazao_referencia = max(hidrograma_entrada) * 2./3
    
    #   Calcular a declividade (m/m)
    declividade = diferenca_cota_m/(comprimento_canal_km * 1000)
    
    #   Calcular a celeridade (m/s): A equacao a seguir considera um canal com largura >> altura
    #   p. 164, MODELOS HIDROLOGICOS, 2ed., 2005 Carlos E. M. Tucci
    #   c = 5/3 * So**0.3 * Qref**0.4/(n**0.6 * larg**0.4)
    celeridade = (5/3. * (declividade**0.3) * (vazao_referencia**0.4))/((rugosidade_manning**0.6) * (largura_canal_m**0.4))
    
    #   Calcular o delta X, para entao descobrir em quantos trechos o canal sera' dividido.
    #   Fread (1993) apud p. 277, HIDROLOGIA PARA ENGENHARIA E CIENCIAS AMBIENTAIS, 1ed., 2013, Collischon e Dornelles.
    #   dX <= c*dt/2 * (1 + ((1+(1.5*Q/(B*So*dt*c**2)))**0.5))
    delta_x = (celeridade * duracao_intervalo_tempo_s / 2.) * (1 + (1 + ((1.5 * vazao_referencia)/(largura_canal_m * declividade * duracao_intervalo_tempo_s * (celeridade**2))))**0.5)

    #   Algoritmo para decidir em quantos trechos o canal sera' dividido
    numero_trechos = int(ceil((comprimento_canal_km * 1000.)/delta_x))
    #   Calcular novo delta X
    delta_x = (comprimento_canal_km * 1000.)/float(numero_trechos)
    
    #   Calcular coeficientes K (segundos) e X(-)
    #   p. 162, MODELOS HIDROLOGICOS, 2ed., 2005 Carlos E. M. Tucci
    #   K = dX/c
    coef_K = delta_x / celeridade
    #   X = 0.5*(1-(Q/larg*So*c*dX))
    coef_X = 0.5 * (1 - (vazao_referencia/(largura_canal_m * declividade * celeridade * delta_x)))
    
    #   calcular C1, C2 e C3:
    #   p. 273, HIDROLOGIA PARA ENGENHARIA E CIENCIAS AMBIENTAIS, 1ed., 2013, Collischon e Dornelles.
    #   c1 = (dt-2*K*X)/(2*K*(1-X)+dt)
    coef_c1 = (duracao_intervalo_tempo_s - (2 * coef_K * coef_X))/(duracao_intervalo_tempo_s + (2 * coef_K * (1 - coef_X)))
    #   c2 = (dt+2*K*X)/(2*K*(1-X)+dt)
    coef_c2 = (duracao_intervalo_tempo_s + (2 * coef_K * coef_X))/(duracao_intervalo_tempo_s + (2 * coef_K * (1 - coef_X)))
    #   c3 = (2*K*(1-X)-dt)/(2*K*(1-X)+dt)
    coef_c3 = ((2 * coef_K * (1 - coef_X))-duracao_intervalo_tempo_s)/(duracao_intervalo_tempo_s + (2 * coef_K * (1 - coef_X)))
    
    #   Declarar variavel de saida: Matriz (2 x nint_tempo);
    #   O primeiro vetor e' o hidrograma que entra no trecho e o segundo e' o hidrograma que sai do trecho
    #   O processo consiste em propagar n vezes o hidrograma, do primeiro vetor ao segundo.
    #   No final do processo de propagacao de cada trecho, copiam-se os valores do hidrograma de saida para o hidrograma de entrada
    #   Portanto, o hidrograma de saida do canal e' o primeiro vetor do ultimo laco.
    hidrogramas_trechos = array([[0.0 for ii in range(numero_intervalos_tempo)] for jj in range(2)], float64)
    
    array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    
    #   Preparo o hidrogramas_trechos[0] para o primeiro loop
    for ii, vazao_entrada in enumerate(hidrograma_entrada):
        hidrogramas_trechos[0][ii] = vazao_entrada

    #   Primeiro valor e' sempre igual... Faco fora do for pois nao ha' necessidade de faze-lo dentro
    hidrogramas_trechos[1][0] = hidrogramas_trechos[0][0]
        
    #   loop da propagacao do canal
    for trecho in range(numero_trechos):
        #   Loop dos demais intervalos de tempo...
        for ii in range(1, numero_intervalos_tempo): # comeca em 1 pois o zero ja' foi feito anteriormente
            #   Calcular do segundo valor adiante
            hidrogramas_trechos[1][ii] = (coef_c1 * hidrogramas_trechos[0][ii]) + (coef_c2 * hidrogramas_trechos[0][ii-1]) + (coef_c3 * hidrogramas_trechos[1][ii-1])
        #   Passar a informacao do segundo vetor para o primeiro antes de calcular o proximo
        for ii, vazao in enumerate(hidrogramas_trechos[1]):
            hidrogramas_trechos[0][ii] = vazao
            
    #   Retorne o primeiro vetor que e' o hidrograma de saida do ultimo trecho
    return hidrogramas_trechos[0]
#------------------------------------------------------------------------
def somar_Hidrogramas(numero_intervalos_tempo, hidrogramas):
    """
    Soma n hidrogramas resultando em um unico so'. 
        
        Ressalta-se que a funcao considera que todos os hidrogramas acontecessem ao mesmo tempo, isto e', 
    o valor de cada intervalo do hidrograma resultante e' a soma dos valores deste mesmo
    intervalo de tempo de todos os N hidrogramas. 
        Segue um exemplo uma soma de dois hidrogramas:
    
        Hidrog. Resultante =  Hidrog.1 + Hidrog.2
             5             =    2      +    3
            10             =    6      +    4
            16             =    9      +    7
           ...             =   ...     +   ... 
            
        Parametros para uso:
            -> numero_intervalos_tempo: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            -> hidrogramas: Variavel do tipo lista que armazana os hidrogramas que serao somados.
                Exemplo: hidrogramas = [[...],[...],[...],[...],...] 
                    -> Em que cada [...] e' um hidrograma que participara' da soma;
                    -> Cada hidrograma deve ter o mesmo numero de dados (tamanho).
                    -> Nao ha' restricao do numero de hidrogramas a serem somados.
    """
    #   Algoritmo original escrito por Vitor G. Geller
    
    from numpy import array, float64
    
    #   variavel que armazenara' o somatorio
    hidrograma_resultante = array([0. for ii in range(numero_intervalos_tempo)],float64)
    
    #--- Os hidrogramas a serem somados entram como listas dentro da lista hidrogramas.
    #--- hidrogramas = [[hid_1],[hid_2],[hid_3],...,[hid_n]]

    #   loop dos intervalos
    for ii in range(numero_intervalos_tempo):
        
        #   declarar/resetar a variavel que recebe a soma dos hidrogramas no intervalo de tempo qualquer
        somatorio_do_intervalo = 0.0
        
        #   loops dos hidrogramas
        for jj in range(len(hidrogramas)):
            #   somar/acumular N parcelas de um mesmo intervalo de tempo
            somatorio_do_intervalo += hidrogramas[jj][ii]
            
        #   armazenar a soma no intervalo correspondente
        hidrograma_resultante[ii] = somatorio_do_intervalo
        
    #    hidrograma resultante e' a simples soma pontual (mesmo intervalo de tempo) dos hidrogramas anteriores.
    return hidrograma_resultante
#------------------------------------------------------------------------
def aplicar_Derivacao_Constante(numero_intervalos_tempo, hidrograma_entrada, valor_derivacao, saida_derivacao):
    """
    Simula uma derivacao (retirada de agua constante) de um hidrograma. 
    Nesse caso, a retirada de agua dar-se-a' por um valor constante em todos os intervalos do hidrograma de entrada.
    Caso o valor do intervalo do hidrograma de entrada for menor que o valor derivado, deriva-se todo o intervalo.
    
        Parametros de uso:
            -> numero_intervalos_tempo
            -> hidrograma_entrada
            -> valor_derivacao
            -> saida_derivacao
    """
    #   Algoritmo original escrito por Vitor G. Geller
    
    from numpy import array, float64
    
    #   Declarar a variavel
    hidrograma_derivado  = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    hidrograma_principal = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    
    #   Calcula-se a derivacao constante retirando o valor informado em cada intervalo de tempo
    for ii, valor in enumerate(hidrograma_entrada):
        #   Se o valor do intervalo for menor que o valor constante derivado
        if valor < valor_derivacao:
            #   Passo o valor para o hidrograma derivado
            hidrograma_derivado[ii] = valor
        #   Se o valor do intervalo for maior que o valor constante derivado
        else:
            #   Passo o valor para o hidrograma derivado
            hidrograma_derivado[ii] = valor_derivacao
            #   Zerar o hidrograma principal
            hidrograma_principal[ii] = valor - valor_derivacao
        
    #   Avaliar qual e' a saida
    #   == 1: hidrograma_principal
    if saida_derivacao == 1:
        return hidrograma_principal
    #   == 2: hidrograma_derivado
    else:
        return hidrograma_derivado
#------------------------------------------------------------------------
def aplicar_Derivacao_Porcentagem(numero_intervalos_tempo, hidrograma_entrada, valor_derivacao, saida_derivacao):
    """
    Simula uma derivacao de um hidrograma. 
    Nesse caso, a retirada de agua dar-se-a' por uma porcentagem do valor do hidrograma de entrada.
    
        Parametros de uso:
            -> numero_intervalos_tempo
            -> hidrograma_entrada
            -> valor_derivacao
            -> saida_derivacao
    """
    #   Algoritmo original escrito por Vitor G. Geller
    
    from numpy import array, float64
    
    #   Declarar a variavel
    hidrograma_derivado  = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    hidrograma_principal = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    
    #   Calcula-se a derivacao retirando o valor porcentual informado em cada intervalo de tempo
    for ii, valor in enumerate(hidrograma_entrada):
        #   Aplicar a porcentagem de derivacao
        hidrograma_derivado[ii] = valor * valor_derivacao / 100.
        #   Reduzir do hidrograma principal
        hidrograma_principal[ii] = valor - hidrograma_derivado[ii]
    
    #   Avaliar qual e' a saida
    #   == 1: hidrograma_principal
    if saida_derivacao == 1:
        return hidrograma_principal
    #   == 2: hidrograma_derivado
    else:
        return hidrograma_derivado
#------------------------------------------------------------------------
def aplicar_Derivacao_Hidrograma(numero_intervalos_tempo, hidrograma_entrada, hidrograma_retirado, saida_derivacao):
    """
    Simula uma derivacao de um hidrograma.
    Nesse caso, a retirada de agua dar-se-a' por valores oriundos de um segundo hidrograma.
    Caso o valor do intervalo do hidrograma de entrada for menor que o valor derivado, deriva-se todo o intervalo.
    
        Parametros de uso:
            -> numero_intervalos_tempo
            -> hidrograma_entrada
            -> hidrograma_retirado
            -> saida_derivacao
    """
    #   Algoritmo original escrito por Vitor G. Geller
    
    from numpy import array, float64
    
    #   Declarar a variavel
    hidrograma_derivado  = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    hidrograma_principal = array([0.0 for ii in range(numero_intervalos_tempo)], float64)
    
    #   Calcula-se a derivacao retirando o valor informado em cada intervalo de tempo
    for ii, valor in enumerate(hidrograma_entrada):
        #   Se o valor do intervalo for menor que o valor constante derivado
        if valor < hidrograma_retirado[ii]:
            #   Passo o valor para o hidrograma derivado
            hidrograma_derivado[ii] = valor
        #   Se o valor do intervalo for maior que o valor constante derivado
        else:
            #   Passo o valor para o hidrograma derivado
            hidrograma_derivado[ii] = hidrograma_retirado[ii]
            #   Zerar o hidrograma principal
            hidrograma_principal[ii] = valor - hidrograma_retirado[ii]
        
    #   Avaliar qual e' a saida
    #   == 1: hidrograma_principal
    if saida_derivacao == 1:
        return hidrograma_principal
    #   == 2: hidrograma_derivado
    else:
        return hidrograma_derivado
#------------------------------------------------------------------------
def plotar_Hidrogramas_PQ(hidrograma, precipitacao_projeto, precipitacao_efetiva, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """
    Funcao responsavel por plotar e salvar os hidrogramas calculados nas operacoes chuva-vazao. 
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        ->hidrograma: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma = [...] -> Valores de vazao de um hidrograma [em metros^3/s].
        ->precipitacao_projeto: Lista/array que contem os dados de chuva de projeto (hietograma de projeto).
            Exemplo: precipitacao_projeto = [...] -> Dados de chuva ordenada [em mm/s].
        ->precipitacao_efetiva: Lista/array que contem os dados de chuva efetiva.
            Exemplo: precipitacao_efetiva = [...] -> Dados de chuva efetiva [em mm/s].
        ->duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        ->diretorio_saida: String que armazena o diretorio em que a imagem sera' salva.
        ->titulo_grafico: String que armazena o titulo do grafico.
        ->numero_operacao: Int que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
        ->resolucao: List/array com dois valores que representam a resolucao da plotagem.
            Exemplo: resolucao = [800,600]
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    from numpy import array, float64, linspace, argmax
    
    #   Calculos iniciais:
    #   Independente da resolucao escolhida, as bordas terao sempre o mesmo tamanho.
    #   Esquerda~96, superior~60, inferior~60, direita~96
    bordas = [0.0, 0.0, 0.0, 0.0]
    #   Calcular borda esquerda
    bordas[0] = 96./resolucao[0]
    #   Calcular borda inferior : deve ser -61 para fechar 60 pixels
    bordas[1] = 61./resolucao[1]
    #   Calcular borda direita : deve ser -97 para fechar 96 pixels
    bordas[2] = ((resolucao[0]-97.)/resolucao[0]) - bordas[0]
    #   Calcular borda superior
    bordas[3] = ((resolucao[1]-60.)/resolucao[1]) - bordas[1]
    #   Ajustar a "escala" vertical do plot do hidrograma
    altura_maxima_grafico = max(hidrograma) / 0.6
    #   Criar o eixo X
    eixo_x = array([ii for ii in range(len(hidrograma))], float64)
    
    #   Iniciar a imagem
    fig = plt.figure(figsize=((resolucao[0]/100.),(resolucao[1]/100.)))
    
    #   Ajustes de borda
    ax1 = fig.add_axes([bordas[0], bordas[1], bordas[2], bordas[3]])
    
    #   Declaracao de eixos
    plt.axis([0, len(hidrograma), 0, altura_maxima_grafico])
    
    #   Plotagem do hidrograma
    ax1.plot(eixo_x, hidrograma, "b-", linewidth=4)
        
    #   Ajustar eixos
    ax1.set_xlabel(r"$Intervalos\; de\; tempo\; (\Delta t\; =\; %ds)$"%(duracao_intervalo_tempo_s), size = 12)
    ax1.set_ylabel(r"$Vaz\~ao\; (m^3/s)$", color="b", size = 12)
    
    #   Trocar a cor dos valores do eixo y
    for corlabel1 in ax1.get_yticklabels():
        corlabel1.set_color("b")
    
    #   Plotar somente alguns valores nos eixos
    valores_grid_horizontal = linspace(0,altura_maxima_grafico,11)
    valores_grid_vertical = linspace(0,len(hidrograma),11)
    ax1.xaxis.set_ticks(valores_grid_vertical)
    ax1.yaxis.set_ticks(valores_grid_horizontal)
    ax1.grid(True, linestyle="--")
    
    #   Criar um novo eixo Y
    ax2 = ax1.twinx()
    #   Inverter eixos
    ax2.invert_yaxis()
    
    #   Criar o eixo X
    eixo_x = array([ii for ii in range(len(precipitacao_projeto))], float64)
    
    #   Plotagem 
    ax2.bar(eixo_x, precipitacao_projeto, width = 1, color='#00FFFF', linewidth = 0, label = "Precipitação")
    ax2.bar(eixo_x, precipitacao_efetiva , width = 1, color='#147E7E', linewidth = 0, label = "Precip. Efetiva")
    
    #   Ajustar valores do segundo eixo Y
    ax2.set_ylabel(r"$Precipitac\c\~ao\; (mm)$", color='#147E7E', size = 12)
    for corlabel2 in ax2.get_yticklabels():
        corlabel2.set_color('#147E7E')
    
    #   Plotar somente 11 valores nos eixos
    valores_grid_horizontal = linspace(0,(max(precipitacao_projeto)/0.3),11)
    ax2.yaxis.set_ticks(valores_grid_horizontal)

    #   Decidir em qual canto colocar a legenda: 
    #   Quase sempre o correto e' posiciona'-la na direita, mas vai la' se saber o que o usuario manda plotar...
    if argmax(precipitacao_projeto) < len(precipitacao_projeto)/2:
        plt.legend(loc="upper right")
    else:
        plt.legend(loc="upper left")

    #   Inserir titulo
    plt.title(("%s\n"%(titulo_grafico) + r"$Chuva-Vaz\~ao$"), size = 12)
    
    #   salve o grafico
    plt.savefig("%s\\PQ_Hid%d_%dx%d.png"%(diretorio_saida, numero_operacao,resolucao[0],resolucao[1]))
        
    #   Limpar e fechar as figuras depois de salva'-las
    fig.clf('all')
    plt.close('all')
#------------------------------------------------------------------------
def plotar_Hidrogramas_PULS(hidrograma_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """
    Plota os hidrogramas de entrada e saida de uma operacao Puls qualquer, salvando-os em uma imagem .png no diretorio fornecido.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        ->hidrograma_entrada: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_entrada = [...] -> Valores de vazao de um hidrograma [em metros^3/s].
        ->hidrograma_saida: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_saida = [...] -> Valores de vazao de um hidrograma de saida [em metros^3/s].
        ->duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        ->diretorio_saida: String que armazena o diretorio em que a imagem sera' salva.
        ->titulo_grafico: String que armazena o titulo do grafico.
        ->numero_operacao: Int que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
        ->resolucao: List/array com dois valores que representam a resolucao da plotagem.
            Exemplo: resolucao = [800,600]
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    from numpy import array, float64, linspace, argmax
    
    #   Calculos iniciais:
    #   Independente da resolucao escolhida, as bordas terao sempre o mesmo tamanho.
    #   Esquerda~96, superior~60, inferior~60, direita~48
    bordas = [0.0, 0.0, 0.0, 0.0]
    #   Calcular borda esquerda
    bordas[0] = 96./resolucao[0]
    #   Calcular borda inferior : deve ser -61 para fechar 60 pixels
    bordas[1] = 61./resolucao[1]
    #   Calcular borda direita : deve ser -49 para fechar 48 pixels
    bordas[2] = ((resolucao[0]-49.)/resolucao[0]) - bordas[0]
    #   Calcular borda superior
    bordas[3] = ((resolucao[1]-60.)/resolucao[1]) - bordas[1]
    #   Ajustar a "escala" vertical do plot do hidrograma
    altura_maxima_grafico = max(hidrograma_entrada) * 1.25
    #   Criar o eixo X
    eixo_x = array([ii for ii in range(len(hidrograma_entrada))], float64)
    
    #   Iniciar a imagem
    fig = plt.figure(figsize=((resolucao[0]/100.),(resolucao[1]/100.)))
    
    #   Ajustes de borda
    ax1 = fig.add_axes([bordas[0], bordas[1], bordas[2], bordas[3]])
    
    #   Declaracao de eixos
    plt.axis([0, len(hidrograma_entrada), 0, altura_maxima_grafico])
    
    #   Plotagem do hidrograma
    ax1.plot(eixo_x, hidrograma_entrada, "b-", linewidth=4, label = r"$Hidrograma\; de\; Entrada$")
    ax1.plot(eixo_x, hidrograma_saida, "r-", linewidth=4, label = r"$Hidrograma\; de\; Sa \'\imath da$")
    
    #   Ajustar eixos
    ax1.set_xlabel(r"$Intervalos\; de\; tempo\; (\Delta t\; =\; %ds)$"%(duracao_intervalo_tempo_s), size = 12)
    ax1.set_ylabel(r"$Vaz\~ao\; (m^3/s)$", color="b", size = 12)
    
    #   Trocar a cor dos valores do eixo y
    for corlabel1 in ax1.get_yticklabels():
        corlabel1.set_color("b")
    
    #   Plotar somente 5 valores nos eixos
    valores_grid_horizontal = linspace(0,altura_maxima_grafico,11)
    valores_grid_vertical = linspace(0,len(hidrograma_entrada),11)
    ax1.xaxis.set_ticks(valores_grid_vertical)
    ax1.yaxis.set_ticks(valores_grid_horizontal)
    ax1.grid(True, linestyle="--")
    
    #   Decidir em qual canto colocar a legenda: 
    #   Quase sempre o correto e' posiciona'-la na direita, mas vai la' se saber o que o usuario manda plotar...
    if argmax(hidrograma_entrada) < len(hidrograma_entrada)/2:
        plt.legend(loc="upper right")
    else:
        plt.legend(loc="upper left")
    
    #   Inserir titulo
    plt.title((str(titulo_grafico) + "\n" + r"$Propagac\c\~ao\; de\; Reservat\'orios:\; Puls$"), size = 12)
    
    #   salve o grafico
    plt.savefig("%s\\PULS_Hid%d_%dx%d.png"%(diretorio_saida, numero_operacao,resolucao[0],resolucao[1]))
    
    #   Limpar e fechar as figuras depois de salva'-las
    fig.clf('all')
    plt.close('all')
#------------------------------------------------------------------------
def plotar_Hidrogramas_MKC(hidrograma_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """
    Plota os hidrogramas de entrada e saida de uma operacao Muskingum-Cunge qualquer, salvando-os em uma imagem .png no diretorio fornecido.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        ->hidrograma_entrada: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_entrada = [...] -> Valores de vazao de um hidrograma [em metros^3/s].
        ->hidrograma_saida: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_saida = [...] -> Valores de vazao de um hidrograma de saida [em metros^3/s].
        ->duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        ->diretorio_saida: String que armazena o diretorio em que a imagem sera' salva.
        ->titulo_grafico: String que armazena o titulo do grafico.
        ->numero_operacao: Int que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
        ->resolucao: List/array com dois valores que representam a resolucao da plotagem.
            Exemplo: resolucao = [800,600]
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    from numpy import array, float64, linspace, argmax
    
    #   Calculos iniciais:
    #   Independente da resolucao escolhida, as bordas terao sempre o mesmo tamanho.
    #   Esquerda~96, superior~60, inferior~60, direita~48
    bordas = [0.0, 0.0, 0.0, 0.0]
    #   Calcular borda esquerda
    bordas[0] = 96./resolucao[0]
    #   Calcular borda inferior : deve ser -61 para fechar 60 pixels
    bordas[1] = 61./resolucao[1]
    #   Calcular borda direita : deve ser -49 para fechar 48 pixels
    bordas[2] = ((resolucao[0]-49.)/resolucao[0]) - bordas[0]
    #   Calcular borda superior
    bordas[3] = ((resolucao[1]-60.)/resolucao[1]) - bordas[1]
    #   Ajustar a "escala" vertical do plot do hidrograma
    altura_maxima_grafico = max(hidrograma_entrada) * 1.25
    #   Criar o eixo X
    eixo_x = array([ii for ii in range(len(hidrograma_entrada))], float64)
    
    #   Iniciar a imagem
    fig = plt.figure(figsize=((resolucao[0]/100.),(resolucao[1]/100.)))
    
    #   Ajustes de borda
    ax1 = fig.add_axes([bordas[0], bordas[1], bordas[2], bordas[3]])
    
    #   Declaracao de eixos
    plt.axis([0, len(hidrograma_entrada), 0, altura_maxima_grafico])
    
    #   Plotagem do hidrograma
    ax1.plot(eixo_x, hidrograma_entrada, "b-", linewidth=4, label = r"$Hidrograma\; de\; Entrada$")
    ax1.plot(eixo_x, hidrograma_saida, "r-", linewidth=4, label = r"$Hidrograma\; de\; Sa \'\imath da$")
    
    #   Ajustar eixos
    ax1.set_xlabel(r"$Intervalos\; de\; tempo\; (\Delta t\; =\; %ds)$"%(duracao_intervalo_tempo_s), size = 12)
    ax1.set_ylabel(r"$Vaz\~ao\; (m^3/s)$", color="b", size = 12)
    
    #   Trocar a cor dos valores do eixo y
    for corlabel1 in ax1.get_yticklabels():
        corlabel1.set_color("b")
    
    #   Plotar somente 5 valores nos eixos
    valores_grid_horizontal = linspace(0,altura_maxima_grafico,11)
    valores_grid_vertical = linspace(0,len(hidrograma_entrada),11)
    ax1.xaxis.set_ticks(valores_grid_vertical)
    ax1.yaxis.set_ticks(valores_grid_horizontal)
    ax1.grid(True, linestyle="--")

    #   Decidir em qual canto colocar a legenda: 
    #   Quase sempre o correto e' posiciona'-la na direita, mas vai la' se saber o que o usuario manda plotar...
    if argmax(hidrograma_entrada) < len(hidrograma_entrada)/2:
        plt.legend(loc="upper right")
    else:
        plt.legend(loc="upper left")
        
    #   Inserir titulo
    plt.title((str(titulo_grafico) + "\n" + r"$Propagac\c\~ao\; de\; Canais:\; Muskingum-Cunge$"), size = 12)
    
    #   salve o grafico
    plt.savefig("%s\\MKC_Hid%d_%dx%d.png"%(diretorio_saida, numero_operacao,resolucao[0],resolucao[1]))
    
    #   Limpar e fechar as figuras depois de salva'-las
    fig.clf('all')
    plt.close('all')
#------------------------------------------------------------------------
def plotar_somar_Hidrogramas(hidrogramas_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """
    Plota os hidrogramas de entrada e saida de uma operacao de Juncao qualquer, salvando-os em uma imagem .png no diretorio fornecido.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        ->hidrogramas_entrada: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrogramas_entrada = [[...],[...],[...],...] -> Cada [...] sao valores de vazao de um hidrograma [em metros^3/s].
        ->hidrograma_saida: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_saida = [...] -> Valores de vazao de um hidrograma de saida [em metros^3/s].
        ->duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        ->diretorio_saida: String que armazena o diretorio em que a imagem sera' salva.
        ->titulo_grafico: String que armazena o titulo do grafico.
        ->numero_operacao: Int que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
        ->resolucao: List/array com dois valores que representam a resolucao da plotagem.
            Exemplo: resolucao = [800,600]
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    from numpy import array, float64, linspace, argmax
    
    #   Calculos iniciais:
    #   Independente da resolucao escolhida, as bordas terao sempre o mesmo tamanho.
    #   Esquerda~96, superior~60, inferior~60, direita~48
    bordas = [0.0, 0.0, 0.0, 0.0]
    #   Calcular borda esquerda
    bordas[0] = 96./resolucao[0]
    #   Calcular borda inferior : deve ser -61 para fechar 60 pixels
    bordas[1] = 61./resolucao[1]
    #   Calcular borda direita : deve ser -49 para fechar 48 pixels
    bordas[2] = ((resolucao[0]-49.)/resolucao[0]) - bordas[0]
    #   Calcular borda superior
    bordas[3] = ((resolucao[1]-60.)/resolucao[1]) - bordas[1]
    #   Ajustar a "escala" vertical do plot do hidrograma
    altura_maxima_grafico = max(hidrograma_saida) / 0.6
    #   Criar o eixo X
    eixo_x = array([ii for ii in range(len(hidrograma_saida))], float64)
    
    #   Iniciar a imagem
    fig = plt.figure(figsize=((resolucao[0]/100.),(resolucao[1]/100.)))
    
    #   Ajustes de borda
    ax1 = fig.add_axes([bordas[0], bordas[1], bordas[2], bordas[3]])
    
    #   Declaracao de eixos
    plt.axis([0, len(hidrograma_saida), 0, altura_maxima_grafico])
    
    #   Plotagem do hidrograma
    ax1.plot(eixo_x, hidrograma_saida, linewidth=4, label = r"$Hidrograma\; de\; Sa \'\imath da$")
    for ii, hidrograma in enumerate(hidrogramas_entrada):
        ax1.plot(eixo_x, hidrograma, linewidth=2, label = r"$Hidrograma\; de\; Entrada\; %d$" %(ii+1))
    
    #   Ajustar eixos
    ax1.set_xlabel(r"$Intervalos\; de\; tempo\; (\Delta t\; =\; %ds)$"%(duracao_intervalo_tempo_s), size = 12)
    ax1.set_ylabel(r"$Vaz\~ao\; (m^3/s)$", color="b", size = 12)
    
    #   Trocar a cor dos valores do eixo y
    for corlabel1 in ax1.get_yticklabels():
        corlabel1.set_color("b")
    
    #   Plotar somente 5 valores nos eixos
    valores_grid_horizontal = linspace(0,altura_maxima_grafico,11)
    valores_grid_vertical = linspace(0,len(hidrograma_saida),11)
    ax1.xaxis.set_ticks(valores_grid_vertical)
    ax1.yaxis.set_ticks(valores_grid_horizontal)
    ax1.grid(True, linestyle="--")

    #   Decidir em qual canto colocar a legenda: 
    #   Quase sempre o correto e' posiciona'-la na direita, mas vai la' se saber o que o usuario manda plotar...
    if argmax(hidrograma_saida) < len(hidrograma_saida)/2:
        plt.legend(loc="upper right")
    else:
        plt.legend(loc="upper left")
    
    #   Inserir titulo
    plt.title((str(titulo_grafico) + "\n" + r"$Junc\c\~ao\; de\; Hidrogramas$"), size = 12)
    
    #   salve o grafico
    plt.savefig("%s\\JUN_Hid%d_%dx%d.png"%(diretorio_saida, numero_operacao,resolucao[0],resolucao[1]))
    
    #   Limpar e fechar as figuras depois de salva'-las
    fig.clf('all')
    plt.close('all')
#------------------------------------------------------------------------
def plotar_Hidrogramas_Leitura(hidrograma_entrada, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """
    Plota os hidrogramas de entrada e saida de uma operacao Muskingum-Cunge qualquer, salvando-os em uma imagem .png no diretorio fornecido.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        ->hidrograma_entrada: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_entrada = [...] -> Valores de vazao de um hidrograma [em metros^3/s].
        ->duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        ->diretorio_saida: String que armazena o diretorio em que a imagem sera' salva.
        ->titulo_grafico: String que armazena o titulo do grafico.
        ->numero_operacao: Int que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
        ->resolucao: List/array com dois valores que representam a resolucao da plotagem.
            Exemplo: resolucao = [800,600]
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    from numpy import array, float64, linspace, argmax
    
    #   Calculos iniciais:
    #   Independente da resolucao escolhida, as bordas terao sempre o mesmo tamanho.
    #   Esquerda~96, superior~60, inferior~60, direita~48
    bordas = [0.0, 0.0, 0.0, 0.0]
    #   Calcular borda esquerda
    bordas[0] = 96./resolucao[0]
    #   Calcular borda inferior : deve ser -61 para fechar 60 pixels
    bordas[1] = 61./resolucao[1]
    #   Calcular borda direita : deve ser -49 para fechar 48 pixels
    bordas[2] = ((resolucao[0]-49.)/resolucao[0]) - bordas[0]
    #   Calcular borda superior
    bordas[3] = ((resolucao[1]-60.)/resolucao[1]) - bordas[1]
    #   Ajustar a "escala" vertical do plot do hidrograma
    altura_maxima_grafico = max(hidrograma_entrada) * 1.25
    #   Criar o eixo X
    eixo_x = array([ii for ii in range(len(hidrograma_entrada))], float64)
    
    #   Iniciar a imagem
    fig = plt.figure(figsize=((resolucao[0]/100.),(resolucao[1]/100.)))
    
    #   Ajustes de borda
    ax1 = fig.add_axes([bordas[0], bordas[1], bordas[2], bordas[3]])
    
    #   Declaracao de eixos
    plt.axis([0, len(hidrograma_entrada), 0, altura_maxima_grafico])
    
    #   Plotagem do hidrograma
    ax1.plot(eixo_x, hidrograma_entrada, "b-", linewidth=4, label = r"$Hidrograma\; de\; Entrada$")
    
    #   Ajustar eixos
    ax1.set_xlabel(r"$Intervalos\; de\; tempo\; (\Delta t\; =\; %ds)$"%(duracao_intervalo_tempo_s), size = 12)
    ax1.set_ylabel(r"$Vaz\~ao\; (m^3/s)$", color="b", size = 12)
    
    #   Trocar a cor dos valores do eixo y
    for corlabel1 in ax1.get_yticklabels():
        corlabel1.set_color("b")
    
    #   Plotar somente 5 valores nos eixos
    valores_grid_horizontal = linspace(0,altura_maxima_grafico,11)
    valores_grid_vertical = linspace(0,len(hidrograma_entrada),11)
    ax1.xaxis.set_ticks(valores_grid_vertical)
    ax1.yaxis.set_ticks(valores_grid_horizontal)
    ax1.grid(True, linestyle="--")

    #   Decidir em qual canto colocar a legenda: 
    #   Quase sempre o correto e' posiciona'-la na direita, mas vai la' se saber o que o usuario manda plotar...
    if argmax(hidrograma_entrada) < len(hidrograma_entrada)/2:
        plt.legend(loc="upper right")
    else:
        plt.legend(loc="upper left")
        
    #   Inserir titulo
    plt.title((str(titulo_grafico) + "\n" + r"$Hidrograma\; informado\; pelo\; usu\acute{a}rio$"), size = 12)
    
    #   salve o grafico
    plt.savefig("%s\\LEITURA_Hid%d_%dx%d.png"%(diretorio_saida, numero_operacao,resolucao[0],resolucao[1]))
    
    #   Limpar e fechar as figuras depois de salva'-las
    fig.clf('all')
    plt.close('all')
#------------------------------------------------------------------------
def plotar_Hidrogramas_Derivacao(hidrograma_entrada, hidrograma_saida, duracao_intervalo_tempo_s, diretorio_saida, titulo_grafico, numero_operacao, resolucao):
    """
    Plota os hidrogramas de entrada e saida de uma operacao Muskingum-Cunge qualquer, salvando-os em uma imagem .png no diretorio fornecido.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        ->hidrograma_entrada: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_entrada = [...] -> Valores de vazao de um hidrograma [em metros^3/s].
        ->hidrograma_saida: Lista/array que contem os dados dos hidrogramas a serem plotados.
            Exemplo: hidrograma_saida = [...] -> Valores de vazao de um hidrograma de saida [em metros^3/s].
        ->duracao_intervalo_tempo_s: Int que representa a duracao do intervalo de tempo [em segundos].
        ->diretorio_saida: String que armazena o diretorio em que a imagem sera' salva.
        ->titulo_grafico: String que armazena o titulo do grafico.
        ->numero_operacao: Int que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
        ->resolucao: List/array com dois valores que representam a resolucao da plotagem.
            Exemplo: resolucao = [800,600]
    """
    #   Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    from numpy import array, float64, linspace, argmax
    
    #   Calculos iniciais:
    #   Independente da resolucao escolhida, as bordas terao sempre o mesmo tamanho.
    #   Esquerda~96, superior~60, inferior~60, direita~48
    bordas = [0.0, 0.0, 0.0, 0.0]
    #   Calcular borda esquerda
    bordas[0] = 96./resolucao[0]
    #   Calcular borda inferior : deve ser -61 para fechar 60 pixels
    bordas[1] = 61./resolucao[1]
    #   Calcular borda direita : deve ser -49 para fechar 48 pixels
    bordas[2] = ((resolucao[0]-49.)/resolucao[0]) - bordas[0]
    #   Calcular borda superior
    bordas[3] = ((resolucao[1]-60.)/resolucao[1]) - bordas[1]
    #   Ajustar a "escala" vertical do plot do hidrograma
    altura_maxima_grafico = max(hidrograma_entrada) * 1.25
    #   Criar o eixo X
    eixo_x = array([ii for ii in range(len(hidrograma_entrada))], float64)
    
    #   Iniciar a imagem
    fig = plt.figure(figsize=((resolucao[0]/100.),(resolucao[1]/100.)))
    
    #   Ajustes de borda
    ax1 = fig.add_axes([bordas[0], bordas[1], bordas[2], bordas[3]])
    
    #   Declaracao de eixos
    plt.axis([0, len(hidrograma_entrada), 0, altura_maxima_grafico])
    
    #   Plotagem do hidrograma
    ax1.plot(eixo_x, hidrograma_entrada, "b-", linewidth=4, label = r"$Hidrograma\; de\; Entrada$")
    ax1.plot(eixo_x, hidrograma_saida, "r-", linewidth=4, label = r"$Hidrograma\; de\; Sa \'\imath da$")
    
    #   Ajustar eixos
    ax1.set_xlabel(r"$Intervalos\; de\; tempo\; (\Delta t\; =\; %ds)$"%(duracao_intervalo_tempo_s), size = 12)
    ax1.set_ylabel(r"$Vaz\~ao\; (m^3/s)$", color="b", size = 12)
    
    #   Trocar a cor dos valores do eixo y
    for corlabel1 in ax1.get_yticklabels():
        corlabel1.set_color("b")
    
    #   Plotar somente 5 valores nos eixos
    valores_grid_horizontal = linspace(0,altura_maxima_grafico,11)
    valores_grid_vertical = linspace(0,len(hidrograma_entrada),11)
    ax1.xaxis.set_ticks(valores_grid_vertical)
    ax1.yaxis.set_ticks(valores_grid_horizontal)
    ax1.grid(True, linestyle="--")

    #   Decidir em qual canto colocar a legenda: 
    #   Quase sempre o correto e' posiciona'-la na direita, mas vai la' se saber o que o usuario manda plotar...
    if argmax(hidrograma_entrada) < len(hidrograma_entrada)/2:
        plt.legend(loc="upper right")
    else:
        plt.legend(loc="upper left")
        
    #   Inserir titulo
    plt.title((str(titulo_grafico) + "\n" + r"$Derivac\c\~ao$"), size = 12)
    
    #   salve o grafico
    plt.savefig("%s\\DERIVACAO_Hid%d_%dx%d.png"%(diretorio_saida, numero_operacao,resolucao[0],resolucao[1]))
    
    #   Limpar e fechar as figuras depois de salva'-las
    fig.clf('all')
    plt.close('all')
#------------------------------------------------------------------------