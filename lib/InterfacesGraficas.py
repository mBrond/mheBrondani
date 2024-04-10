# -*- coding: utf-8 -*-

#   Neste arquivo encontram-se as funcoes que desenham as janelas do programa.
#   O objetivo foi tentar separar ao maximo as funcoes de interface do resto do codigo.
#   No entanto, ainda ha' algumas linhas que poderiam ser feitas em outras partes.


#   Import das bibliotecas Python
from sys import exit
from tkinter import *
from tkinter import scrolledtext
from os import path
from PIL import Image, ImageTk
#   Import das bibliotecas customizadas
from Utilidades import centralizarJanela, criarPasta, deletarArquivoAntigo
from Utilidades import escreverArquivoEntrada, mensagensInterfaces
from Utilidades import mensagensIntegridadeArquivosObservados
from CalculoOperacoes import iniciarProcessamento, iniciarGraficos
from Leitura import procurarArquivo, checarIntegridadeArquivoTexto
from Leitura import checarIntegridadeArquivoCotaVolume, determinarDiretoriosPlotagens


#-----------------------------------------------------------------------
class InterfacePrincipal(Toplevel):
    """Classe responsavel por exibir a tela de entrada do modelo."""
    #-----------------------------------------------------------------------
    def __init__(self, master, versao_do_software, diretorio_do_software):
        """"""
        #   Sumir com a janelinha, não gosto dela
        master.withdraw()
        
        #   Facilitar minha vida 
        self.master = master
        self.versao_do_software = versao_do_software
        self.diretorio_do_software = diretorio_do_software
        
        #   Mudar todos os icones
        icone = ImageTk.PhotoImage(Image.open(self.diretorio_do_software + "/lib/icone.png".encode()))
        self.master.wm_iconphoto(True, icone)
        
        #   Rodar interface
        self.interfacePrincipal()
    #-----------------------------------------------------------------------
    def interfacePrincipal(self):
        """Desenha a janela principal do modelo"""
        #   Fazer a janela
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Alguns detalhes
        self.resizable(width=False, height=False)
        self.title("Modelo Hidrológico Ecotecnologias %5.2f" %(self.versao_do_software))
        self.protocol("WM_DELETE_WINDOW", self.sair)
        
        #   Criar o frame para inserir os widgets
        primeiroFrame = Frame(self, bg="#DFF9CA")
        primeiroFrame.pack(padx = 20, pady = 10)
        
        #   Iniciar o menu de barras
        menubar = Menu(self)
        
        #   Primeiro menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Escrever arquivo de entrada...", command=lambda: self.abrirInterfaceAuxiliar())
        filemenu.add_separator()
        filemenu.add_command(label="Executar um único arquivo de entrada...", command=lambda: self.executarEntrada(0))
        filemenu.add_command(label="Executar todos os arquivos de uma pasta...", command=lambda: self.executarEntrada(1))
        filemenu.add_separator()
        filemenu.add_command(label="Plotar gráficos...", command=lambda: self.abrirInterfacePlotagens())
        filemenu.add_separator()
        filemenu.add_command(label="Fechar programa", command=self.sair)
        menubar.add_cascade(label="Arquivo", menu=filemenu)
        #   Segundo menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Ajuda", foreground="#A9A9A9", activeforeground="#A9A9A9")
        helpmenu.add_command(label="Sobre...", command=lambda: self.abrirAbout())
        menubar.add_cascade(label="Informações", menu=helpmenu)
        #   Mostre o menu
        self.config(menu=menubar)   
    
        #   Nome e versao
        cabecalho = Label(primeiroFrame, text = ("MHE  -  Versão: %5.2f  (Python 3)" %self.versao_do_software), bd = 1, relief = "sunken" , anchor = "w", padx = 25)
        cabecalho.grid(row = 0, column = 0, columnspan = 4, pady = 10, padx = 0, ipady = 10, ipadx = 5)
    
        #    Bi de ibaaaagens cobandante habilton!
        imagemLogo = ImageTk.PhotoImage(Image.open(self.diretorio_do_software + "/lib/Logo.png".encode()))
        imagemLabel = Label(primeiroFrame, image=imagemLogo, bg="#DFF9CA")
        imagemLabel.grid(row = 1, column = 0, columnspan = 4, pady = 0, padx = 0)
        imagemLabel.image = imagemLogo
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def sair(self):
        """Sai do software sem crashar."""
        self.destroy()
        exit()
    #-----------------------------------------------------------------------
    def abrirInterfaceAuxiliar(self):
        """Esta funcao serve pra abrir a janela do passo-a-passo em uma nova janela."""
        #   Pode fechar a janela principal, sera' reiniciada depois
        self.destroy()
        
        #   Abrir a segunda Janela
        InterfaceAuxiliar(self.master, self.versao_do_software, self.diretorio_do_software)
    #-----------------------------------------------------------------------
    def abrirInterfacePlotagens(self):
        """Esta funcao serve pra abrir a janela das plotagens."""
        #   Pode fechar a janela principal, sera' reiniciada depois
        self.destroy()
        
        #   Abrir a segunda Janela
        InterfacePlotagens(self.master, self.versao_do_software, self.diretorio_do_software)
    #-----------------------------------------------------------------------
    def abrirAbout(self):
        """Esta funcao serve pra abrir a janela das informacoes do programa."""
        #   Pode fechar a janela principal, sera' reiniciada depois
        self.destroy()
        
        #   Abrir a segunda Janela
        InterfaceSobre(self.master, self.versao_do_software, self.diretorio_do_software)
    #-----------------------------------------------------------------------
    def executarEntrada(self, isFolder):
        """Esta funcao serve para chamar as funcoes da logica do programa (processamento dos dados)."""
        #   Esconder a janelinha, afinal ela fica congelada mesmo.
        self.withdraw()
        
        #   Rodar as funcoes de calculo das operacoes
        iniciarProcessamento(isFolder, self.diretorio_do_software)
        
        #   Atualizar a interface
        self.update()
        #   Mostrar interface
        self.deiconify()

