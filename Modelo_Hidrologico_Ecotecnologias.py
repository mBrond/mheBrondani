# -*- coding: utf-8 -*-

#   Neste arquivo esta' apenas a inicializacao do codigo.

###############################################################################################################
#                                                                                                             #
#        Caro leitor,                                                                                         #
#        -Venho por meio deste avisar-te que este programa trata-se de um modelo acadêmico escrito            #
#    majoritariamente por um estudante de engenharia CIVIL, em sua maioria durante a graduação;               #
#        -Infelizmente este codigo não é um exemplo de boas praticas de programação, contudo, o código        #
#    mostrou-se eficaz em cumprir as funções as quais fora designado;                                         #
#        -Para o correto funcionamento do modelo certifique-se da existência das seguintes bibliotecas em     #
#   seu interpretador Python 3.7 (ou superior): "numpy", "matplotlib", "PIL", "tkinter", "sys", "os" e "math".#
#                                                                                                             #
#        -Espero que tenhas uma boa experiência com o software.                                               #
#        -Não hesite em reportar bugs ao e-mail "vitorgg_hz@hotmail.com"                                      #
#        -Como disse um grande amigo meu, "Se funciona, não é idiota" - Eckhardt, R. B.                       #
#                                                                                                     Vitor G.#
###############################################################################################################
#   Sugestões para as proximas atualizacoes:                                                                  #
#   -Prioridade média:                                                                                        #
#   	1) Opção de permitir definir máximo e mínimo nos gráficos. Para poder comparar graficos               #
#   de bacias diferentes ou na mesma bacia com urbanizacoes diferentes)                                       #
#   -Prioridade baixa:                                                                                        #
#   		b. Permitir que o hidrograma lido possa ser utilizado nos gráficos, assim seria possível          #
#   "calibrar" e comparar com observados                                                                      #
###############################################################################################################

#   Import das bibliotecas Python
from sys import exit, argv, path as syspath
from os import path
from tkinter import *

#-----------------------------------------------------------------------
if __name__ == '__main__':
    versao_do_software = round(220706/200000,2) # AAMMDD/200000
    #   Pegar o diretorio do software
    diretorio_do_software = path.dirname(path.abspath(argv[0])).encode()
    diretorio_biblioteca = diretorio_do_software + "/lib".encode()
    #   Estabelecer o diretorio dos arquivos deste programa para poderem ser importados
    syspath.insert(1, diretorio_biblioteca.decode())
    
    #   Import(s) final(is)
    from lib.InterfacesGraficas import InterfacePrincipal
    
    print ("""
     ------------------ MODELO HIDROLOGICO ECOTECNOLOGIAS ----------------- 
    |Desenvolvedores:                                                      |
    |- Vitor Gustavo Geller - vitorgg_hz@hotmail.com                       |
    |- Lucas Camargo da Silva Tassinari - lucascstassinari@gmail.com       |
    |- Daniel Gustavo Allasia P. - dallasia@gmail.com                      |
    |- Rutineia Tassi - rutineia@gmail.com                                 |
    |                                                                      |
    |VERSAO: %5.2f                                                         |
    |------------------------- INSTRUCOES DE USO --------------------------|
    |                                                                      |
    |-> Caso voce nao possua um arquivo de entrada, voce pode cria'-lo     |
    |utilizando o ambiente auxiliar localizado na opcao "Escrever arquivo  |
    |de entrada..." dentro do menu "Arquivo".                              |
    |                                                                      |
    |-> Se voce ja' possui um arquivo de entrada e deseja executa'-lo,     |
    |utilize a funcao "Executar arquivo de entrada..." ou "Executar todos  |
    |os arquivos de uma pasta..." ambas dentro do menu "Arquivo".          |
    |                                                                      |
    |-> Se voce ja' executou algum arquivo de entrada e deseja plotar os   |
    |resultados, utilize a funcao "Plotar graficos..." presente dentro do  |
    |menu "Arquivo".                                                       |
    |                                                      Boas simulacoes!|
    |                                                              Vitor G.|
     ---------------------------------------------------------------------- """ %(versao_do_software))
    
    #   Iniciar funcoes de interface
    root = Tk()
    #   Rodar o programa
    app = InterfacePrincipal(root, versao_do_software, diretorio_do_software)
    #   Finalizar loop do programa
    app.mainloop()
#-----------------------------------------------------------