#-----------------------------------------------------------------------
class InterfaceAuxiliar(Toplevel):
    """Classe responsavel por exibir todas as janelas do ambiente auxiliar do modelo."""
    strings_entrada = []
    strings_estruturas_puls = []
    strings_hidrogramas_jun = []
    n_max_op = 0
    n_max_ch = 0
    n_ch = 0
    n_op = 0
    n_int_op = 0
    n_int_ch = 0
    dir_arq_cotavolume = ""
    #-----------------------------------------------------------------------
    def __init__(self, master, versao_do_software, diretorio_do_software):
        #   Sumir com a janelinha, não gosto dela
        master.withdraw()
        
        #   Facilite minha vida
        self.master = master
        self.versao_do_software = versao_do_software
        self.diretorio_do_software = diretorio_do_software
        
        #   Mudar todos os icones
        icone = ImageTk.PhotoImage(Image.open(self.diretorio_do_software + "/lib/icone.png".encode()))
        self.master.wm_iconphoto(True, icone)
        
        #   Rodar interface
        self.janelaInterfaceAuxiliar()
    #-----------------------------------------------------------------------
    def janelaInterfaceAuxiliar(self):
        """Desenha a janela principal do ambiente auxiliar"""
        #   Cria a janela
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Criar Arquivo de Entrada" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.esvaziarStringsEntrada(cxTextoEntrada,0))
        
        #   Introduzir o frame
        primeiroFrame = Frame(self, bg="#DFF9CA")
        primeiroFrame.pack(padx = 10, pady = 10)
        
        #   Criar barra horizontal
        xscrollbar = Scrollbar(primeiroFrame, orient="horizontal")
        
        #   Text Box
        cxTextoEntrada = scrolledtext.ScrolledText(primeiroFrame, height = 0, width = 0, wrap=NONE, xscrollcommand=xscrollbar.set)
        #   Posicionar
        cxTextoEntrada.grid(row = 1, column = 2, columnspan = 2, rowspan = 6, sticky = "se", padx = 15, pady = 0, ipadx=200, ipady=104)
        
        #   Configurar barra horizontal
        xscrollbar.grid(row = 7, column = 2, columnspan = 2, rowspan = 1, sticky = "n", padx = 15, pady = 0, ipadx=189)
        xscrollbar.config(command=cxTextoEntrada.xview)
        
        #   Quero editar
        cxTextoEntrada.configure(state="disabled")
        
        #   Chamo a funcao para escreve na textbox
        self.strings_entrada = self.atualizarTextBox(cxTextoEntrada, self.strings_entrada)
        
        cxTextoEntrada.focus()
        
        #   Escrever visualizacao
        Label(primeiroFrame, text = "Visualização", bg="#DFF9CA").grid(row = 0, column = 2, columnspan = 2, sticky = "s", padx = 15, pady = 0)
        
        #Button(primeiroFrame, text = "Inserir Comentario", width = 20, command=lambda: self.disableButton()).grid(row = 1, column = 0, columnspan = 2, sticky = "n", padx = 5, pady = 0, ipadx=0)
        self.buttonInfoGerais    = Button(primeiroFrame, text = "Informações Gerais", width = 20)
        self.buttonInserirChuvas = Button(primeiroFrame, text = "Inserir Chuvas"    , width = 20)
        self.buttonInfoGerais   .grid(row = 1, column = 0, columnspan = 2, sticky = "n", padx = 5, pady = 0, ipadx=0)
        self.buttonInserirChuvas.grid(row = 2, column = 0, columnspan = 2, sticky = "n", padx = 5, pady = 5, ipadx=0)
        
        opGroup = LabelFrame(primeiroFrame, text="Operações Hidrológicas", bg="#DFF9CA")
        opGroup.grid(row = 3, column = 0, columnspan = 2, sticky = "n", padx = 5, pady = 3, ipadx = 0, ipady=5)
        #   Botoes
        self.buttonInserirPQ        = Button(opGroup, text = "Op. Chuva-Vazão"    , width = 20)
        self.buttonInserirPULS      = Button(opGroup, text = "Op. PULS"           , width = 20)
        self.buttonInserirMKC       = Button(opGroup, text = "Op. Muskingum-Cunge", width = 20)
        self.buttonInserirJUN       = Button(opGroup, text = "Op. Junção"         , width = 20)
        self.buttonInserirHIDRO     = Button(opGroup, text = "Ler Hidrograma"     , width = 20)
        self.buttonInserirDerivacao = Button(opGroup, text = "Inserir Derivação"  , width = 20)
        #   Grids
        self.buttonInserirPQ       .grid(row = 0, column = 0, columnspan = 2, sticky = "n", padx = 10, pady = 5, ipadx=0)
        self.buttonInserirPULS     .grid(row = 1, column = 0, columnspan = 2, sticky = "n", padx = 10, pady = 0, ipadx=0)
        self.buttonInserirMKC      .grid(row = 2, column = 0, columnspan = 2, sticky = "n", padx = 10, pady = 5, ipadx=0)
        self.buttonInserirJUN      .grid(row = 3, column = 0, columnspan = 2, sticky = "n", padx = 10, pady = 0, ipadx=0)
        self.buttonInserirHIDRO    .grid(row = 4, column = 0, columnspan = 2, sticky = "n", padx = 10, pady = 5, ipadx=0)
        self.buttonInserirDerivacao.grid(row = 5, column = 0, columnspan = 2, sticky = "n", padx = 10, pady = 0, ipadx=0)
        
        #   Botao para salvar o conteudo criado pelo usuario
        self.buttonSalvar = Button(primeiroFrame, text = "Salvar", width = 10)
        self.buttonFechar = Button(primeiroFrame, text = "Fechar", width = 10)
        self.buttonSalvar.grid(row = 8, column = 3, columnspan = 1, sticky = "e", padx = 15, pady = 5)
        self.buttonFechar.grid(row = 8, column = 2, columnspan = 1, sticky = "w", padx = 15, pady = 5)
        
        #   Comecando a escrever o arquivo, nao ha nem informacoes iniciais
        if ((self.n_max_ch == 0) and (self.n_max_op == 0)):
            #   Info geral
            self.buttonInfoGerais.configure(fg="#000000", command=lambda: self.inserirInformacoesGerais())
            #   Chuvas
            self.buttonInserirChuvas.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Operacoes
            self.buttonInserirPQ.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirPULS.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirMKC.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirJUN.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirHIDRO.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirDerivacao.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Ultimos botes
            self.buttonSalvar.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonFechar.configure(text = "Fechar", command=lambda: self.esvaziarStringsEntrada(cxTextoEntrada,0))
            #   Bindar ESC para fechar
            self.bind("<Escape>", lambda i: self.esvaziarStringsEntrada(cxTextoEntrada,i))
            
        #   desabilita tudo e habilita o "save"
        elif ((self.n_ch == self.n_max_ch) and (self.n_op == self.n_max_op)):
            #   Info geral
            self.buttonInfoGerais.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Chuvas
            self.buttonInserirChuvas.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Operacoes
            self.buttonInserirPQ.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirPULS.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirMKC.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirJUN.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirHIDRO.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonInserirDerivacao.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Ultimos botoes
            self.buttonSalvar.configure(fg="#000000", command=lambda: self.criarArquivo())
            self.buttonFechar.configure(text = "Desfazer", command=lambda: self.desfazerUltimoComando(cxTextoEntrada,0))
            #   Bindar ESC para voltar
            self.bind("<Escape>", lambda i: self.desfazerUltimoComando(cxTextoEntrada,i))
        
        #   Falta algo, ou chuva, ou operacao, ou ambos
        else:
            #   Info geral
            self.buttonInfoGerais.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Chuvas completas
            if self.n_ch == self.n_max_ch:
                self.buttonInserirChuvas.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Chuvas INcompletas:
            else:
                self.buttonInserirChuvas.configure(fg="#000000", command=lambda: self.inserirChuvas())
            #   Operacoes completas
            if self.n_op == self.n_max_op:
                self.buttonInserirPQ.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirPULS.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirMKC.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirJUN.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirHIDRO.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirDerivacao.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            #   Operacoes estao INcompletas
            else:
                self.buttonInserirPQ.configure(fg="#000000", command=lambda: self.inserirPQ())
                self.buttonInserirPULS.configure(fg="#000000", command=lambda: self.inserirPULS())
                self.buttonInserirMKC.configure(fg="#000000", command=lambda: self.inserirMKC())
                self.buttonInserirJUN.configure(fg="#000000", command=lambda: self.inserirJuncao())
                self.buttonInserirHIDRO.configure(fg="#000000", command=lambda: self.inserirHidrograma())
                self.buttonInserirDerivacao.configure(fg="#000000", command=lambda: self.inserirDerivacao())
            #   Bindar ESC para voltar
            self.bind("<Escape>", lambda i: self.desfazerUltimoComando(cxTextoEntrada,i))
            #   Ultimos botoes
            self.buttonSalvar.configure(fg="#A9A9A9", command=lambda: self.disableButton())
            self.buttonFechar.configure(text = "Desfazer", command=lambda: self.desfazerUltimoComando(cxTextoEntrada,0))

        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def validarFloat(self, novo_texto):
        """"""
        if not novo_texto:
            return True
        try:
            if len(novo_texto) < 9: # Pode digitar somente 8 caracteres
                float(novo_texto)
                if "-" in novo_texto:
                    raise ValueError
                elif " " in novo_texto:
                    raise ValueError
                else:
                    return True
            else:
                raise ValueError
        except ValueError:
            return False
    #-----------------------------------------------------------------------
    def validarFloatAteCem(self, novo_texto):
        """"""
        if not novo_texto:
            return True
        try:
            if len(novo_texto) < 9: # Pode digitar somente 8 caracteres
                if float(novo_texto) > 100:
                    raise ValueError
                elif "-" in novo_texto:
                    raise ValueError
                elif " " in novo_texto:
                    raise ValueError
                else:
                    return True
            else:
                raise ValueError
        except ValueError:
            return False
    #-----------------------------------------------------------------------
    def validarInt(self, novo_texto):
        """"""
        if not novo_texto:
            return True
        try:
            if len(novo_texto) < 7: # Pode digitar somente 6 caracteres
                int(novo_texto)
                if "-" in novo_texto:
                    raise ValueError
                elif " " in novo_texto:
                    raise ValueError
                else:
                    return True
            else:
                raise ValueError
        except ValueError:
            return False
    #-----------------------------------------------------------------------
    def validarIntSemZero(self, novo_texto):
        """"""
        if not novo_texto: # o campo esta sendo limpo
            return True
        try:
            if len(novo_texto) < 7: # Pode digitar somente 6 caracteres
                if int(novo_texto) == 0:
                    raise ValueError
                elif "-" in novo_texto:
                    raise ValueError
                elif " " in novo_texto:
                    raise ValueError
                else:
                    return True
            else:
                raise ValueError
        except ValueError: #forcar erro
            return False #falso para nao digitar
    #-----------------------------------------------------------------------
    def disableButton(self):
        """Essa funcao e' assim mesmo, ela nao faz nada... e' para desabilitar um botao."""
        pass
    #-----------------------------------------------------------------------
    def desfazerUltimoComando(self, cxTexto, evento):
        """Faz parte da logica para o funcionamento da interface grafica"""
        #   Preferi fazer uma funcao especifica para a string de resumo do conteudo pois resulta em funcoes mais simples (porem em mais funcoes)
        if len(self.strings_entrada) > 0:
            #   Ver o que foi deletado
            ultima_string = self.strings_entrada[-1]
            
            #   Se for a primeira linha...
            if ultima_string.split(";")[0] == "INICIO":
                #   Volte a estaca zero
                self.n_ch = 0
                self.n_op = 0
                self.n_max_op = 0
                self.n_max_ch = 0
                self.n_int_ch = 0
                self.n_int_op = 0
                
                #   Reconfigurar os botoes
                self.buttonInfoGerais.configure(fg="#000000", command=lambda: self.inserirInformacoesGerais())
                #   Chuvas
                self.buttonInserirChuvas.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                #   Operacoes
                self.buttonInserirPQ.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirPULS.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirMKC.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirJUN.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirHIDRO.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonInserirDerivacao.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                #   Ultimos botes
                self.buttonSalvar.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonFechar.configure(text = "Fechar", command=lambda: self.esvaziarStringsEntrada(cxTexto,0))
                #   Bindar ESC para fechar
                self.bind("<Escape>", lambda i: self.esvaziarStringsEntrada(cxTexto,i))
                
            #   Se for Chuva
            if ultima_string.split(";")[0] == "CHUVA":
                #   Reduza um n_ch
                self.n_ch -= 1
                
                #   Reconfigurar os botoes
                self.buttonInfoGerais.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                #   Chuvas
                self.buttonInserirChuvas.configure(fg="#000000", command=lambda: self.inserirChuvas())
                #   Operacoes completas
                if self.n_op == self.n_max_op:
                    self.buttonInserirPQ.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                    self.buttonInserirPULS.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                    self.buttonInserirMKC.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                    self.buttonInserirJUN.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                    self.buttonInserirHIDRO.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                    self.buttonInserirDerivacao.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                #   Operacoes estao INcompletas
                else:
                    self.buttonInserirPQ.configure(fg="#000000", command=lambda: self.inserirPQ())
                    self.buttonInserirPULS.configure(fg="#000000", command=lambda: self.inserirPULS())
                    self.buttonInserirMKC.configure(fg="#000000", command=lambda: self.inserirMKC())
                    self.buttonInserirJUN.configure(fg="#000000", command=lambda: self.inserirJuncao())
                    self.buttonInserirHIDRO.configure(fg="#000000", command=lambda: self.inserirHidrograma())
                    self.buttonInserirDerivacao.configure(fg="#000000", command=lambda: self.inserirDerivacao())
                #   Ultimos botoes
                self.buttonSalvar.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonFechar.configure(text = "Desfazer", command=lambda: self.desfazerUltimoComando(cxTexto,0))
                #   Bindar ESC para voltar
                self.bind("<Escape>", lambda i: self.desfazerUltimoComando(cxTexto,i))
                
            #   Se for Operacao
            if ultima_string.split(";")[0] == "OPERACAO":
                #   Reduza um n_ch
                self.n_op -= 1            
            
                #   Reconfigurar os botoes
                self.buttonInfoGerais.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                #   Chuvas completas
                if self.n_ch == self.n_max_ch:
                    self.buttonInserirChuvas.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                #   Chuvas INcompletas:
                else:
                    self.buttonInserirChuvas.configure(fg="#000000", command=lambda: self.inserirChuvas())
                #   Operacoes
                self.buttonInserirPQ.configure(fg="#000000", command=lambda: self.inserirPQ())
                self.buttonInserirPULS.configure(fg="#000000", command=lambda: self.inserirPULS())
                self.buttonInserirMKC.configure(fg="#000000", command=lambda: self.inserirMKC())
                self.buttonInserirJUN.configure(fg="#000000", command=lambda: self.inserirJuncao())
                self.buttonInserirHIDRO.configure(fg="#000000", command=lambda: self.inserirHidrograma())
                self.buttonInserirDerivacao.configure(fg="#000000", command=lambda: self.inserirDerivacao())
                #   Ultimos botoes
                self.buttonSalvar.configure(fg="#A9A9A9", command=lambda: self.disableButton())
                self.buttonFechar.configure(text = "Desfazer", command=lambda: self.desfazerUltimoComando(cxTexto,0))
                #   Bindar ESC para voltar
                self.bind("<Escape>", lambda i: self.desfazerUltimoComando(cxTexto,i))
                
            #   Delete a ultima coisa 
            del self.strings_entrada[-1]
            
            #   Modifique o texto da textbox
            self.strings_entrada = self.atualizarTextBox(cxTexto, self.strings_entrada)
    #-----------------------------------------------------------------------
    def procurarArquivoBotao(self, caso):
        """"""
        #   Abra-!
        self.withdraw()
        
        #   Informacao de curva cota-volume: clicou, resetou
        if caso == 1:
            #   Modificar o botao
            self.buttonCotaVolume.configure(fg="#000000", text = "Procurar arquivo")
            self.buttonCotaVolume.grid(ipadx=6)
            #   Resetar diretorio
            self.dir_arq_cotavolume = ""
        
        #   Procure o arquivo...
        diretorio_arquivo_entrada = procurarArquivo(self.diretorio_do_software)
        
        #   Verificar se algo foi selecionado
        if (not diretorio_arquivo_entrada == None):
            #   Verificar se o arquivo existe
            if (path.isfile(diretorio_arquivo_entrada) == True):
                #   Armazenar extensao do arquivo
                extensao_arquivo = diretorio_arquivo_entrada.decode().split("/")[-1]
                extensao_arquivo = extensao_arquivo.split(".")[-1]
                #   Verificar se a extensao dele e' txt
                if ((extensao_arquivo == "txt") or (extensao_arquivo == "TXT")):
                    #   Testar qual variavel deve ser modificada
                    #   Informacao de chuva observada
                    if caso == 0:
                        #   Falta verificar a integridade desse arquivo de chuva
                        integridade_arquivo, linha = checarIntegridadeArquivoTexto(diretorio_arquivo_entrada, self.n_int_ch)
                        #   Se o arquivo for valido
                        if integridade_arquivo == True:
                            #   Armazenar
                            self.dir_arq_chuva = diretorio_arquivo_entrada.decode()
                            #   But here's my NUMBER ONEE! (HEY!!!)
                            self.strings_entrada.append("CHUVA; " + str(self.n_ch+1) + "; " + self.chuva_local + "OBS; " + str(self.dir_arq_chuva) + ";\n")
                            #   Resetar, ja armazenei-o
                            self.dir_arq_chuva = ""
                            #   Resetar
                            self.chuva_local = "\n"
                            #   Somar uma chuva
                            self.n_ch += 1
                            #   Sumir com a janela antiga
                            self.fecharJanelaSecundaria(0)
                        #   SE nao for valido
                        else:
                            #   Que ruim que deu?
                            if linha == 0: #    Numero de dados incorretos
                                mensagensIntegridadeArquivosObservados(1, linha, (self.n_ch+1), self.n_op, self.n_int_ch, self.n_int_op)
                            else: # Linha X e' o problema
                                mensagensIntegridadeArquivosObservados(2, linha, (self.n_ch+1), self.n_op, self.n_int_ch, self.n_int_op)
                    
                    #   Informacao de curva cota-volume
                    elif caso == 1:
                        #   Falta verificar a integridade desse arquivo de cota-volume
                        integridade_arquivo, linha = checarIntegridadeArquivoCotaVolume(diretorio_arquivo_entrada)
                        #   Se o arquivo for valido
                        if integridade_arquivo == True:
                            #   Armazenar
                            self.dir_arq_cotavolume = diretorio_arquivo_entrada.decode()
                            #   Modificar o botao
                            self.buttonCotaVolume.configure(fg="#00B400", text = "Arq. encontrado")
                            self.buttonCotaVolume.grid(ipadx=7)
                        #   SE nao for valido
                        else:
                            #   Que ruim que deu?
                            if linha == 0: #    Numero de dados incorretos
                                mensagensIntegridadeArquivosObservados(5, linha, self.n_ch, (self.n_op+1), self.n_int_ch, self.n_int_op)
                            else: # Linha X e' o problema
                                mensagensIntegridadeArquivosObservados(6, linha, self.n_ch, (self.n_op+1), self.n_int_ch, self.n_int_op)
                    
                    #   Informacao de hidrogramas de entrada
                    elif caso == 2:
                        #   Falta verificar a integridade desse arquivo de chuva
                        integridade_arquivo, linha = checarIntegridadeArquivoTexto(diretorio_arquivo_entrada, self.n_int_op)
                        #   Se o arquivo for valido
                        if integridade_arquivo == True:
                            #   Armazenar
                            self.dir_arq_hidro = diretorio_arquivo_entrada.decode()
                            #   But here's my NUMBER ONEE! (HEY!!!)
                            self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + self.local_hidro + "HIDROGRAMA; " + str(self.dir_arq_hidro) + ";\n")
                            #   Somar uma operacao
                            self.n_op += 1
                            #   Resetar a variavel
                            self.local_hidro = "\n"
                            #   Sumir com a janela antiga
                            self.fecharJanelaSecundaria(0)
                        #   SE nao for valido
                        else:
                            #   Que ruim que deu?
                            if linha == 0: #    Numero de dados incorretos
                                mensagensIntegridadeArquivosObservados(3, linha, self.n_ch, (self.n_op+1), self.n_int_ch, self.n_int_op)
                            else: # Linha X e' o problema
                                mensagensIntegridadeArquivosObservados(4, linha, self.n_ch, (self.n_op+1), self.n_int_ch, self.n_int_op)
                    
                    #   Deu erro, so feche o arquivo
                    else:
                        #   Sumir com a janela antiga, voltar a apresentar a janela com o texto
                        self.fecharJanelaSecundaria(0)
                #   Nao e' arquivo txt
                else:
                    #   Mandar a mensagem para o usuario
                    mensagensInterfaces(1, "")
            #   O arquivo nao existe
            else:
                #   Mandar a mensagem para o usuario
                mensagensInterfaces(2, "")
        #   Selecione algum aquivo de entrada
        else:
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(3, "")
            
        #   Kadabra!
        self.deiconify()
    #-----------------------------------------------------------------------
    def atualizarTextBox(self, cxTexto, string_conteudo):
        """Escreve na textbox"""
        #   Desbloquear
        cxTexto.configure(state="normal")
        
        #   Delete o que tem
        cxTexto.delete(1.0, END)
        
        #   Escrever a string na cxTexto
        for ii in range(len(string_conteudo)):
            #   Escreva linha em linha
            cxTexto.insert(END, string_conteudo[ii])
        
        #   Bloquear novamente
        cxTexto.configure(state="disabled")
        
        #   Retorne a string atualizada
        return string_conteudo
    #-----------------------------------------------------------------------
    def esvaziarStringsEntrada(self, cxTexto, evento):
        """Esvazia a string dos dados, fecha a interface auxiliar e abre a janela inicial"""
        #   Loop para esvaziar a string
        for ii in range(len(self.strings_entrada)):
            #   Delete
            del self.strings_entrada[0]

        #   Chamo a funcao para escreve na textbox
        self.strings_entrada = self.atualizarTextBox(cxTexto, self.strings_entrada)
        
        #   Fechar a janela
        self.destroy()
        
        #   Reinicio a janela principal
        InterfacePrincipal(self.master, self.versao_do_software, self.diretorio_do_software)
    #-----------------------------------------------------------------------
    def fecharJanelaSecundaria(self, evento):
        """Fecha qualquer janela secundaria e abre a interface auxiliar da forma que foi deixada"""
        #   Destrua o conteudo da janela
        self.destroy()
        #   Reinicie a janela principal da visualizacao do arquivo de saida
        self.janelaInterfaceAuxiliar()
    #-----------------------------------------------------------------------
    def manipularInformacaoGeral(self):
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        focus = 0
        
        #   Testar numero operacoes hidrologicas
        if self.entryOphidro.get() == "":
            auxERROS = ERROS
            ERROS = "Informe o número de operações hidrológicas.\n\n"
            ERROS += auxERROS
            focus = 4
        elif int(self.entryOphidro.get()) == 0:
            auxERROS = ERROS
            ERROS = "O número de operações hidrológicas deve ser maior que zero.\n\n"
            ERROS += auxERROS
            focus = 4
        #   Testar numero intervalos de tempo com chuva
        if self.entryNint_tempo_chuva.get() == "":
            auxERROS = ERROS
            ERROS = "Informe o número de intervalos de tempo com chuva.\n\n"
            ERROS += auxERROS
            focus = 3
        #   Testar numero de chuvas
        if self.entryNchuvas.get() == "":
            auxERROS = ERROS
            ERROS = "Informe o número do posto de chuva.\n\n"
            ERROS += auxERROS
            focus = 2
        #   Testar o intervalo de tempo
        if self.entryDt.get() == "":
            auxERROS = ERROS
            ERROS = "Informe a duração do intervalo de tempo (segundos).\n\n"
            ERROS += auxERROS
            focus = 1
        #   Testar numero de intervalos de tempo
        if self.entryNint_tempo.get() == "":
            auxERROS = ERROS
            ERROS = "Informe o número de intervalos de tempo.\n\n"
            ERROS += auxERROS
            focus = 0
            
        #   checar se foram encontrados erros:
        if not (ERROS == ""):
            #   remover os enters excessivos no final da string
            ERROS = ERROS[0:-2]
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(4, str(ERROS))
            #   Focus na entry correta
            if focus == 0:
                self.entryNint_tempo.focus()
            elif focus == 1:
                self.entryDt.focus()
            elif focus == 2:
                self.entryNchuvas.focus()
            elif focus == 3:
                self.entryNint_tempo_chuva.focus()
            else: 
                self.entryOphidro.focus()
                
        #   Sem erros aparentes...Continue o PROGRAMA 
        else: 
            #   But here's my NUMBER ONEE! (HEY!!!)
            self.strings_entrada.append("INICIO; "+ self.entryNint_tempo.get() + "; " + self.entryDt.get() + "; " + self.entryNchuvas.get() + "; " + self.entryNint_tempo_chuva.get() + "; " + self.entryOphidro.get() + ";\n")
            
            #   Atualizar a variavel de numero maximo de operacoes
            self.n_max_op = int(self.entryOphidro.get())
            
            #   Atualizar a variavel de numero maximo de chuvas
            self.n_max_ch = int(self.entryNchuvas.get())
            
            #   Atualizar a variavel de numero de intervalos de tempo com chuva
            self.n_int_ch = int(self.entryNint_tempo_chuva.get())
            
            #   Atualizar a variavel de numero de intervalos de tempo de simulacao
            self.n_int_op = int(self.entryNint_tempo.get())
            
            #   Sumir com a janela antiga
            self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def inserirInformacoesGerais(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Informações Gerais" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)

        #   TITULO:
        Label(segundoFrame, text= "INFORMAÇÕES GERAIS DA SIMULAÇÃO", bg="#DFF9CA").grid(row=0, column=0, columnspan=4, sticky="n", padx=0, pady=5)

        #   Labels
        Label(segundoFrame, text= "Número de intervalos de tempo:"           , bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 2)
        Label(segundoFrame, text= "Duração do intervalo de tempo (segundos):", bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 0)
        Label(segundoFrame, text= "Número de postos de chuva:"               , bg="#DFF9CA").grid(row = 3, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 2)
        Label(segundoFrame, text= "Número de intervalos de tempo com chuva:" , bg="#DFF9CA").grid(row = 4, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 0)
        Label(segundoFrame, text= "Número de operações hidrológicas:"        , bg="#DFF9CA").grid(row = 5, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 2)
        #   Registers
        nint_tempo       = self.register(self.validarIntSemZero)
        dt               = self.register(self.validarIntSemZero)
        nchuvas          = self.register(self.validarInt)
        nint_tempo_chuva = self.register(self.validarInt)
        ophidro          = self.register(self.validarIntSemZero)
        #   Entries
        self.entryNint_tempo       = Entry(segundoFrame, validate="key", width=1, validatecommand=(nint_tempo, "%P"))
        self.entryDt               = Entry(segundoFrame, validate="key", width=1, validatecommand=(dt, "%P"))
        self.entryNchuvas          = Entry(segundoFrame, validate="key", width=1, validatecommand=(nchuvas, "%P"))
        self.entryNint_tempo_chuva = Entry(segundoFrame, validate="key", width=1, validatecommand=(nint_tempo_chuva, "%P"))
        self.entryOphidro          = Entry(segundoFrame, validate="key", width=1, validatecommand=(ophidro, "%P"))
        #   Grids
        self.entryNint_tempo      .grid(row = 1, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=35)
        self.entryDt              .grid(row = 2, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=35)
        self.entryNchuvas         .grid(row = 3, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=35)
        self.entryNint_tempo_chuva.grid(row = 4, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=35)
        self.entryOphidro         .grid(row = 5, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=35)

        #   botao proximo
        Button(segundoFrame, text = "Próximo", width = 10, command=lambda: self.manipularInformacaoGeral()).grid(row = 6, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 5 )
        #   botao voltar
        Button(segundoFrame, text = "Voltar", width = 10, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 6, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 5 )
        
        self.entryNint_tempo.focus()
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def manipularInserirChuva(self, tipo_chuva):
        """"""
        #   Preguica de fazer uma funcao nova so' para isso....
        if not len(self.entryChuvaLocal.get()) == 0:
            self.chuva_local = (self.entryChuvaLocal.get() + ";\n")
        else:
            self.chuva_local = "\n"
            
        #   Se for chuva observada...
        if tipo_chuva == 0:
            #   Procurar arquivo
            self.procurarArquivoBotao(0)
        #   Se for chuva de IDF
        elif tipo_chuva == 1:
            #   Chamar funcao da janela IDF
            self.inserirIDF()
    #-----------------------------------------------------------------------
    def inserirChuvas(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Informação Pluvial" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)

        #   TITULO:
        Label(segundoFrame, text= "INSERIR CHUVA À SIMULAÇÃO", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 5 )
        
        #   Nome/local da chuva
        Label(segundoFrame,text= "Local de origem:", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 3 )
        #   Caixa do comentario
        self.entryChuvaLocal = Entry(segundoFrame, width = 20)
        self.entryChuvaLocal.grid(row = 1, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        
        #   botao IDF
        Button(segundoFrame, text = "Gerar chuva a partir de uma IDF", width = 34, command=lambda: self.manipularInserirChuva(1)).grid(row = 2, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 3 )
        #   botao OBS
        Button(segundoFrame, text = "Inserir chuva de um arquivo (txt)", width = 34, command=lambda: self.manipularInserirChuva(0)).grid(row = 3, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 3 )
        #   botao sair
        Button(segundoFrame, text = "Voltar", width = 34, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 4, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 3 )
        
        #   Focus
        self.entryChuvaLocal.focus()
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def manipularInserirIDF(self):
        """"""
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        focus = 0
        
        #   Testar D
        if self.entryParametroD.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o parametro D da equação IDF.\n\n")
            ERROS += auxERROS
            focus = 6
        #   Testar C
        if self.entryParametroC.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o parametro C da equação IDF.\n\n")
            ERROS += auxERROS
            focus = 5
        #   Testar B
        if self.entryParametroB.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o parametro B da equação IDF.\n\n")
            ERROS += auxERROS
            focus = 4
        #   Testar A
        if self.entryParametroA.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o parametro A da equação IDF.\n\n")
            ERROS += auxERROS
            focus = 3
        #   Testar TR
        if self.entryTemporetorno.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o tempo de recorrência da chuva (anos).\n\n")
            ERROS += auxERROS
            focus = 2
        #   Testar PP
        if self.entryPospico.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o valor de posição do pico (entre 0 e 100).\n\n")
            ERROS += auxERROS
            focus = 1
            
        if self.entryLimite.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o valor limite de intensidade para os primeiros intervalos de tempo de chuva (minutos).\n\nDica: Utilize zero para desabilitar esta opção.\n\n")
            ERROS += auxERROS
            focus = 0
            
        #   checar se foram encontrados erros:
        if not (ERROS == ""):
            #   remover os enters excessivos no final da string
            ERROS = ERROS[0:-2]
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(4, str(ERROS))
            #   Focus na entry correta
            if focus == 0:
                self.entryLimite.focus()
            elif focus == 1:
                self.entryPospico.focus()
            elif focus == 2:
                self.entryTemporetorno.focus()
            elif focus == 3:
                self.entryParametroA.focus()
            elif focus == 4:
                self.entryParametroB.focus()
            elif focus == 5:
                self.entryParametroC.focus()
            else: 
                self.entryParametroD.focus()

        #   Sem erros aparentes...Continue o PROGRAMA 
        else: 
            #   But here's my NUMBER ONEE! (HEY!!!)
            self.strings_entrada.append("CHUVA; " + str(self.n_ch+1) + "; " + self.chuva_local + "IDF; " +  str(self.valorTipoIDF.get()) + "; " + str(float(self.entryPospico.get())/100.) + "; " + self.entryTemporetorno.get() + "; " + self.entryParametroA.get() + "; " + self.entryParametroB.get() + "; " + self.entryParametroC.get() + "; " + self.entryParametroD.get() + "; " + self.entryLimite.get() + ";\n")
            
            #   Somar uma chuva
            self.n_ch += 1
            
            #   Sumir com a janela antiga
            self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def cancelarChuvaIDF(self):
        """"""
        self.chuva_local = "\n"
        self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def inserirIDF(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Chuva de IDF" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)

        #   TITULO:
        Label(segundoFrame, text= "INFORMAÇÕES DA IDF", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 5 )
    
        #   Tipo da IDF : So' ha' uma ate' a versao atual
        Label(segundoFrame,text= "Tipo da IDF:", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 0 )
        #   Cria a variavel que controla os botoes
        self.valorTipoIDF = IntVar()
        self.valorTipoIDF.set(1)
        #   Cria os botoes pra clicar
        Checkbutton(segundoFrame, text = "Tipo 1", bg="#DFF9CA", activebackground="#DFF9CA", variable = self.valorTipoIDF, onvalue = 1, offvalue = 1).grid(row = 1, column = 2, columnspan = 2, sticky = "w", padx = 0, pady = 3 )
        
        #   Labels
        Label(segundoFrame,text= "Posição do pico (%):"            , bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 2)
        Label(segundoFrame,text= "Tempo de retorno da chuva:"      , bg="#DFF9CA").grid(row = 3, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 0)
        Label(segundoFrame,text= "Parâmetro A da IDF:"             , bg="#DFF9CA").grid(row = 4, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 2)
        Label(segundoFrame,text= "Parâmetro B da IDF:"             , bg="#DFF9CA").grid(row = 5, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 0)
        Label(segundoFrame,text= "Parâmetro C da IDF:"             , bg="#DFF9CA").grid(row = 6, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 2)
        Label(segundoFrame,text= "Parâmetro D da IDF:"             , bg="#DFF9CA").grid(row = 7, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 0)
        Label(segundoFrame,text= "Limite de intensidade (minutos):", bg="#DFF9CA").grid(row = 8, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 2)
        #   Registers
        pospico      = self.register(self.validarFloatAteCem)
        temporetorno = self.register(self.validarIntSemZero)
        parametroA   = self.register(self.validarFloat)
        parametroB   = self.register(self.validarFloat)
        parametroC   = self.register(self.validarFloat)
        parametroD   = self.register(self.validarFloat)
        limiteIDF    = self.register(self.validarInt)
        #   Entries
        self.entryPospico      = Entry(segundoFrame, validate="key", width=1, validatecommand=(pospico, "%P"))
        self.entryTemporetorno = Entry(segundoFrame, validate="key", width=1, validatecommand=(temporetorno, "%P"))
        self.entryParametroA   = Entry(segundoFrame, validate="key", width=1, validatecommand=(parametroA, "%P"))
        self.entryParametroB   = Entry(segundoFrame, validate="key", width=1, validatecommand=(parametroB, "%P"))
        self.entryParametroC   = Entry(segundoFrame, validate="key", width=1, validatecommand=(parametroC, "%P"))
        self.entryParametroD   = Entry(segundoFrame, validate="key", width=1, validatecommand=(parametroD, "%P"))
        self.entryLimite       = Entry(segundoFrame, validate="key", width=1, validatecommand=(limiteIDF, "%P"))
        #   Grids
        self.entryPospico     .grid(row = 2, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=31)
        self.entryTemporetorno.grid(row = 3, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=31)
        self.entryParametroA  .grid(row = 4, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=31)
        self.entryParametroB  .grid(row = 5, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=31)
        self.entryParametroC  .grid(row = 6, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=31)
        self.entryParametroD  .grid(row = 7, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=31)
        self.entryLimite      .grid(row = 8, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=31)
        
        #   botao proximo
        Button(segundoFrame, text = "Próximo", width = 9, command=lambda: self.manipularInserirIDF()).grid(row = 9, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        #   botao sair
        Button(segundoFrame, text = "Sair", width = 9, command=lambda: self.cancelarChuvaIDF()).grid(row = 9, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        
        #   Foco
        self.entryPospico.focus()
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def habilitaEntryTC(self):
        """"""
        #   Habilite
        self.entryTC.configure(state="normal")
        #   Delete o que esta' escrito
        self.entryTCDifCota.delete(0, END)
        self.entryTCCompCanal.delete(0, END)
        #   Desabilite
        self.entryTCDifCota.configure(state="disabled")
        self.entryTCCompCanal.configure(state="disabled")
    #---------------------------------------------------------------------------
    def habilitaEntryKirpich(self):
        """"""
        #   Delete o que esta' escrito
        self.entryTC.delete(0, END)
        #   Desabilite
        self.entryTC.configure(state="disabled")
        #   Habilite
        self.entryTCDifCota.configure(state="normal")
        self.entryTCCompCanal.configure(state="normal")
    #-----------------------------------------------------------------------
    def manipularInserirPQ(self):
        """"""
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        focus = 0
        
        #   Preguica de fazer uma funcao nova so' para isso....
        if not len(self.entryNomeOperacao.get()) == 0:
            local_operacao = (self.entryNomeOperacao.get() + ";\n")
        else:
            local_operacao = "\n"
        
        #   Testar TC: Se for horas
        if int((self.valorTempoConcentracao.get()) == 1):
            #   Trata-se de valor informado em horas!
            if self.entryTC.get() == "":
                auxERROS = ERROS
                ERROS = ("Informe o tempo de concentração (horas).\n\n")
                ERROS += auxERROS
                focus = 3
        #   Testar TC: Se for Kirpich
        elif int((self.valorTempoConcentracao.get()) == 2):
            #   Trata-se de TC calculado por Kirpich
            #   Testar o comprimento do canal
            if self.entryTCCompCanal.get() == "":
                auxERROS = ERROS
                ERROS = ("Informe o comprimento do principal curso d'água da bacia (km).\n\n")
                ERROS += auxERROS
                focus = 5
            #   Testar Diferenca de cota
            if self.entryTCDifCota.get() == "":
                auxERROS = ERROS
                ERROS = ("Informe a diferença de cota ao longo do curso d'água (m).\n\n")
                ERROS += auxERROS
                focus = 4
        
        #   Testar AREA
        if self.entryArea.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe a área de bacia (km²).\n\n")
            ERROS += auxERROS
            focus = 2
        #   Testar CN
        if self.entryCN.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o coeficiente adimensional CN utilizado no método.\n\n")
            ERROS += auxERROS
            focus = 1
        #   Testar Numero de CHuva
        if self.entryChuvaPQ.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o posto de chuva que será utilizada no método.\n\n")
            ERROS += auxERROS
            focus = 0
        elif int(self.entryChuvaPQ.get()) > self.n_max_ch:
            auxERROS = ERROS
            ERROS = ("Número de chuva incorreto. Há somente %d chuvas declaradas no arquivo de entrada.\n\n"%(self.n_max_ch))
            ERROS += auxERROS
            focus = 0

        #   checar se foram encontrados erros:
        if not (ERROS == ""):
            #   remover os enters excessivos no final da string
            ERROS = ERROS[0:-2]
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(4, str(ERROS))
            #   Focus na entry correta
            if focus == 0:
                self.entryChuvaPQ.focus()
            elif focus == 1:
                self.entryCN.focus()
            elif focus == 2:
                self.entryArea.focus()
            elif focus == 3:
                self.entryTC.focus()
            elif focus == 4:
                self.entryTCDifCota.focus()
            else: 
                self.entryTCCompCanal.focus()

        #   Sem erros aparentes...Continue o PROGRAMA 
        else: 
            #   Testar TC: Se for horas
            if int((self.valorTempoConcentracao.get()) == 1):
                #   Com TC em horas:
                self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "PQ; " + self.entryChuvaPQ.get() + ";\nCN; " + self.entryCN.get() + ";\nHUT; " + self.entryArea.get() + "; " + self.entryTC.get() + ";\n")
                #   Acrescer numero de operacoes
                self.n_op += 1
            #   Se TC de Kirpich
            elif int((self.valorTempoConcentracao.get()) == 2):
                #   Com TC calculado por kirpich
                self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "PQ; " + self.entryChuvaPQ.get() + ";\nCN; " + self.entryCN.get() + ";\nHUT; " + self.entryArea.get() + "; KIRPICH; " + self.entryTCDifCota.get() + "; " + self.entryTCCompCanal.get() + ";\n")
                #   Acrescer numero de operacoes
                self.n_op += 1
            
            #   Sumir com a janela antiga
            self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def inserirPQ(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Operação Chuva-Vazão" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)

        #   TITULO:
        Label(segundoFrame, text= "INFORMAÇÕES CHUVA-VAZÃO", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 10)
    
        #   Label local
        Label(segundoFrame, text= "Nome/local da operação:", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 0)
        #   Caixa de dialogo para entrar local
        self.entryNomeOperacao = Entry(segundoFrame, width = 12)
        self.entryNomeOperacao.grid(row = 1, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0)
    
        #   Chuva numero
        Label(segundoFrame,text= "Número do posto de chuva:", bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 3)
        #   Caixa de dialogo para entrar com qual chuva esta operacao deve usar
        chuvadapq = self.register(self.validarIntSemZero)
        self.entryChuvaPQ = Entry(segundoFrame, validate="key", width=12, validatecommand=(chuvadapq, "%P"))
        self.entryChuvaPQ.grid(row = 2, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 3)

        #   CN
        Label(segundoFrame,text= "Valor estimado do coeficiente CN:", bg="#DFF9CA").grid(row = 3, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 0)
        #   Caixa de dialogo para entrar com CN
        coefCN = self.register(self.validarFloatAteCem)
        self.entryCN = Entry(segundoFrame, validate="key", width=12, validatecommand=(coefCN, "%P"))
        self.entryCN.grid(row = 3, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0)
        
        #   Area
        Label(segundoFrame,text= "Área estimada da bacia (km²):", bg="#DFF9CA").grid(row = 4, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 3)
        #   Caixa de dialogo para entrar com area
        areaBacia = self.register(self.validarFloat)
        self.entryArea = Entry(segundoFrame, validate="key", width=12, validatecommand=(areaBacia, "%P"))
        self.entryArea.grid(row = 4, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        
        #-------------------
        #   TC
        tcGroup = LabelFrame(segundoFrame, text="Tempo de concentração", bg="#DFF9CA")
        tcGroup.grid(row = 5, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 3, ipadx = 4, ipady=3)
        #   cria a variavel que controla os botoes
        self.valorTempoConcentracao = IntVar()
        self.valorTempoConcentracao.set(1)
        #   Primeira linha da groupbox
        Checkbutton(tcGroup, text = "Informar valor (horas):", bg="#DFF9CA", activebackground="#DFF9CA", variable = self.valorTempoConcentracao, onvalue = 1, offvalue = 1, command=lambda: self.habilitaEntryTC()).grid(row = 0, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        Checkbutton(tcGroup, text = "Calcular utilizando a eq. de Kirpich:", bg="#DFF9CA", activebackground="#DFF9CA", variable = self.valorTempoConcentracao, onvalue = 2, offvalue = 2, command=lambda: self.habilitaEntryKirpich()).grid(row = 1, column = 0, columnspan = 4, sticky = "w", padx = 5, pady = 0)
        #   Variaveis das entries
        TC          = self.register(self.validarFloat)
        TTCDifCota  = self.register(self.validarFloat)
        TCCompCanal = self.register(self.validarFloat)
        #   Criar entries
        self.entryTC          = Entry(tcGroup, validate="key", width=13, validatecommand=(TC, "%P"))
        self.entryTCDifCota   = Entry(tcGroup, validate="key", width=13, validatecommand=(TTCDifCota, "%P"))
        self.entryTCCompCanal = Entry(tcGroup, validate="key", width=13, validatecommand=(TCCompCanal, "%P"))
        #   Posicionar Entries
        self.entryTC         .grid(row = 0, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0)
        self.entryTCDifCota  .grid(row = 2, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0)
        self.entryTCCompCanal.grid(row = 3, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0)
        #   Labels
        Label(tcGroup,text= "Diferença de cota (m):", bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 2)
        Label(tcGroup,text= "Comprimento do canal (km):", bg="#DFF9CA").grid(row = 3, column = 0, columnspan = 2, sticky = "e", padx = 5, pady = 2)

        #   Desabilite-as
        self.entryTCDifCota.configure(state="disabled")
        self.entryTCCompCanal.configure(state="disabled")
        
        #   botao proximo
        Button(segundoFrame, text = "Próximo", width=8, command=lambda: self.manipularInserirPQ()).grid(row = 8, column = 2, columnspan = 2, sticky = "e", padx = 5, pady = 3)
        #   botao sair
        Button(segundoFrame, text = "Voltar", width=8, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 8, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        
        #   Foco
        self.entryNomeOperacao.focus()
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def manipularInserirPULS(self):
        """"""
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        focus = 0
        
        #   Preguica de fazer uma funcao nova so' para isso....
        if not len(self.entryNomeOperacao.get()) == 0:
            local_operacao = (self.entryNomeOperacao.get() + ";\n")
        else:
            local_operacao = "\n"
        
        #   Testar estruturas de extravasao
        if len(self.strings_estruturas_puls) == 0:
            auxERROS = ERROS
            ERROS = ("É necessário pelo menos uma estrutura de extravasão.\n\n")
            ERROS += auxERROS
        
        #   Se o diretorio CCV ta vazio
        if self.dir_arq_cotavolume == "":
            auxERROS = ERROS
            ERROS = ("Selecione o arquivo da curva cota-volume.\n\n")
            ERROS += auxERROS
    
        #   Testar valor de by-pass
        if self.entryVazaoByPass.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe um valor de vazão para o by-pass (m³/s).\nUtilize 0 (zero) caso o reservatório for on-line (sem by-pass).\n\n")
            ERROS += auxERROS
            focus = 3
            
        #   Testar cota inicial do reservatorio
        if self.entryCotaReservatorio.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe a cota inicial do reservatório (metros).\nUtilize 0 (zero) caso o reservatório encontrar-se inicialmente vazio.\n\n")
            ERROS += auxERROS
            focus = 2
            
        #   Hidrograma de entrada
        if self.entryHidroEntrada.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o número da operação que servirá de hidrograma de entrada para esta operação.\n\n")
            ERROS += auxERROS
            focus = 1
        elif int(self.entryHidroEntrada.get()) > self.n_max_op:
            auxERROS = ERROS
            ERROS = ("Número de operação incorreto. Há somente %d operações declaradas no arquivo de entrada.\n\n"%(self.n_max_op))
            ERROS += auxERROS
            focus = 1
        elif int(self.entryHidroEntrada.get()) == (self.n_op + 1):
            auxERROS = ERROS
            ERROS = ("Número de operação incorreto. Não é possível utilizar o hidrograma de saída da operação %d como entrada da operação %d.\n\n"%(int(self.entryHidroEntrada.get()), (self.n_op + 1)))
            ERROS += auxERROS
            focus = 1
        
        #   checar se foram encontrados erros:
        if not (ERROS == ""):
            #   remover os enters excessivos no final da string
            ERROS = ERROS[0:-2]
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(4, str(ERROS))
            #   Focus na entry correta
            if focus == 1:
                self.entryHidroEntrada.focus()
            elif focus == 2:
                self.entryCotaReservatorio.focus()
            elif focus == 3:
                self.entryVazaoByPass.focus()
        
        #   Sem erros aparentes...Continue o PROGRAMA 
        else: 
            #   Sera' usada a seguir
            estruturas = ""
            #   "recortar" as estruturas
            for ii in range(len(self.strings_estruturas_puls)):
                #   Adicione
                estruturas += self.strings_estruturas_puls[ii]
            
            #   Com hidrograma de outra operacao:
            self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "PULS; " + self.entryHidroEntrada.get() + "; " + self.entryCotaReservatorio.get() + "; " + self.entryVazaoByPass.get() + "; " + str(len(self.strings_estruturas_puls)) + ";\n" + estruturas + self.dir_arq_cotavolume + ";\n")
            #   Acrescer numero de operacoes
            self.n_op += 1

            #   Resetar
            self.strings_estruturas_puls = []
            self.dir_arq_cotavolume = ""
            
            #   Sumir com a janela antiga
            self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def desfazerUltimaEstruturaPULS(self, cxTexto):
        """"""
        #   E' preciso chamar especificamente self.strings_estruturas pois essa funcao nao pode retornar nada
        if len(self.strings_estruturas_puls) > 0:
            del self.strings_estruturas_puls[-1]
        
            #   Se nao sobrou nada
            if len(self.strings_estruturas_puls) == 0:
                #   Desabilite o botao
                self.buttonPulsUndo.configure(fg="#A9A9A9", command=lambda: self.disableButton())
        
        #   Chamo a funcao para escreve na textbox e "retornar" a variavel
        self.strings_estruturas_puls = self.atualizarTextBox(cxTexto, self.strings_estruturas_puls)
    #-----------------------------------------------------------------------
    def adicionarVertedor(self, cxTexto):
        """"""
        #   Testar as entries
        if not (self.entryCoeficienteVertedor.get() == ""):
            if not (self.entryComprimentoSoleira.get() == ""):
                if not (self.entryCotaSoleira.get() == ""):
                    if not (self.entryCotaMaxVertedor.get() == ""):
                        #   Habilitar o botao de remocao
                        self.buttonPulsUndo.configure(fg="#000000", command=lambda: self.desfazerUltimaEstruturaPULS(cxTexto))
                        #   adicionar
                        self.strings_estruturas_puls.append("VERTEDOR; " + self.entryCoeficienteVertedor.get() + "; " + self.entryComprimentoSoleira.get() + "; " + self.entryCotaSoleira.get() + "; " + self.entryCotaMaxVertedor.get() + ";\n")
                        
                        #   Chamo a funcao para escreve na textbox
                        self.strings_estruturas_puls = self.atualizarTextBox(cxTexto, self.strings_estruturas_puls)
                        
                        #   Foco
                        self.entryCoeficienteVertedor.focus()
    #-----------------------------------------------------------------------
    def adicionarOrificio(self, cxTexto):
        """"""
        #   Testar as entries
        if not (self.entryCoeficienteOrificio.get() == ""):
            if not (self.entryAlturaOrificio.get() == ""):
                if not (self.entryCotaOrificio.get() == ""):
                    #   Habilitar o botao de remocao
                    self.buttonPulsUndo.configure(fg="#000000", command=lambda: self.desfazerUltimaEstruturaPULS(cxTexto))
                
                    #   adicionar
                    self.strings_estruturas_puls.append("ORIFICIO; " + self.entryCoeficienteOrificio.get() + "; " + self.entryAlturaOrificio.get() + "; " + self.entryCotaOrificio.get() + ";\n")
                    
                    #   Chamo a funcao para escreve na textbox
                    self.strings_estruturas_puls = self.atualizarTextBox(cxTexto, self.strings_estruturas_puls)
                    
                    #   Foco
                    self.entryCoeficienteOrificio.focus()
    #-----------------------------------------------------------------------
    def inserirPULS(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Operação PULS" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)

        #   TITULO:
        Label(segundoFrame, text= "INFORMAÇÕES PULS", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 15, pady = 5)
    
        #   Label local
        Label(segundoFrame, text= "", bg="#DFF9CA").grid(row = 1, column = 1, columnspan = 1, sticky = "e", padx = 0, pady = 2, ipadx=150)
        Label(segundoFrame, text= "Nome/local da operação:", bg="#DFF9CA").grid(row = 1, column = 1, columnspan = 1, sticky = "e", padx = 0, pady = 2)
        self.entryNomeOperacao = Entry(segundoFrame, width=1)
        #   Caixa de dialogo para entrar local
        self.entryNomeOperacao.grid(row = 1, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=50)
        
        #   Labels
        Label(segundoFrame, text= "Número da operação hidrológica de entrada:", bg="#DFF9CA").grid(row = 2, column = 1, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        Label(segundoFrame, text= "Cota inicial do reservatório (m):"         , bg="#DFF9CA").grid(row = 3, column = 1, columnspan = 1, sticky = "e", padx = 0, pady = 2)
        Label(segundoFrame, text= "Vazão do by-pass (m³/s):"                  , bg="#DFF9CA").grid(row = 4, column = 1, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        #   Registers
        hidroEntrada     = self.register(self.validarIntSemZero)
        CotaReservatorio = self.register(self.validarFloat)
        vazaoByPass      = self.register(self.validarFloat)
        #   Entries
        self.entryHidroEntrada     = Entry(segundoFrame, validate="key", width=1, validatecommand=(hidroEntrada, "%P"))
        self.entryCotaReservatorio = Entry(segundoFrame, validate="key", width=1, validatecommand=(CotaReservatorio, "%P"))
        self.entryVazaoByPass      = Entry(segundoFrame, validate="key", width=1, validatecommand=(vazaoByPass, "%P"))
        #   Grids
        self.entryHidroEntrada    .grid (row = 2, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=50)
        self.entryCotaReservatorio.grid (row = 3, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=50)
        self.entryVazaoByPass     .grid (row = 4, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=50)
        
        #   Curva cota volume
        Label(segundoFrame, text= "Selecione o arquivo da cota-volume:", bg="#DFF9CA").grid(row = 5, column = 1, columnspan = 1, sticky = "e", padx = 0, pady = 2)
        #   Caixa de dialogo para entrar com cota
        self.buttonCotaVolume = Button(segundoFrame, text = "Procurar arquivo", command=lambda: self.procurarArquivoBotao(1))
        self.buttonCotaVolume.grid(row = 5, column = 2, columnspan = 2, sticky = "e", padx = 5, pady = 2, ipadx=6)
        
        #-------------------
        #   Segunda groupbox
        estrGroup = LabelFrame(segundoFrame, text="Estruturas de extravasão", bg="#DFF9CA")
        estrGroup.grid(row = 6, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 3, ipady=0)

        Label(estrGroup,text= "VERTEDOR RETANGULAR", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 2, sticky = "n", padx = 5, pady = 0)
        Label(estrGroup,text= "ORIFÍCIO CIRCULAR", bg="#DFF9CA").grid(row = 1, column = 2, columnspan = 2, sticky = "n", padx = 5, pady = 0)
        
        #   Para o vertedor
        Label(estrGroup,text= "Coef. de descarga:", bg="#DFF9CA")      .grid(row = 2, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 1)
        Label(estrGroup,text= "Largura da soleira (m):", bg="#DFF9CA") .grid(row = 3, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        Label(estrGroup,text= "Cota da soleira (m):", bg="#DFF9CA")    .grid(row = 4, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 1)
        Label(estrGroup,text= "Cota máxima (m):", bg="#DFF9CA")        .grid(row = 5, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        CoeficienteVertedor = self.register(self.validarFloat)
        ComprimentoSoleira  = self.register(self.validarFloat)
        CotaSoleira         = self.register(self.validarFloat)
        AlturaVertedor      = self.register(self.validarFloat)
        self.entryCoeficienteVertedor = Entry(estrGroup, validate="key", width=1, validatecommand=(CoeficienteVertedor, "%P"))
        self.entryComprimentoSoleira  = Entry(estrGroup, validate="key", width=1, validatecommand=(ComprimentoSoleira, "%P"))
        self.entryCotaSoleira         = Entry(estrGroup, validate="key", width=1, validatecommand=(CotaSoleira, "%P"))
        self.entryCotaMaxVertedor     = Entry(estrGroup, validate="key", width=1, validatecommand=(AlturaVertedor, "%P"))
        self.entryCoeficienteVertedor.grid(row = 2, column = 1, columnspan = 1, sticky = "w", padx = 0, pady = 1, ipadx=25)
        self.entryComprimentoSoleira .grid(row = 3, column = 1, columnspan = 1, sticky = "w", padx = 0, pady = 1, ipadx=25)
        self.entryCotaSoleira        .grid(row = 4, column = 1, columnspan = 1, sticky = "w", padx = 0, pady = 1, ipadx=25)
        self.entryCotaMaxVertedor    .grid(row = 5, column = 1, columnspan = 1, sticky = "w", padx = 0, pady = 1, ipadx=25)
        #   botao adicionar
        Button(estrGroup, text = "Adicionar Vertedor", command=lambda: self.adicionarVertedor(cxTextoPULS)).grid(row = 6, column = 0, columnspan = 2, sticky = "w", padx = 14, pady = 3, ipadx = 38)
        
        #   Para o vertedor
        Label(estrGroup,text= "Coef. de descarga:", bg="#DFF9CA")  .grid(row = 2, column = 2, columnspan = 1, sticky = "e", padx = 0, pady = 1)
        Label(estrGroup,text= "Altura/diâmetro (m):", bg="#DFF9CA").grid(row = 3, column = 2, columnspan = 1, sticky = "e", padx = 0, pady = 1)
        Label(estrGroup,text= "Cota do centro (m):", bg="#DFF9CA") .grid(row = 4, column = 2, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        CoeficienteOrificio = self.register(self.validarFloat)
        AlturaOrificio      = self.register(self.validarFloat)
        CotaOrificio        = self.register(self.validarFloat)
        self.entryCoeficienteOrificio = Entry(estrGroup, validate="key", width=1, validatecommand=(CoeficienteOrificio, "%P"))
        self.entryAlturaOrificio      = Entry(estrGroup, validate="key", width=1, validatecommand=(AlturaOrificio, "%P"))
        self.entryCotaOrificio        = Entry(estrGroup, validate="key", width=1, validatecommand=(CotaOrificio, "%P"))
        self.entryCoeficienteOrificio.grid(row = 2, column = 3, columnspan = 1, sticky = "w", padx = 0, pady = 1, ipadx=25)
        self.entryAlturaOrificio     .grid(row = 3, column = 3, columnspan = 1, sticky = "w", padx = 0, pady = 1, ipadx=25)
        self.entryCotaOrificio       .grid(row = 4, column = 3, columnspan = 1, sticky = "w", padx = 0, pady = 1, ipadx=25)
        #   botao adicionar orificio
        Button(estrGroup, text = "Adicionar Orifício", command=lambda: self.adicionarOrificio(cxTextoPULS)).grid(row = 6, column = 2, columnspan = 2, sticky = "e", padx = 14, pady = 3, ipadx=38)
        
        #   botao remover ultima estrutura adiciona
        self.buttonPulsUndo = Button(estrGroup, text = "Remover última estrutura adicionada", fg="#A9A9A9", command=lambda: self.disableButton())
        self.buttonPulsUndo.grid(row = 7, column = 0, columnspan = 4, sticky = "e", padx = 14, pady = 0, ipadx=95)
        
        #   Text Box
        cxTextoPULS = scrolledtext.ScrolledText(estrGroup, height = 0, width = 0)
        #   Posicionar
        cxTextoPULS.grid(row = 8, column = 0, columnspan = 4, rowspan = 1, sticky = "w", padx = 14, pady = 6, ipadx = 183, ipady = 0)
        #   Quero editar
        cxTextoPULS.configure(state="disabled")
        
        #   Chamo a funcao para escreve na textbox
        self.strings_estruturas_puls = self.atualizarTextBox(cxTextoPULS, self.strings_estruturas_puls)
        
        #   Configurar o botao de removao de estruturas
        if len(self.strings_estruturas_puls) > 0:
            self.buttonPulsUndo.configure(fg="#000000", command=lambda: self.desfazerUltimaEstruturaPULS(cxTextoPULS))
        
        #   botao proximo
        Button(segundoFrame, text = "Próximo", width = 10, command=lambda: self.manipularInserirPULS()).grid(row = 7, column = 2, columnspan = 2, sticky = "e", padx = 5, pady = 3 )
        #   botao sair
        Button(segundoFrame, text = "Voltar", width = 10, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 7, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3 )
        
        #   Foco
        self.entryNomeOperacao.focus()
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def manipularInserirMKC(self):
        """"""
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        focus = 0
        
        #   Preguica de fazer uma funcao nova so' para isso....
        if not len(self.entryNomeOperacao.get()) == 0:
            local_operacao = (self.entryNomeOperacao.get() + ";\n")
        else:
            local_operacao = "\n"
        
        #   Testar 
        if self.entryCoeficienteRugosidade.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o coeficiente de rugosidade médio.\n\n")
            ERROS += auxERROS
            focus = 5
        
        #   Testar 
        if self.entryLarguraCanalM.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe a largura média do canal (metros).\n\n")
            ERROS += auxERROS
            focus = 4
            
        #   Testar 
        if self.entryComprimentoCanalKM.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o comprimento do canal (quilômetros).\n\n")
            ERROS += auxERROS
            focus = 3
            
        #   Testar 
        if self.entryDiferencaCotaM.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe a diferença de cota do canal (metros).\n\n")
            ERROS += auxERROS
            focus = 2
        
        #   Hidrograma entrada
        if self.entryHidroEntrada.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o número da operação que servirá de hidrograma de entrada para esta operação.\n\n")
            ERROS += auxERROS
            focus = 1
        elif int(self.entryHidroEntrada.get()) > self.n_max_op:
            auxERROS = ERROS
            ERROS = ("Número de operação incorreto. Há somente %d operações declaradas no arquivo de entrada.\n\n"%(self.n_max_op))
            ERROS += auxERROS
            focus = 1
        elif int(self.entryHidroEntrada.get()) == (self.n_op + 1):
            auxERROS = ERROS
            ERROS = ("Número de operação incorreto. Não é possível utilizar o hidrograma de saída da operação %d como entrada da operação %d.\n\n"%(int(self.entryHidroEntrada.get()), (self.n_op + 1)))
            ERROS += auxERROS
            focus = 1
        
        #   checar se foram encontrados erros:
        if not (ERROS == ""):
            #   remover os enters excessivos no final da string
            ERROS = ERROS[0:-2]
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(4, str(ERROS))
            #   Focus na entry correta
            if focus == 1:
                self.entryHidroEntrada.focus()
            elif focus == 2:
                self.entryDiferencaCotaM.focus()
            elif focus == 3:
                self.entryComprimentoCanalKM.focus()
            elif focus == 4:
                self.entryLarguraCanalM.focus()
            elif focus == 5:
                self.entryCoeficienteRugosidade.focus()

        #   Sem erros aparentes...Continue o PROGRAMA 
        else: 
            #   Com hidrograma de outra operacao:
            self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "MKC; " + self.entryHidroEntrada.get() + "; " + self.entryDiferencaCotaM.get() + "; " + self.entryComprimentoCanalKM.get() + "; " + self.entryLarguraCanalM.get() + "; " + self.entryCoeficienteRugosidade.get() + ";\n")
            #   Acrescer numero de operacoes
            self.n_op += 1
            
            #   Sumir com a janela antiga
            self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def inserirMKC(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Operação MKC" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)

        #   TITULO:
        Label(segundoFrame, text= "INFORMAÇÕES MUSKINGUM-CUNGE", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 5 )
    
        #   Label local
        Label(segundoFrame, text= "Nome/local da operação:", bg="#DFF9CA").grid(row = 1, column = 1, columnspan = 1, sticky = "e", padx = 0, pady = 2)
        #   Caixa de dialogo para entrar local
        self.entryNomeOperacao = Entry(segundoFrame, width = 1)
        self.entryNomeOperacao.grid(row = 1, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=35)
        
        #   Labels
        Label(segundoFrame,text= "Número da operação hidrológica de entrada:", bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 0)
        Label(segundoFrame,text= "Diferença de cota (m):"                    , bg="#DFF9CA").grid(row = 3, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 2)
        Label(segundoFrame,text= "Comprimento do canal (km):"                , bg="#DFF9CA").grid(row = 4, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 0)
        Label(segundoFrame,text= "Largura do canal (m):"                     , bg="#DFF9CA").grid(row = 5, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 2)
        Label(segundoFrame,text= "Coeficiente de rugosidade (-):"            , bg="#DFF9CA").grid(row = 6, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 0)
        #   Entries
        hidroEntrada          = self.register(self.validarIntSemZero)
        DiferencaCotaM        = self.register(self.validarFloat)
        ComprimentoCanalKM    = self.register(self.validarFloat)
        LarguraCanalM         = self.register(self.validarFloat)
        CoeficienteRugosidade = self.register(self.validarFloat)
        #   Grids
        self.entryHidroEntrada          = Entry(segundoFrame, validate="key", width=1, validatecommand=(hidroEntrada, "%P"))
        self.entryDiferencaCotaM        = Entry(segundoFrame, validate="key", width=1, validatecommand=(DiferencaCotaM, "%P"))
        self.entryLarguraCanalM         = Entry(segundoFrame, validate="key", width=1, validatecommand=(LarguraCanalM, "%P"))
        self.entryComprimentoCanalKM    = Entry(segundoFrame, validate="key", width=1, validatecommand=(ComprimentoCanalKM, "%P"))
        self.entryCoeficienteRugosidade = Entry(segundoFrame, validate="key", width=1, validatecommand=(CoeficienteRugosidade, "%P"))
        self.entryHidroEntrada         .grid(row = 2, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=35)
        self.entryDiferencaCotaM       .grid(row = 3, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=35)
        self.entryLarguraCanalM        .grid(row = 4, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=35)
        self.entryComprimentoCanalKM   .grid(row = 5, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2, ipadx=35)
        self.entryCoeficienteRugosidade.grid(row = 6, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 0, ipadx=35)
        
        #   botao proximo
        Button(segundoFrame, text = "Próximo", width=10, command=lambda: self.manipularInserirMKC()).grid(row = 7, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        #   botao sair
        Button(segundoFrame, text = "Voltar", width=10, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 7, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        
        #   Foco
        self.entryNomeOperacao.focus()
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def manipularInserirJuncao(self):
        """"""
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        
        #   Preguica de fazer uma funcao nova so' para isso....
        if not len(self.entryNomeOperacao.get()) == 0:
            local_operacao = (self.entryNomeOperacao.get() + ";\n")
        else:
            local_operacao = "\n"

        #   Precisa ter pelo menos 2 hidrogramas na juncao
        if len(self.strings_hidrogramas_jun) < 2:
            auxERROS = ERROS
            ERROS = ("É necessário pelo menos dois hidrogramas em uma junção.\n\n")
            ERROS += auxERROS
        
        #   Se ha' mais que dois, verifica-lo-ei
        else:
            #   cria
            hidrogramas_jun = []
            #   transformar o texto em numeros inteiros
            for hidrograma in (self.strings_hidrogramas_jun):
                hid_aux = int(hidrograma[0:-2])
                hidrogramas_jun.append(hid_aux)
                
            #   Nao pode haver o numero ZERO
            if 0 in hidrogramas_jun:
                auxERROS = ERROS
                ERROS = ("Não há operação 0 (zero). A contagem das operações hidrológicas inicia-se em 1.\n\n")
                ERROS += auxERROS
            
            #   Nao pode ter um valor mais alto que o numero maximo de operacoes hidrologicas
            temErro = False
            erroInd = 0
            for hidrograma in hidrogramas_jun:
                if hidrograma > self.n_max_op:
                    temErro = True
                    erroInd = hidrogramas_jun.index(hidrograma)
                    
            if temErro == True:
                auxERROS = ERROS
                ERROS = ("É impossível unir o hidrograma %d pois há somente %d hidrogramas na simulação.\n\n"%(hidrogramas_jun[erroInd], self.n_max_op))
                ERROS += auxERROS

            #   Nao pode ter numero repetido
            temErro = False
            erroInd = 0
            for hidrograma in hidrogramas_jun:
                contagem = hidrogramas_jun.count(hidrograma)
                if contagem > 1:
                    temErro = True
                    erroInd = hidrogramas_jun.index(hidrograma)
            if temErro == True:
                auxERROS = ERROS
                ERROS = ("O hidrograma %d foi adicionado mais de uma vez à junção.\n\n"%(hidrogramas_jun[erroInd]))
                ERROS += auxERROS
            
            #   Nao pode ter o valor da propria operacao na juncao
            temErro = False
            erroInd = 0
            for hidrograma in hidrogramas_jun:
                if hidrograma == (self.n_op + 1):
                    temErro = True
                    erroInd = hidrogramas_jun.index(hidrograma)
            if temErro == True:
                auxERROS = ERROS
                ERROS = ("Número de operação incorreto. Não é possível utilizar o hidrograma de saída da operação %d como entrada da operação %d.\n\n"%(hidrogramas_jun[erroInd], (self.n_op + 1)))
                ERROS += auxERROS
        
        #   checar se foram encontrados erros:
        if not (ERROS == ""):
            #   remover os enters excessivos no final da string
            ERROS = ERROS[0:-2]
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(4, str(ERROS))
            #   Focus na entry correta
            self.entryAdicionarHidro.focus()

        #   Sem erros aparentes...Continue o PROGRAMA 
        else: 
            #   preparacao
            string_operacao = ""
            for hid in self.strings_hidrogramas_jun:
                string_operacao += hid
            #   Remover bug
            string_operacao = string_operacao[0:-2]
            #   Adicionar texto 'a string de comandos
            self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "JUN; " + string_operacao + ";\n")
            #   Acrescer numero de operacoes
            self.n_op += 1
            #   Resetar
            self.strings_hidrogramas_jun = []
            
            #   Sumir com a janela antiga
            self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def desfazerUltimoHidrogramaJun(self, cxTexto):
        """"""
        if len(self.strings_hidrogramas_jun) > 0:
            del self.strings_hidrogramas_jun[-1]
            
            #   Se nao sobrou nada
            if len(self.strings_hidrogramas_jun) == 0:
                #   Desabilite o botao
                self.buttonJunUndo.configure(fg="#A9A9A9", command=lambda: self.disableButton())
        
        #   Chamo a funcao para escreve na textbox
        self.strings_hidrogramas_jun = self.atualizarTextBox(cxTexto, self.strings_hidrogramas_jun)
    #-----------------------------------------------------------------------
    def adicionarHidrogramaJun(self, cxTexto):
        """"""
        #   Testar as entries
        if not (self.entryAdicionarHidro.get() == ""):
            #   Habilite o botao
            self.buttonJunUndo.configure(fg="#000000", command=lambda: self.desfazerUltimoHidrogramaJun(cxTexto))
            
            #   adicionar: LEMBRETE: Substituir o ultimo caractere (" ") por um ("\n"), pois na hora de ler "quebra-se" a string em ";", e se houver um " " no final, via dar ruim!
            self.strings_hidrogramas_jun.append(self.entryAdicionarHidro.get() + "; ")
            
            #   Chamo a funcao para escreve na textbox
            self.strings_hidrogramas_jun = self.atualizarTextBox(cxTexto, self.strings_hidrogramas_jun)
            
            #   Delete o que esta' escrito
            self.entryAdicionarHidro.delete(0, END)
            
            #   Foco
            self.entryAdicionarHidro.focus()
    #-----------------------------------------------------------------------
    def inserirJuncao(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Operação JUN" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)

        #   TITULO:
        Label(segundoFrame, text= "INFORMAÇÕES JUNÇÃO", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 5 )
    
        #   Label local
        Label(segundoFrame, text= "Nome/local da operação:", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        #   Caixa de dialogo para entrar local
        self.entryNomeOperacao = Entry(segundoFrame, width = 1)
        self.entryNomeOperacao.grid(row = 1, column = 1, columnspan = 3, sticky = "e", padx = 5, pady = 0, ipadx=125)
        
        #   Hidrogramas
        Label(segundoFrame, text= "Número do hidrograma:", bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        #   Caixa de dialogo para entrar com cota
        AdicionarHidro = self.register(self.validarIntSemZero)
        self.entryAdicionarHidro = Entry(segundoFrame, validate="key", width=1, validatecommand=(AdicionarHidro, "%P"))
        self.entryAdicionarHidro.grid (row = 2, column = 1, columnspan = 1, sticky = "e", padx = 5, pady = 2, ipadx=50)
        
        #   Criar barra horizontal
        xscrollbar = Scrollbar(segundoFrame, orient="horizontal")
        
        #   Text Box
        cxTextoJun = scrolledtext.ScrolledText(segundoFrame, height = 0, width = 0, wrap=NONE, xscrollcommand=xscrollbar.set)
        #   Posicionar
        cxTextoJun.grid(row = 3, column = 0, columnspan = 4, rowspan = 1, padx = 5, pady = 0, ipadx = 185, ipady = 5)
        xscrollbar.grid(row = 4, column = 0, columnspan = 4, rowspan = 1, padx = 0, pady = 0, ipadx = 174)
        xscrollbar.config(command=cxTextoJun.xview)
        #   Quero editar
        cxTextoJun.configure(state="disabled")
        
        #   Chamo a funcao para escreve na textbox
        self.strings_hidrogramas_jun = self.atualizarTextBox(cxTextoJun, self.strings_hidrogramas_jun)
        
        #   O code dos botoes a seguir esta' embaixo da caixa de texto pois eles dependem da existencia da caixa para seu correto funcionamento
        #   Portanto, o grid deles e' MENOR que o grid da caixa de texto, pois os mesmos aparecem ACIMA na GUI
        #   botao adicionar
        buttonJunAdd = Button(segundoFrame, text = "Adicionar", width=8, fg="#000000", command=lambda: self.adicionarHidrogramaJun(cxTextoJun))
        buttonJunAdd.grid(row = 2, column = 2, columnspan = 1, padx = 0, pady = 2)
        
        #   botao remover
        self.buttonJunUndo = Button(segundoFrame, text = "Remover", fg="#A9A9A9", command=lambda: self.disableButton(), width=8)
        self.buttonJunUndo.grid(row = 2, column = 3, columnspan = 1, sticky = "e", padx = 5, pady = 2)
        
        #   Configurar botao remover - correcao de bug: Se voltar 'a interface auxiliar com operacoes escritas na caixa de texto e, em seguida, retornar novamente para inserir mais JUN, o botao de remover permanecia inativo
        if len(self.strings_hidrogramas_jun) > 0:
            self.buttonJunUndo.configure(fg="#000000", command=lambda: self.desfazerUltimoHidrogramaJun(cxTextoJun))
        
        #   botao proximo
        Button(segundoFrame, text = "Próximo", width=9, command=lambda: self.manipularInserirJuncao()).grid(row = 5, column = 3, columnspan = 1, sticky = "e", padx = 5, pady = 3)
        #   botao sair
        Button(segundoFrame, text = "Voltar", width=9, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 5, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        
        #   Foco
        self.entryNomeOperacao.focus()
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def manipularInserirHidrograma(self):
        """"""
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        focus = 0
        
        #   Preguica de fazer uma funcao nova so' para isso....
        if not len(self.entryNomeOperacao.get()) == 0:
            self.local_hidro = (self.entryNomeOperacao.get() + ";\n")
        else:
            self.local_hidro = "\n"
        
        #   Procurar arquivo
        self.procurarArquivoBotao(2)
    #-----------------------------------------------------------------------
    def inserirHidrograma(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Inserir Hidrogramas" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)
        
        #   TITULO:
        Label(segundoFrame, text= "INSERIR HIDROGRAMA OBSERVADO", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 5 )
        
        #   Label local
        Label(segundoFrame, text= "Nome/local do hidrograma:", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 2)
        #   Caixa de dialogo para entrar local
        self.entryNomeOperacao = Entry(segundoFrame, width = 10)
        self.entryNomeOperacao.grid(row = 1, column = 2, columnspan = 2, sticky = "w", padx = 5, pady = 2)
        
        #   botao sair
        Button(segundoFrame, text = "Procurar Arquivo", width=16, command=lambda: self.manipularInserirHidrograma()).grid(row = 2, column = 1, columnspan = 3, sticky = "e", padx = 5, pady = 3)
        
        #   botao sair
        Button(segundoFrame, text = "Voltar", width=9, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 2, column = 0, columnspan = 1, sticky = "w", padx = 5, pady = 3)
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def manipularDerivacao(self):
        """"""
        #   checar erros basicos:
        auxERROS = ""
        ERROS = "" #string que armazena os erros dos dados de entrada.
        focus = 0
        
        #   Preguica de fazer uma funcao nova so' para isso....
        if not len(self.entryNomeOperacao.get()) == 0:
            local_operacao = (self.entryNomeOperacao.get() + ";\n")
        else:
            local_operacao = "\n"
            
        #   Hidrograma de entrada
        if self.entryHidroEntrada.get() == "":
            auxERROS = ERROS
            ERROS = ("Informe o número da operação que servirá de hidrograma de entrada para esta operação.\n\n")
            ERROS += auxERROS
            focus = 4
        elif int(self.entryHidroEntrada.get()) > self.n_max_op:
            auxERROS = ERROS
            ERROS = ("Número de operação incorreto. Há somente %d operações declaradas no arquivo de entrada.\n\n"%(self.n_max_op))
            ERROS += auxERROS
            focus = 4
        elif int(self.entryHidroEntrada.get()) == (self.n_op + 1):
            auxERROS = ERROS
            ERROS = ("Número de operação incorreto. Não é possível utilizar o hidrograma de saída da operação %d como entrada da operação %d.\n\n"%(int(self.entryHidroEntrada.get()), (self.n_op + 1)))
            ERROS += auxERROS
            focus = 4
        
        #   CONSTANTE
        if int(self.tipoDerivacao.get()) == 1:
            #   Testar 
            if self.entryOpDerivacaoConstante.get() == "":
                auxERROS = ERROS
                ERROS = ("Informe o valor de vazão da derivação (m³/s).\n\n")
                ERROS += auxERROS
                focus = 3
            elif float(self.entryOpDerivacaoConstante.get()) == 0.0:
                auxERROS = ERROS
                ERROS = ("O valor de vazão da derivação (m³/s) deve ser maior que zero.\n\n")
                ERROS += auxERROS
                focus = 3
        #   PORCENTAGEM
        elif int(self.tipoDerivacao.get()) == 2:
            #   Testar 
            if self.entryOpDerivacaoPorcentagem.get() == "":
                auxERROS = ERROS
                ERROS = ("Informe a porcentagem de cada intervalo da derivação (%).\n\n")
                ERROS += auxERROS
                focus = 2
            elif float(self.entryOpDerivacaoPorcentagem.get()) == 0.0:
                auxERROS = ERROS
                ERROS = ("A porcentagem de derivação de cada intervalo deve ser maior que zero.\n\n")
                ERROS += auxERROS
                focus = 2
        #   HIDROGRAMA
        else:
            #   Testar 
            if self.entryOpDerivacaoHidrograma.get() == "":
                auxERROS = ERROS
                ERROS = ("Informe o número do hidrograma que será utilizado como derivação.\n\n")
                ERROS += auxERROS
                focus = 1
            elif int(self.entryOpDerivacaoHidrograma.get()) > self.n_max_op:
                auxERROS = ERROS
                ERROS = ("Número de hidrograma incorreto. Há somente %d hidrogramas declarados no arquivo de entrada.\n\n"%(self.n_max_op))
                ERROS += auxERROS
                focus = 1
            elif int(self.entryOpDerivacaoHidrograma.get()) == (self.n_op + 1):
                auxERROS = ERROS
                ERROS = ("Número de hidrograma incorreto. Não é possível utilizar o hidrograma de saída da operação %d como entrada da operação %d.\n\n"%(int(self.entryOpDerivacaoHidrograma.get()), (self.n_op + 1)))
                ERROS += auxERROS
                focus = 1
            elif int(self.entryOpDerivacaoHidrograma.get()):
                auxERROS = ERROS
                ERROS = ("Número de hidrograma incorreto. O número da operação deve ser maior que zero.\n\n")
                ERROS += auxERROS
                focus = 1
            
        #   checar se foram encontrados erros:
        if not (ERROS == ""):
            #   remover os enters excessivos no final da string
            ERROS = ERROS[0:-2]
            #   Mandar a mensagem para o usuario
            mensagensInterfaces(4, str(ERROS))
            #   Focus na entry correta
            if focus == 1:
                self.entryOpDerivacaoHidrograma.focus()
            elif focus == 2:
                self.entryOpDerivacaoPorcentagem.focus()
            elif focus == 3:
                self.entryOpDerivacaoConstante.focus()
            else:
                self.entryHidroEntrada.focus()
        
        #   Sem erros
        else:
            #   Tipo derivacao constante
            if int(self.tipoDerivacao.get()) == 1:
                #   Se sai o hidrograma do curso principal
                if int(self.tipoSaidaDerivacao.get()) == 1:
                    #   
                    self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "DERIVACAO; " + self.entryHidroEntrada.get() + "; CONSTANTE; " + self.entryOpDerivacaoConstante.get() + "; PRINCIPAL;\n")
                #   Se sai o hidrograma da derivacao
                else:
                    #   
                    self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "DERIVACAO; " + self.entryHidroEntrada.get() + "; CONSTANTE; " + self.entryOpDerivacaoConstante.get() + "; DERIVADO;\n")
                
            #   Tipo derivacao porcentagem
            elif int(self.tipoDerivacao.get()) == 2:
                #   Se sai o hidrograma do curso principal
                if int(self.tipoSaidaDerivacao.get()) == 1:
                    #   
                    self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "DERIVACAO; " + self.entryHidroEntrada.get() + "; PORCENTAGEM; " + self.entryOpDerivacaoPorcentagem.get() + "; PRINCIPAL;\n")
                #   Se sai o hidrograma da derivacao
                else:
                    #   
                    self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "DERIVACAO; " + self.entryHidroEntrada.get() + "; PORCENTAGEM; " + self.entryOpDerivacaoPorcentagem.get() + "; DERIVADO;\n")
                
            #   Tipo derivacao Hidrograma
            else:
                #   Se sai o hidrograma do curso principal
                if int(self.tipoSaidaDerivacao.get()) == 1:
                    #   
                    self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "DERIVACAO; " + self.entryHidroEntrada.get() + "; HIDROGRAMA; " + self.entryOpDerivacaoHidrograma.get() + "; PRINCIPAL;\n")
                #   Se sai o hidrograma da derivacao
                else:
                    #   
                    self.strings_entrada.append("OPERACAO; " + str(self.n_op+1) + "; " + local_operacao + "DERIVACAO; " + self.entryHidroEntrada.get() + "; HIDROGRAMA; " + self.entryOpDerivacaoHidrograma.get() + "; DERIVADO;\n")
            
            #   Acrescer numero de operacoes
            self.n_op += 1                
            #   Sumir com a janela antiga
            self.fecharJanelaSecundaria(0)
    #-----------------------------------------------------------------------
    def SelecionaTipoDerivacao(self, escolha):
        """"""
        #   Caso clicou no constante
        if escolha == 1:
            #   Habilite o constante
            self.entryOpDerivacaoConstante.configure(state="normal")
            
            #   Delete o que estiver escrito nos demais
            self.entryOpDerivacaoPorcentagem.delete(0, END)
            self.entryOpDerivacaoHidrograma.delete(0, END)
            
            #   Desabilite os demais
            self.entryOpDerivacaoPorcentagem.configure(state="disabled")
            self.entryOpDerivacaoHidrograma.configure(state="disabled")
        
        #   Caso clicou no porcentagem
        elif escolha == 2:
            #   Habilite o porcentagem
            self.entryOpDerivacaoPorcentagem.configure(state="normal")
            
            #   Delete o que estiver escrito nos demais
            self.entryOpDerivacaoConstante.delete(0, END)
            self.entryOpDerivacaoHidrograma.delete(0, END)
            
            #   Desabilite os demais
            self.entryOpDerivacaoConstante.configure(state="disabled")
            self.entryOpDerivacaoHidrograma.configure(state="disabled")
            
        #   Caso clicou no hidrograma
        else:
            #   Habilite o hidrograma
            self.entryOpDerivacaoHidrograma.configure(state="normal")
            
            #   Delete o que estiver escrito nos demais
            self.entryOpDerivacaoConstante.delete(0, END)
            self.entryOpDerivacaoPorcentagem.delete(0, END)
            
            #   Desabilite os demais
            self.entryOpDerivacaoConstante.configure(state="disabled")
            self.entryOpDerivacaoPorcentagem.configure(state="disabled")
    #-----------------------------------------------------------------------
    def inserirDerivacao(self):
        """"""
        #   Sumir com a janela antiga
        self.destroy()
        
        #   Criar janela nova
        Toplevel.__init__(self, bg="#DFF9CA")
        
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Inserir Derivação" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaSecundaria(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaSecundaria(i))
        
        #   Criar o frame
        segundoFrame = Frame(self, bg="#DFF9CA")
        segundoFrame.pack(padx = 10, pady = 10)
        
        #   TITULO:
        Label(segundoFrame, text= "INSERIR DERIVAÇÃO", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 5)
        
        #   Label local
        Label(segundoFrame, text= "Nome/local da operação:", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        #   Caixa de dialogo para entrar local
        self.entryNomeOperacao = Entry(segundoFrame, width = 16)
        self.entryNomeOperacao.grid(row = 1, column = 1, columnspan = 3, sticky = "w", padx = 0, pady = 0)
        
        #   Label hidrograma
        Label(segundoFrame, text= "Número da operação hidrológica de entrada:", bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        #   Register
        HidroEntrada = self.register(self.validarIntSemZero)
        #   Caixa de dialogo para entrar hidrograma
        self.entryHidroEntrada = Entry(segundoFrame, validate="key", width = 16, validatecommand=(HidroEntrada, "%P"))
        self.entryHidroEntrada.grid(row = 2, column = 1, columnspan = 3, sticky = "w", padx = 0, pady = 0)
        
        #-------------------
        #   Primeira groupbox
        derivGroup = LabelFrame(segundoFrame, text="Tipo de derivação", bg="#DFF9CA")
        derivGroup.grid(row = 3, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 3, ipady=0)
        
        Label(derivGroup, text= "", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "e", padx = 0, pady = 0, ipadx=168)
        
        #   cria a variavel que controla os botoes
        self.tipoDerivacao = IntVar()
        self.tipoDerivacao.set(1)
        
        #   Checkbuttons
        Checkbutton(derivGroup, text = "Valor de vazão constante"     , bg="#DFF9CA", activebackground="#DFF9CA", variable = self.tipoDerivacao, onvalue = 1, offvalue = 1, command=lambda: self.SelecionaTipoDerivacao(1)).grid(row = 0, column = 0, columnspan = 2, sticky = "w", padx = 0, pady = 2)
        Checkbutton(derivGroup, text = "Porcentagem de cada intervalo", bg="#DFF9CA", activebackground="#DFF9CA", variable = self.tipoDerivacao, onvalue = 2, offvalue = 2, command=lambda: self.SelecionaTipoDerivacao(2)).grid(row = 1, column = 0, columnspan = 2, sticky = "w", padx = 0, pady = 0)
        Checkbutton(derivGroup, text = "Hidrograma de uma operação"   , bg="#DFF9CA", activebackground="#DFF9CA", variable = self.tipoDerivacao, onvalue = 3, offvalue = 3, command=lambda: self.SelecionaTipoDerivacao(3)).grid(row = 2, column = 0, columnspan = 2, sticky = "w", padx = 0, pady = 2)
        
        #   Labels
        Label(derivGroup,text= ">0 (m³/s):"               , bg="#DFF9CA").grid(row = 0, column = 2, columnspan = 1, sticky = "e", padx = 0, pady = 2)
        Label(derivGroup,text= ">0~100 (%):"              , bg="#DFF9CA").grid(row = 1, column = 2, columnspan = 1, sticky = "e", padx = 0, pady = 0)
        Label(derivGroup,text= "1~%d (-):"%(self.n_max_op), bg="#DFF9CA").grid(row = 2, column = 2, columnspan = 1, sticky = "e", padx = 0, pady = 2)
        
        #   Registers
        valorConstante       = self.register(self.validarFloat)
        porcentagemIntervalo = self.register(self.validarFloatAteCem)
        numeroHidrograma     = self.register(self.validarIntSemZero)
        
        #   Entries
        self.entryOpDerivacaoConstante   = Entry(derivGroup, validate="key", width=10, validatecommand=(valorConstante, "%P"))
        self.entryOpDerivacaoPorcentagem = Entry(derivGroup, validate="key", width=10, validatecommand=(porcentagemIntervalo, "%P"))
        self.entryOpDerivacaoHidrograma  = Entry(derivGroup, validate="key", width=10, validatecommand=(numeroHidrograma, "%P"))
        
        #   Grids
        self.entryOpDerivacaoConstante  .grid(row = 0, column = 3, columnspan = 1, sticky = "e", padx = 5, pady = 2)
        self.entryOpDerivacaoPorcentagem.grid(row = 1, column = 3, columnspan = 1, sticky = "e", padx = 5, pady = 0)
        self.entryOpDerivacaoHidrograma .grid(row = 2, column = 3, columnspan = 1, sticky = "e", padx = 5, pady = 2)
        
        #   Desabilitar as demais entries
        self.entryOpDerivacaoPorcentagem.configure(state="disabled")
        self.entryOpDerivacaoHidrograma.configure(state="disabled")
        #-------------------
        #   Segunda groupbox
        outputGroup = LabelFrame(segundoFrame, text="Saída da operação", bg="#DFF9CA")
        outputGroup.grid(row = 4, column = 0, columnspan = 4, sticky = "n", padx = 5, pady = 3)
        
        Label(outputGroup, text= "", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "e", padx = 0, pady = 0, ipadx=168)
        
        #   cria a variavel que controla os botoes
        self.tipoSaidaDerivacao = IntVar()
        self.tipoSaidaDerivacao.set(1)
        
        #   Checkbuttons
        Checkbutton(outputGroup, text = "Hidrograma remanescente no curso principal", bg="#DFF9CA", activebackground="#DFF9CA", variable = self.tipoSaidaDerivacao, onvalue = 1, offvalue = 1).grid(row = 0, column = 0, columnspan = 4, sticky = "w", padx = 0, pady = 0)
        Checkbutton(outputGroup, text = "Hidrograma derivado"                       , bg="#DFF9CA", activebackground="#DFF9CA", variable = self.tipoSaidaDerivacao, onvalue = 2, offvalue = 2).grid(row = 1, column = 0, columnspan = 4, sticky = "w", padx = 0, pady = 2)
        #-------------------
        
        #   botao proximo
        Button(segundoFrame, text = "Próximo", width=9, command=lambda: self.manipularDerivacao()).grid(row = 5, column = 3, columnspan = 1, sticky = "e", padx = 5, pady = 3)
        #   botao sair
        Button(segundoFrame, text = "Voltar", width=9, command=lambda: self.fecharJanelaSecundaria(0)).grid(row = 5, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3)
        
        #   Centralizar o programa na tela
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def criarArquivo(self):
        """"""
        #   Criar a pasta para salvar arquivo de entrada
        criarPasta(self.diretorio_do_software + "/Entrada".encode())
        
        #   Verificar se o arquivo existe
        if (path.isfile(self.diretorio_do_software + "/Entrada/Arquivo_entrada".encode()) == True):
            #   Delete o arquivo antigo
            deletarArquivoAntigo((self.diretorio_do_software + "/Entrada".encode()), "Arquivo_entrada".encode(), "hyd".encode())
        
        #   Escrever um novo
        escreverArquivoEntrada(self.diretorio_do_software, self.strings_entrada)
        
        #   Avise o usuario para checar o diretorio do modelo
        mensagensInterfaces(5, "")

#-----------------------------------------------------------------------
class InterfacePlotagens(Toplevel):
    """Classe responsavel por exibir a janela de plotagens do modelo."""
    #-----------------------------------------------------------------------
    def __init__(self, master, versao_do_software, diretorio_do_software):
        #   Sumir com a janelinha, não gosto dela
        master.withdraw()
        
        #   Facilite minha vida
        self.master = master
        self.versao_do_software = versao_do_software
        self.diretorio_do_software = diretorio_do_software
        
        #   Mudar todos os icones
        icone = ImageTk.PhotoImage(Image.open(self.diretorio_do_software + "/lib/icone.png".encode()))
        self.master.wm_iconphoto(True, icone)
        
        #   Rodar interface
        self.janelaInterfacePlotagens()
    #-----------------------------------------------------------------------
    def janelaInterfacePlotagens(self):
        #   Cria a janela
        Toplevel.__init__(self, bg="#DFF9CA")
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Plotagens" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaPlotagem(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaPlotagem(i))
        #   Introduzir o frame
        primeiroFrame = Frame(self, bg="#DFF9CA")
        primeiroFrame.pack(padx = 10, pady = 10)
        
        #   TITULO:
        Label(primeiroFrame, text= "PLOTAGENS", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 4, sticky = "n", padx = 15, pady = 5 )
    
        #   Label resolucao
        Label(primeiroFrame, text= "Resolução da(s) imagem(ns):", bg="#DFF9CA").grid(row = 1, column = 0, columnspan = 2, sticky = "e", padx = 0, pady = 3 )
        
        #   Variavel do menu
        self.textoResolucao = StringVar()
        self.textoResolucao.set("640x480")
        #   Criar menubutton
        self.menuButtonResolucao = Menubutton(primeiroFrame, width=10, relief=RAISED, textvariable=self.textoResolucao)
        self.menuButtonResolucao.grid(row = 1, column = 2, columnspan = 2, sticky = "e", padx = 10, pady = 3, ipadx = 25)
        self.menuButtonResolucao.menu = Menu(self.menuButtonResolucao, tearoff = 0)
        self.menuButtonResolucao["menu"] = self.menuButtonResolucao.menu
        #   Adicionar os comandos
        self.menuButtonResolucao.menu.add_command(label="     640x480      ", command=lambda:self.textoResolucao.set("640x480"))
        self.menuButtonResolucao.menu.add_command(label="     800x600      ", command=lambda:self.textoResolucao.set("800x600"))
        self.menuButtonResolucao.menu.add_command(label="    1024x768      ", command=lambda:self.textoResolucao.set("1024x768"))
        self.menuButtonResolucao.menu.add_command(label="    1280x800      ", command=lambda:self.textoResolucao.set("1280x800"))
        self.menuButtonResolucao.menu.add_command(label="    1600x900      ", command=lambda:self.textoResolucao.set("1600x900"))
        
        #   Cria a variavel que controla os botoes
        self.isFolderPlot = IntVar()
        self.isFolderPlot.set(0)
        
        #   Botao procurar arquivo
        Checkbutton(primeiroFrame, text = "Procurar arquivo:", bg="#DFF9CA", activebackground="#DFF9CA", variable = self.isFolderPlot, onvalue = 0, offvalue = 0, command=lambda: self.habilitaButtonPlotarArquivo()).grid(row = 2, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 0)#, ipadx=22)
        self.buttonPlotarArquivo = Button(primeiroFrame, text = "Procurar", width=10, fg="#000000", command=lambda: self.executarPlotagem())
        self.buttonPlotarArquivo.grid(row = 2, column = 2, columnspan = 2, sticky = "e", padx = 10, pady = 0, ipadx = 21)
        
        #   Botao procurar pasta
        Checkbutton(primeiroFrame, text = "Procurar pasta:", bg="#DFF9CA", activebackground="#DFF9CA", variable = self.isFolderPlot, onvalue = 1, offvalue = 1, command=lambda: self.habilitaButtonPlotarPasta()).grid(row = 3, column = 0, columnspan = 2, sticky = "w", padx = 5, pady = 3)#, ipadx=22)
        self.buttonPlotarPasta = Button(primeiroFrame, text = "Procurar", width=10, fg="#A9A9A9", command=lambda: self.disableButton())
        self.buttonPlotarPasta.grid(row = 3, column = 2, columnspan = 2, sticky = "e", padx = 10, pady = 3, ipadx = 21)
        
        #   Botoes finais
        Button(primeiroFrame, text = "Voltar", width = 15, fg="#000000", command=lambda: self.fecharJanelaPlotagem(0)).grid(row = 4, column = 0, columnspan = 2, sticky = "w", padx = 10, pady = 5)
        
        #   Centralizar a janela do programa no monitor
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def habilitaButtonPlotarArquivo(self):
        """"""
        #   Desabilite o botao de pasta
        self.buttonPlotarPasta.configure(fg="#A9A9A9", command=lambda: self.disableButton())
        #   Habilite o botao de pasta
        self.buttonPlotarArquivo.configure(fg="#000000", command=lambda: self.executarPlotagem())
    #-----------------------------------------------------------------------
    def habilitaButtonPlotarPasta(self):
        """"""
        #   Desabilite o botao de arquivos
        self.buttonPlotarArquivo.configure(fg="#A9A9A9", command=lambda: self.disableButton())
        #   Habilite o botao de pasta
        self.buttonPlotarPasta.configure(fg="#000000", command=lambda: self.executarPlotagem())
    #-----------------------------------------------------------------------    
    def disableButton(self):
        """E' assim mesmo, ela nao faz nada... e' para desabilitar um botao."""
        pass
    #-----------------------------------------------------------------------        
    def fecharJanelaPlotagem(self, evento):
        #   Fechar a janela
        self.destroy()
        
        #   Reinicio a janela principal
        InterfacePrincipal(self.master, self.versao_do_software, self.diretorio_do_software)
    #-----------------------------------------------------------------------
    def executarPlotagem(self):
        """Chama as funcoes da logica das plotagens."""
        #   Esconder a janelinha, afinal ela fica congelada mesmo.
        self.withdraw()
        
        #   Trabalhar a resolucao antes de enviar
        resolucao = [int(self.textoResolucao.get().split("x")[0]), int(self.textoResolucao.get().split("x")[1])]
        
        #   Rodar as funcoes de calculo das operacoes
        iniciarGraficos(self.isFolderPlot.get(), self.diretorio_do_software, resolucao)
        
        #   Atualizar a interface
        self.update()
        #   Mostrar interface
        self.deiconify()

#-----------------------------------------------------------------------
class InterfaceSobre(Toplevel):
    """Classe responsavel por exibir a janela de informacoes do modelo."""
    info_gerais = ""
    aux = "->     Este é um software acadêmico gratuito e de código aberto.\n\n"; info_gerais += aux
    aux = "->     Este modelo pode ser usado livremente em trabalhos acadêmicos e profissionais desde que devidamente citado.\n\n"; info_gerais += aux
    aux = "->     Recomenda-se criticidade na análise dos resultados, pois os desenvolvedores deste programa não se responsabilizam por quaisquer consequências oriundas de erros de qualquer natureza.\n\n"; info_gerais += aux
    aux = "->     Não hesite em reportar bugs aos desenvolvedores.\n\n"; info_gerais += aux
    aux = "Desenvolvedores:\n"; info_gerais += aux
    aux = "     Vitor Gustavo Geller - vitorgg_hz@hotmail.com\n"; info_gerais += aux
    aux = "     Lucas Camargo da Silva Tassinari - lucascstassinari@gmail.com\n"; info_gerais += aux
    aux = "     Daniel Gustavo Allasia P. - dallasia@gmail.com\n"; info_gerais += aux
    aux = "     Rutinéia Tassi - rutineia@gmail.com\n\n"; info_gerais += aux
    aux = "Citar como: Geller, V.G.; Tassinari, L.C.S.; Allasia, D.G.; Tassi, R., Modelo Hidrológico Ecotecnologias, versão 1.10, Santa Maria/RS.\n\n"; info_gerais += aux
    aux = "Boas simulações!"; info_gerais += aux
    #-----------------------------------------------------------------------
    def __init__(self, master, versao_do_software, diretorio_do_software):
        #   Sumir com a janelinha, não gosto dela
        master.withdraw()
        
        #   Facilite minha vida
        self.master = master
        self.versao_do_software = versao_do_software
        self.diretorio_do_software = diretorio_do_software
        
        #   Mudar todos os icones
        icone = ImageTk.PhotoImage(Image.open(self.diretorio_do_software + "/lib/icone.png".encode()))
        self.master.wm_iconphoto(True, icone)
        
        #   Rodar interface
        self.janelaInterfaceInformacoes()
    #-----------------------------------------------------------------------
    def janelaInterfaceInformacoes(self):
        #   Cria a janela
        Toplevel.__init__(self, bg="#DFF9CA")
        #   Configurar a janela
        self.resizable(width=False, height=False)
        self.title("MHE - Sobre" )
        self.protocol("WM_DELETE_WINDOW", lambda: self.fecharJanelaAbout(0))
        self.bind("<Escape>", lambda i: self.fecharJanelaAbout(i))
        #   Introduzir o frame
        primeiroFrame = Frame(self, bg="#DFF9CA")
        primeiroFrame.pack(padx = 10, pady = 10)
        
        #   Titulo
        Label(primeiroFrame, text = "Modelo Hidrológico Ecotecnologias", bg="#DFF9CA").grid(row = 0, column = 0, columnspan = 2, sticky = "n", padx = 10, pady = 5)

        #   Text Box
        cxTextoInfo = scrolledtext.ScrolledText(primeiroFrame, height = 0, width = 0, wrap=WORD)
        #   Posicionar
        cxTextoInfo.grid(row = 1, column = 0, columnspan = 2, rowspan = 1, sticky = "n", padx = 15, pady = 0, ipadx=300, ipady=140)
        
        #   Quero editar
        cxTextoInfo.insert(END, self.info_gerais)
        cxTextoInfo.configure(state="disabled")
        cxTextoInfo.focus()
        
        Label(primeiroFrame, text = "06 de julho de 2022.", bg="#DFF9CA").grid(row = 2, column = 0, columnspan = 2, sticky = "w", padx = 10, pady = 5)
        Button(primeiroFrame, text = "Fechar", width = 10, command=lambda: self.fecharJanelaAbout(0)).grid(row = 2, column = 1, columnspan = 1, sticky = "e", padx = 15, pady = 5)
        
        #   Centralizar a janela do programa no monitor
        centralizarJanela(self)
    #-----------------------------------------------------------------------
    def fecharJanelaAbout(self, evento):
        #   Fechar a janela
        self.destroy()
        
        #   Reinicio a janela principal
        InterfacePrincipal(self.master, self.versao_do_software, self.diretorio_do_software)
    #-----------------------------------------------------------------------