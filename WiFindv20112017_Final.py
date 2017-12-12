#! /usr/bin/env python
# encoding: utf-8
#
## Importar ferramentas do sistema
import sys # Biblioteca importada para determinar o tipo de sistema no qual este programa esta sendo executado
import os # Biblioteca importada para executar comandos do shell do linux dentro do python

## Importar bibliotecas para o grafico tempo real
import matplotlib # Biblioteca usada para gerar graficos do estilo do matlab
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import style
style.use('ggplot')
import matplotlib.animation as animation

## Bibliotecas de apoio
import time, calendar
import datetime # Biblioteca para executar comandos que envolvam tempo
from PIL import ImageTk # Bibioteca para trabalhar com imagens

## Bibliotacas para gerar PDF
import Gnuplot
import numpy

from threading import Thread as th

## Bibiotecas do Tkinter para interface grafica
import Tkinter as tk

## Themed Tkinter
import ttk

def inicia_interf_grafica():
    root = tk.Tk()
    img = tk.PhotoImage(file = r'./lupafi.gif')
    root.call('wm', 'iconphoto', root._w, img)
    obj_principal = WiFind (root)
    root.protocol('WM_DELETE_WINDOW', obj_principal.destroi_janela)
    root.mainloop()

# Classe Principal
class WiFind:
    def __init__(self, top=None):
        self.top = top
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#d9d9d9' # X11 color: 'gray85'
        font10 = "-family {URW Gothic L} -size 10 -weight normal "  \
            "-slant italic -underline 0 -overstrike 0"
        font11 = "-family {URW Gothic L} -size 12 -weight bold "  \
            "-slant italic -underline 0 -overstrike 0"
        font9 = "-family FreeMono -size 24 -weight bold -slant roman "  \
            "-underline 0 -overstrike 0"

        #Definicao das cores dos canais que serão mostrados no gráfico. Faremos definicoes somente para os 3 canais principais: 1, 6 e 11
        #Canal 1 - Azul
        Azul1='#191970'
        #Canal 6 - Verde
        Verde1='#b22228'
        #Canal 11 - Vermelho
        Vermelho1='#800000'
        #Outros canais - Preto

        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        ###################################################

        # Configuracoes da janela top level

        self.largura_tela = self.top.winfo_screenwidth() # pega o valor da largura da tela
        self.altura_tela = self.top.winfo_screenheight() # pega o valor da altura da tela
        self.top.geometry('%sx%s' % (self.largura_tela, self.altura_tela)) # define o tamanho da janela toplevel para o tamanho maximo da tela do computador

        self.top.title("WiFind") # titulo da janela top level

        # Configuracoes do menu superior da janela principal

        self.menubar = tk.Menu(self.top,font="TkMenuFont",bg=_bgcolor,fg=_fgcolor)
        self.top.configure(menu = self.menubar)

        self.opcoes = tk.Menu(self.top,tearoff=0)
        self.menubar.add_cascade(menu=self.opcoes,
                activebackground="#d9d9d9",
                activeforeground="#000000",
                background="#d9d9d9",
                font="TkMenuFont",
                foreground="#000000",
                label="Opções")
        self.opcoes.add_command(
                activebackground="#d8d8d8",
                activeforeground="#000000",
                background="#d9d9d9",
                font="TkMenuFont",
                foreground="#000000",
                label="Gerar Relatório em PDF",
                command=self.gerarPDF)
        self.ajuda = tk.Menu(self.top,tearoff=0)
        self.menubar.add_cascade(menu=self.ajuda,
                activebackground="#d9d9d9",
                activeforeground="#000000",
                background="#d9d9d9",
                font="TkMenuFont",
                foreground="#000000",
                label="Ajuda")
        self.ajuda.add_command(
                activebackground="#d8d8d8",
                activeforeground="#000000",
                background="#d9d9d9",
                font="TkMenuFont",
                foreground="#000000",
                label="Sobre",
                command = self.abre_sobre)
        self.ajuda.add_command(
                activebackground="#d8d8d8",
                activeforeground="#000000",
                background="#d9d9d9",
                #command=teste_tela4_support,
                font="TkMenuFont",
                foreground="#000000",
                label="Como Usar",
                command=self.abre_comousar)

        #############################################################

        # Configuracoes do container onde serao colocadas as abas que mostrarao os graficos
        # O container eh uma TNotebook.Tab e vamos chama-lo aqui de Container_Abas

        ###
        # Define o estilo do Container_Abas
        self.style.configure('TNotebook.Tab', background=_bgcolor)
        self.style.configure('TNotebook.Tab', foreground=_fgcolor)
        self.style.map('TNotebook.Tab', background=
            [('selected', _compcolor), ('active',_ana2color)])
        ###

        ###
        # Criacao do Container_Abas
        self.Container_Abas = ttk.Notebook(self.top) # Criado como um Notebook. Como podemos ver, esse widget Notebook nao e padrao do Tkinter. Ele eh importado de uma biblioteca chamada ttk
        self.Container_Abas.place(relx=0.2, rely=0.0, relheight=1.0, relwidth=0.8) # Algumas propriedades graficas: relx nos diz a posicao horizontal na qual o container sera colocado em relacao ao seu mestre, no caso, top. As outras configuracoes sao intuitivas
        self.Container_Abas.configure(takefocus="")
        ###

        #############################################################
        # Vamos agora alterar as configuracoes dos frames que serao criados para mostrar o conteudo de cada aba. As abas sao duas: Aba_SSID e Aba_Geral

        # Vamos comecar pela Aba_SSID e definiremos todas as configuracoes e widgets dentro dele

        self.Aba_SSID = tk.Frame(self.Container_Abas) # Criacao do Frame
        self.Aba_SSID.configure(background = "#666666") # Definicao do plano de fundo cinza
        self.Container_Abas.add(self.Aba_SSID, padding=3) # Adicionando ele como aba do Container_Abas
        self.Container_Abas.tab(0, text="Scan por SSID",underline="-1",) # Definindo o nome que aparecera no topo da aba para selecao

        # Criacao do canvas onde sera mostrado o grafico
        # Utilizamos a biblioteca do matplotlib para mostrar um grafico que sera atualizado em tempo real.
        # Primeiro criamos uma figura onde o grafico sera mostrado

        self.Figura_SSID = Figure(figsize=(10,8), dpi=100) # criacao da figura e suas caracteristicas
        self.Grafico_SSID = self.Figura_SSID.add_subplot(111) # adicao do grafico em forma de subplot. Todos os metodos sao diferentes e podem ser acessados no link: https://matplotlib.org/api/axes_api.html



        # Criacao do Canvas_SSID, onde sera colocada a figura do grafico
        self.Canvas_SSID = FigureCanvasTkAgg(self.Figura_SSID, self.Aba_SSID)
        self.Canvas_SSID.show()
        self.Canvas_SSIDMAT = self.Canvas_SSID.get_tk_widget()
        self.Canvas_SSIDMAT.place(relx=0.05, rely=0.1, relheight=0.85, relwidth=0.9)
        self.Canvas_SSIDMAT.configure(background="white")
        self.Canvas_SSIDMAT.configure(borderwidth="2")
        self.Canvas_SSIDMAT.configure(relief=tk.RIDGE)
        self.Canvas_SSIDMAT.configure(selectbackground="#c4c4c4")
        self.Canvas_SSIDMAT.configure(takefocus="0")
        self.Canvas_SSIDMAT.configure(width=744)
        self.decisao_ssid = 0
        self.ani_ssid = animation.FuncAnimation(self.Figura_SSID,self.animate_ssid,interval=500)

        #############################################################

        self.DICSSIDs = {}
        self.executathread = True
        self.threadalimenta = th(target=self.alimentalista)
        self.threadalimenta.start()

        ### Script que gera o dropdown lsit com os tSSIDs encontrados
        # Tambem armazena na variavel self.variable qual o valor escolhido na lista

        self.variable = tk.StringVar(self.top)
        self.variable.set('-') # default value
        self.dropdownSSID = ttk.Combobox(self.Aba_SSID, textvariable=self.variable, state="readonly", values=self.DICSSIDs.keys())
        self.dropdownSSID.place(relx=0.1, rely=0.05, relheight=0.04, relwidth=0.3)

        ######################################################

        # Label (Texto) indicando para o usuario escolher o SSID
        self.Label_EscolherSSID = tk.Label(self.Aba_SSID)
        self.Label_EscolherSSID.place(relx=0.1, rely=0.008, relheight=0.04, relwidth=0.3)
        self.Label_EscolherSSID.configure(activebackground="#666666")
        self.Label_EscolherSSID.configure(background="#666666")
        self.Label_EscolherSSID.configure(foreground="white")
        self.Label_EscolherSSID.configure(text='''Escolha o SSID:''')

        # Botao Plotar na aba Scan por SSID
        self.Imagem_BotaoSSID = ImageTk.PhotoImage(file="./button_plotar.ico") # imagem do botao Plotar
        self.Button_PlotarSSID = tk.Button(self.Aba_SSID, image=self.Imagem_BotaoSSID, justify=tk.LEFT,
        command = lambda
        arg1 = "Button_PlotarSSID", arg2 = 1, arg3 = "Opcao por SSID escolhida!" :
        self.buttonHandler(arg1, arg2, arg3)) # Faz a imagem aparecer no lugar do botao Plotar. No caso, o botao eh a propria imagem
        self.Button_PlotarSSID.place(relx=0.4, rely=0.03, relwidth=0.2)
        # Para fazer com que soh a imgagem seja vista, precisamos colocar o botao com borda nula, e cor de fundo igual a cor de fundo do container onde ele esta
        self.Button_PlotarSSID.configure(activebackground="#666666")
        self.Button_PlotarSSID.configure(background="#666666")
        self.Button_PlotarSSID.configure(disabledforeground="#666666")
        self.Button_PlotarSSID.configure(highlightbackground="#666666")
        self.Button_PlotarSSID.configure(bd=0)

        ###
        # Agora Aba_Geral
        self.Aba_Geral = tk.Frame(self.Container_Abas,background="#666666",)
        self.Container_Abas.add(self.Aba_Geral, padding=3)
        self.Container_Abas.tab(1, text="Scan Geral",underline="-1",)

        self.Figura_Geral = Figure(figsize=(10,8), dpi=100) # criacao da figura e suas caracteristicas
        self.Grafico_Geral = self.Figura_Geral.add_subplot(111) # adicao do grafico

        # Criacao do Canvas_Geral, onde sera colocada a figura do grafico
        self.Canvas_Geral = FigureCanvasTkAgg(self.Figura_Geral, self.Aba_Geral)
        self.Canvas_Geral.show()
        self.Canvas_GeralMAT = self.Canvas_Geral.get_tk_widget()
        self.Canvas_GeralMAT.place(relx=0.05, rely=0.1, relheight=0.85, relwidth=0.9)
        self.Canvas_GeralMAT.configure(background="white")
        self.Canvas_GeralMAT.configure(borderwidth="2")
        self.Canvas_GeralMAT.configure(relief=tk.RIDGE)
        self.Canvas_GeralMAT.configure(selectbackground="#c4c4c4")
        self.Canvas_GeralMAT.configure(takefocus="0")
        self.Canvas_GeralMAT.configure(width=744)
        self.decisao_geral = 0
        self.ani_geral = animation.FuncAnimation(self.Figura_Geral,self.animate_geral,interval=500)

        # Botao Plotar na aba Scan GEral
        self.Imagem_BotaoGeral = ImageTk.PhotoImage(file="./button_plotar.ico") # imagem do botao Plotar
        self.Button_PlotarGeral = tk.Button(self.Aba_Geral, image=self.Imagem_BotaoGeral, justify=tk.LEFT,
        command = lambda
        arg1= "Button_PlotarGeral", arg2 = 1, arg3 = "Opcao Todos os SSIDs escolhida!" :
        self.buttonHandler(arg1, arg2, arg3)) # Faz a imagem aparecer no lugar do botao Plotar. No caso, o botao eh a propria imagem
        self.Button_PlotarGeral.place(relx=0.4, rely=0.03, relwidth=0.2)
        # Para fazer com que soh a imgagem seja vista, precisamos colocar o botao com borda nula, e cor de fundo igual a cor de fundo do container onde ele estah
        self.Button_PlotarGeral.configure(activebackground="#666666")
        self.Button_PlotarGeral.configure(background="#666666")
        self.Button_PlotarGeral.configure(disabledforeground="#666666")
        self.Button_PlotarGeral.configure(highlightbackground="#666666")
        self.Button_PlotarGeral.configure(bd=0)

        ###
        # Criacao do Frame onde vamos colocar o titulo e os autores

        self.Frame_Titulo = tk.Frame(self.top) # criando frame
        self.Frame_Titulo.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=0.2) # dimensoes
        self.Frame_Titulo.configure(relief=tk.GROOVE)
        self.Frame_Titulo.configure(borderwidth="2")
        self.Frame_Titulo.configure(background="#ffbd4a")

        # Craicao do label do titulo do software
        self.Label_TituloSoftware = tk.Label(self.Frame_Titulo)
        self.Label_TituloSoftware.place(relx=0.0, rely=0.0, relheight=0.1, relwidth=1)
        self.Label_TituloSoftware.configure(activebackground="#c84351")
        self.Label_TituloSoftware.configure(activeforeground="white")
        self.Label_TituloSoftware.configure(background="#ffbd4a")
        self.Label_TituloSoftware.configure(foreground="white")
        self.Label_TituloSoftware.configure(font=font9)
        self.Label_TituloSoftware.configure(text='''WiFind''')

        # Criacao do label dos autores do software
        self.Label_Autores = tk.Label(self.Frame_Titulo)
        self.Label_Autores.place(relx=0.0, rely=0.9, relheight=0.1, relwidth=1)
        self.Label_Autores.configure(activebackground="#c84351")
        self.Label_Autores.configure(activeforeground="white")
        self.Label_Autores.configure(background="#ffbd4a")
        self.Label_Autores.configure(foreground="black")
        self.Label_Autores.configure(font=font10)
        self.Label_Autores.configure(text='''Por Bruno Pacheco e Gentil Gomes''')

        #Frames e Labels dos canais
        # Craicao do label do titulo dos Canais
        self.Label_Descricao = tk.Label(self.Frame_Titulo)
        self.Label_Descricao.place(relx=0.1, rely=0.64, relheight=0.04, relwidth=0.8)
        self.Label_Descricao.configure(activebackground="#c84351")
        self.Label_Descricao.configure(activeforeground="black")
        self.Label_Descricao.configure(background="#ffbd4a")
        self.Label_Descricao.configure(foreground="black")
        self.Label_Descricao.configure(font=font11)
        self.Label_Descricao.configure(text='''Legenda de Canais''')

        self.Frame_Canal1 = tk.Frame(self.Frame_Titulo)
        self.Frame_Canal1.place(relx=0.04, rely=0.70, relheight=0.04, relwidth=0.1)
        self.Frame_Canal1.configure(relief=tk.RAISED)
        self.Frame_Canal1.configure(borderwidth="2")
        self.Frame_Canal1.configure(relief=tk.RAISED)
        self.Frame_Canal1.configure(background="red")
        self.Frame_Canal1.configure(width=45)

        self.Label_Canal1 = tk.Label(self.Frame_Titulo)
        self.Label_Canal1.place(relx=0.14, rely=0.70, relheight=0.04, relwidth=0.3)
        self.Label_Canal1.configure(background="#ffbd4a")
        self.Label_Canal1.configure(foreground="black")
        self.Label_Canal1.configure(font=font10)
        self.Label_Canal1.configure(justify = tk.LEFT)
        self.Label_Canal1.configure(text='Canal 1')

        self.Frame_Canal6 = tk.Frame(self.Frame_Titulo)
        self.Frame_Canal6.place(relx=0.04, rely=0.76, relheight=0.04, relwidth=0.1)
        self.Frame_Canal6.configure(relief=tk.RAISED)
        self.Frame_Canal6.configure(borderwidth="2")
        self.Frame_Canal6.configure(relief=tk.RAISED)
        self.Frame_Canal6.configure(background="blue")
        self.Frame_Canal6.configure(width=45)

        self.Label_Canal6 = tk.Label(self.Frame_Titulo)
        self.Label_Canal6.place(relx=0.14, rely=0.76, relheight=0.04, relwidth=0.3)
        self.Label_Canal6.configure(background="#ffbd4a")
        self.Label_Canal6.configure(foreground="black")
        self.Label_Canal6.configure(font=font10)
        self.Label_Canal6.configure(justify = tk.LEFT)
        self.Label_Canal6.configure(text='Canal 6')

        self.Frame_Canal11 = tk.Frame(self.Frame_Titulo)

        self.Frame_Canal11.place(relx=0.04, rely=0.82, relheight=0.04, relwidth=0.1)
        self.Frame_Canal11.configure(relief=tk.RAISED)
        self.Frame_Canal11.configure(borderwidth="2")
        self.Frame_Canal11.configure(relief=tk.RAISED)
        self.Frame_Canal11.configure(background="green")
        self.Frame_Canal11.configure(width=45)

        self.Label_Canal11 = tk.Label(self.Frame_Titulo)

        self.Label_Canal11.place(relx=0.14, rely=0.82, relheight=0.04, relwidth=0.3)
        self.Label_Canal11.configure(background="#ffbd4a")
        self.Label_Canal11.configure(foreground="black")
        self.Label_Canal11.configure(font=font10)
        self.Label_Canal11.configure(justify = tk.LEFT)
        self.Label_Canal11.configure(text='Canal 11')

        self.Frame_OutrosCanais = tk.Frame(self.Frame_Titulo)


        self.Frame_OutrosCanais.place(relx=0.04, rely=0.88, relheight=0.04, relwidth=0.1)
        self.Frame_OutrosCanais.configure(relief=tk.RAISED)
        self.Frame_OutrosCanais.configure(borderwidth="2")
        self.Frame_OutrosCanais.configure(relief=tk.RAISED)
        self.Frame_OutrosCanais.configure(background="black")
        self.Frame_OutrosCanais.configure(width=45)

        self.Label_OutrosCanais = tk.Label(self.Frame_Titulo)

        self.Label_OutrosCanais.place(relx=0.14, rely=0.88, relheight=0.04, relwidth=0.4)
        self.Label_OutrosCanais.configure(background="#ffbd4a")
        self.Label_OutrosCanais.configure(foreground="black")
        self.Label_OutrosCanais.configure(justify = tk.LEFT)
        self.Label_OutrosCanais.configure(font=font10)
        self.Label_OutrosCanais.configure(text='Outros Canais')
        #############################################################

    def buttonHandler(self, argument1, argument2, argument3):
        # A funcao buttonHandler tem um objetivo: alimentar os eventos dos botoes apertados.
        # Ao apertar o botao "Plotar" em qualquer uma das abas ela eh acionada. A diferenca esta nos argumentos passados.

        if argument1 == "Button_PlotarGeral":
            self.decisao_geral = 1


        if argument1 == "Button_PlotarSSID":
            self.decisao_ssid = 1

    def alimentalista(self):
        while self.executathread:
            while 1: # Esse while eh usado para prevenir o problema que acontece quando o retorno do comando que captura os dados eh nulo
                self.saidaiwlist = os.popen('iwlist wlp3s0 scanning | grep -A 5 Address') # arquivo que armazena o retorno do comando.
                self.strsaidaiwlist = self.saidaiwlist.read() # variavel que le o arquivo de retorno do comando e armazena em uma string
                if len(self.strsaidaiwlist) != 0: # Se a string tem tamanho nulo, significa que o comando nao retornou nada, e o loop deve continuar. Se nao for nulo, o loop eh interrompido e o programa segue
                    break
                time.sleep(0.1)

            self.liststrsaidaiwlist = self.strsaidaiwlist.split('\n') # Faz um split dos dados separando a saida do comanto por linhas
            self.qtdecells = len(self.liststrsaidaiwlist)/7 # Cada celula tem informacoes em um conjunto de 7 linhas. Se dividirmos a quantidade de linhas por 7, temos a quantidade de celulas capturadas
            for self.k in range(1,self.qtdecells+1): # realiza um loop onde a quantidade de vezes que o loop eh executado eh a mesma que a quantidade de celulas encontradas. Todas as funcoes abaixo, portanto, serao execeutadas para cada celula (BSSID)
                self.stringcellatual = self.liststrsaidaiwlist[((self.k-1)*7):((self.k*7)-1)] # coloca toda a informacao do BSSID em uma lista de strings. Cada elemento da lista nos da uma informacao. Segue um exemplo: ['          Cell 01 - Address: EC:08:6B:FF:E2:54', '                    Channel:11', '                    Frequency:2.462 GHz (Channel 11)', '                    Quality=66/70  Signal level=-44 dBm  ', '                    Encryption key:on', '                    ESSID:"OpenWrt"']
                self.tamssidatual = len(self.stringcellatual[5]) # como o tamanho do SSID eh variavel, para que possamos pegar exatamente o numero de caracteres do SSID, precisamos do tamanho dele. Essa variavel nos da o tamanho do elemento da lista que contem o SSID, e nao o tamanho do SSID.

                self.ssidatual = self.stringcellatual[5][27:(self.tamssidatual-1)]; # Sabendo o tamanho do campo, podemos capturar somente o SSID. Sabemos que ele comeca no caractere 28 (27 e o indice dele). Pegamos do 28 ate o final da string
                self.bssidatual = self.stringcellatual[0][29:46] # captura o BSSID da celula em questao
                self.rssiatual = int(self.stringcellatual[3][48:51]) # captura o RSSI da celula em questao
                self.canalcellatual = self.stringcellatual[1][28:30]

                if not self.ssidatual in self.DICSSIDs:
                    self.DICSSIDs[self.ssidatual] = {}
                    # verifica se o ssid em questao nao existe na listassids. Se nao existir, cria o dicionario, coloca o ssid na lista, cria a lista dos BSSIDs desse SSID, cria a lista das medias da rssi dos BSSIDs e coloca seu SSID nee mesmo


                if not self.bssidatual in self.DICSSIDs[self.ssidatual]: # verfica se o BSSID atual nao pertence a lista de BSSIDs do atual SSID
                    # se nao pertence, coloca na lista
                    self.DICSSIDs[self.ssidatual][self.bssidatual] = {}
                    self.DICSSIDs[self.ssidatual][self.bssidatual]['canal'] = self.canalcellatual
                    self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'] = range(0,60)
                    self.DICSSIDs[self.ssidatual][self.bssidatual]['epoch'] = range(0,60)
                    self.DICSSIDs[self.ssidatual][self.bssidatual]['mediarssi'] = self.rssiatual
                    if self.DICSSIDs[self.ssidatual][self.bssidatual]['canal'] == "1":
                        self.DICSSIDs[self.ssidatual][self.bssidatual]['cor'] = 'red'
                    elif self.DICSSIDs[self.ssidatual][self.bssidatual]['canal'] == "6":
                        self.DICSSIDs[self.ssidatual][self.bssidatual]['cor'] = 'blue'
                    elif self.DICSSIDs[self.ssidatual][self.bssidatual]['canal'] == '11':
                        self.DICSSIDs[self.ssidatual][self.bssidatual]['cor'] = 'green'
                    else:
                        self.DICSSIDs[self.ssidatual][self.bssidatual]['cor'] = 'black'
                    for indice,valor in enumerate(self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi']):
                        self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'][indice] = None
                        self.DICSSIDs[self.ssidatual][self.bssidatual]['epoch'][indice] = None

                self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'].append(self.rssiatual)
                self.DICSSIDs[self.ssidatual][self.bssidatual]['epoch'].append(int(time.time()))

                self.DICSSIDs[self.ssidatual][self.bssidatual]['mediarssi'] =  float(sum(self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'][60:len(self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'])-1]) / (len(self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'])-60))

                self.DICSSIDs[self.ssidatual][self.bssidatual]['existe'] = 0
                for self.a in self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'][len(self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'])-10:len(self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'])]:
                    if self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'][len(self.DICSSIDs[self.ssidatual][self.bssidatual]['rssi'])-1] != self.a:
                        self.DICSSIDs[self.ssidatual][self.bssidatual]['existe'] = 1
                        break
        return



    def animate_ssid(self,i):
        self.dropdownSSID['values'] = self.DICSSIDs.keys()
        if self.decisao_ssid:
            self.Grafico_SSID.clear()
            self.horaatual = time.strftime("%H:%M:%S")
            self.horamenos15 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,15)
            self.horamenos30 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,30)
            self.horamenos45 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,45)
            self.horamenos60 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,60)

            for self.bssid in self.DICSSIDs[self.variable.get()].keys():
                if self.DICSSIDs[self.variable.get()][self.bssid]['existe'] == 0:
                    continue

                ## Rotina para nao plotar celulas(BSSIDs) que somem
                # Por padrao do software, quando um BSSID some, o programa repete o ultimo rssi por 13 vezes antes de parar de atualizar. Ess rotina testa isso e se os ultimos 10 rssi foram iguais, param o plotar a celula

                self.Grafico_SSID.plot(self.DICSSIDs[self.variable.get()][self.bssid]['rssi'][len(self.DICSSIDs[self.variable.get()][self.bssid]['rssi'])-60:len(self.DICSSIDs[self.variable.get()][self.bssid]['rssi'])], self.DICSSIDs[self.variable.get()][self.bssid]['cor'])

                self.Grafico_SSID.set_xticks([0, 15, 30, 45, 60])
                self.Grafico_SSID.text(57, self.DICSSIDs[self.variable.get()][self.bssid]['rssi'][len(self.DICSSIDs[self.variable.get()][self.bssid]['rssi'])-1], self.bssid, bbox=dict(facecolor=self.DICSSIDs[self.variable.get()][self.bssid]['cor'], alpha=0.5))
                self.Grafico_SSID.set_xticklabels([str(self.horamenos60.time()), str(self.horamenos45.time()), str(self.horamenos30.time()), str(self.horamenos15.time()), self.horaatual])

            self.Grafico_SSID.set_xlabel('Tempo')
            self.Grafico_SSID.set_ylabel('RSSI em dBm')
            self.Grafico_SSID.set_title('Grafico por SSID')

    def animate_geral(self,i): # Funcao que faz a extracao dos dados do comando iwlist
        if self.decisao_geral:
            self.Grafico_Geral.clear()
            self.horaatual = time.strftime("%H:%M:%S")
            self.horamenos15 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,15)
            self.horamenos30 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,30)
            self.horamenos45 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,45)
            self.horamenos60 = datetime.datetime.strptime(self.horaatual, '%H:%M:%S') - datetime.timedelta(0,60)

            for self.ssid in self.DICSSIDs.keys():
                self.bssidmaiormedia = None
                self.maiormedia = -150
                for self.bssid in self.DICSSIDs[self.ssid].keys():
                    if self.DICSSIDs[self.ssid][self.bssid]['mediarssi'] > self.maiormedia and self.DICSSIDs[self.ssid][self.bssid]['existe']==1:
                        self.bssidmaiormedia = self.bssid


                if self.bssidmaiormedia == None:
                    continue
                self.Grafico_Geral.plot(self.DICSSIDs[self.ssid][self.bssidmaiormedia]['rssi'][len(self.DICSSIDs[self.ssid][self.bssidmaiormedia]['rssi'])-60:len(self.DICSSIDs[self.ssid][self.bssidmaiormedia]['rssi'])],self.DICSSIDs[self.ssid][self.bssidmaiormedia]['cor'])
                self.Grafico_Geral.set_xticks([0, 15, 30, 45, 60])
                self.Grafico_Geral.text(59, self.DICSSIDs[self.ssid][self.bssidmaiormedia]['rssi'][len(self.DICSSIDs[self.ssid][self.bssidmaiormedia]['rssi'])-1], self.ssid+'\n'+self.bssidmaiormedia, bbox=dict(facecolor=self.DICSSIDs[self.ssid][self.bssidmaiormedia]['cor'], alpha=0.5))
                self.Grafico_Geral.set_xticklabels([str(self.horamenos60.time()), str(self.horamenos45.time()), str(self.horamenos30.time()), str(self.horamenos15.time()), self.horaatual])

            self.Grafico_Geral.set_xlabel('Tempo')
            self.Grafico_Geral.set_ylabel('RSSI em dBm')
            self.Grafico_Geral.set_title('Grafico Todos os SSIDs')

    def destroi_janela(self):
        self.executathread = False
        self.gerarPDF()
        self.top.destroy()

    def abre_sobre(self):
        self.janela_sobre = tk.Toplevel(self.top)
        font10 = "-family FreeMono -size 24 -weight bold -slant roman "  \
            "-underline 0 -overstrike 0"
        font9 = "-family FreeMono -size 12 -weight normal -slant roman"  \
            " -underline 0 -overstrike 0"
        self.janela_sobre.geometry("525x407+467+207")
        self.janela_sobre.title("Sobre WiFind")
        self.janela_sobre.configure(highlightcolor="black")

        self.Frame1 = tk.Frame(self.janela_sobre)
        self.Frame1.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=1.0)
        self.Frame1.configure(relief=tk.GROOVE)
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(background="#ffbd4a")
        self.Frame1.configure(width=125)

        self.Label1 = tk.Label(self.Frame1)
        self.Label1.place(relx=0.01, rely=0.05, height=41, width=515)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(background="#ffbd4a")
        self.Label1.configure(font=font10)
        self.Label1.configure(foreground="#ffffff")
        self.Label1.configure(text='''WiFind''')

        self.Label2 = tk.Label(self.Frame1)
        self.Label2.place(relx=0.0, rely=0.9, height=40, width=521)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(background="#ffbd4a")
        self.Label2.configure(font=font9)
        self.Label2.configure(text='''Criado por: Bruno Pacheco e Gentil Gomes''')

        self.Label4 = tk.Label(self.Frame1)
        self.Label4.place(relx=0.0, rely=0.15, height=41, width=521)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(background="#ffbd4a")
        self.Label4.configure(font=font9)
        self.Label4.configure(text='''Versão 1.0.0 - Dezembro de 2017''')

        self.Label3 = tk.Label(self.Frame1)
        self.Label3.place(relx=0.01, rely=0.28, height=203, width=515)
        self.Label3.configure(background="#ffbd4a")
        self.Label3.configure(font=font9)
        self.Label3.configure(text='''Este software foi criado para servir como ferramenta de análise de redes Wi-Fi na banda de 2,4 GHz. Com as funções de analisar as potências recebidas de todas as redes sem fio do ambiente e todos os pontos de acesso, o software pode, além de dimensionar novas redes Wi-Fi, indicar melhorias nas configurações atuais para um melhor desempenho da rede. Para facilitar esses estudos de ambientes, o software ainda é capaz de gerar um arquivo em PDF com os gráficos de potências recebidas que foram gerados dos diferentes pontos de acesso ao longo do tempo.''')
        self.Label3.configure(wraplength="470")
        self.janela_sobre.mainloop()

    def abre_comousar(self):
        self.janela_comousar = tk.Toplevel(self.top)
        font10 = "-family FreeMono -size 24 -weight bold -slant roman "  \
            "-underline 0 -overstrike 0"
        font9 = "-family FreeMono -size 12 -weight normal -slant roman"  \
            " -underline 0 -overstrike 0"
        self.janela_comousar.geometry("700x700+467+207")
        self.janela_comousar.title("Como Usar")
        self.janela_comousar.configure(highlightcolor="black")

        self.Frame1 = tk.Frame(self.janela_comousar)
        self.Frame1.place(relx=0.0, rely=0.0, relheight=1.0, relwidth=1.0)
        self.Frame1.configure(relief=tk.GROOVE)
        self.Frame1.configure(borderwidth="2")
        self.Frame1.configure(background="#ffbd4a")
        self.Frame1.configure(width=125)

        self.Label1 = tk.Label(self.Frame1)
        self.Label1.place(relx=0.01, rely=0.05, height=41, relwidth=0.98)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(background="#ffbd4a")
        self.Label1.configure(font=font10)
        self.Label1.configure(foreground="#ffffff")
        self.Label1.configure(text='''WiFind''')

        self.Label2 = tk.Label(self.Frame1)
        self.Label2.place(relx=0.0, rely=0.9, height=40, relwidth=0.98)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(background="#ffbd4a")
        self.Label2.configure(font=font9)
        self.Label2.configure(text='''Criado por: Bruno Pacheco e Gentil Gomes''')

        self.Label4 = tk.Label(self.Frame1)
        self.Label4.place(relx=0.0, rely=0.15, height=41, relwidth=0.98)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(background="#ffbd4a")
        self.Label4.configure(font=font9)
        self.Label4.configure(text='''Versão 1.0.0 - Dezembro de 2017''')

        self.Label3 = tk.Label(self.Frame1)
        self.Label3.place(relx=0.01, rely=0.28, relheight=0.5, relwidth=0.98)
        self.Label3.configure(background="#ffbd4a")
        self.Label3.configure(justify=tk.LEFT)
        self.Label3.configure(font=font9)
        self.Label3.configure(text='''Ao abrir o software, o mesmo já começa a realizar scans e guardar informações sobre o ambiente WiFi atual.\n\nNa aba Scan por SSID, você tem a opção de escolher um SSID detectado no seu ambiente e, ao pressionar o botão \"Plotar\", serão mostrados no gráfico abaixo, todos os BSSIDs que tem o SSID escolhido.\nO gráfico mostrará um intervalo de 1 minuto da RSSI dos BSSIDs do SSID escolhido.\n\nSelecionando a aba Scan Geral, serão mostrados todos os SSIDs detectados. O BSSID plotado é aquele que tem a maior média dos últimos 10 segundos.\n\nVocê também tém a opção de gerar um PDF, dividido por SSID, com o gráfico RSSI x Tempo de cada BSSID encontrado. Selecione Opções, depois Gerar Relatório em PDF.''')
        self.Label3.configure(wraplength="630")
        self.janela_comousar.mainloop()

    def gerarPDF(self):
        for self.ssidpdf in self.DICSSIDs.keys():
            self.g = Gnuplot.Gnuplot()
            self.g("set terminal pdf monochrome enhanced size 30cm,15cm")
            self.g("set output '/home/devbru_ubuntu/Dropbox/TCC/rssi_python/WiFindv20112017/"+self.ssidpdf+".pdf'")
            for self.bssidpdf in self.DICSSIDs[self.ssidpdf].keys():
                self.g.title('Dados do BSSID '+self.bssidpdf)
                self.g.xlabel("Epoch Time (H:M:S)")
                self.g.ylabel("RSSI em dBm")
                self.g("set grid")
                self.tempoinicio = self.DICSSIDs[self.ssidpdf][self.bssidpdf]['epoch'][61] - 5
                self.tempofim = self.DICSSIDs[self.ssidpdf][self.bssidpdf]['epoch'][len(self.DICSSIDs[self.ssidpdf][self.bssidpdf]['epoch']) -1] + 5
                self.g("set xdata time")
                self.g('set timefmt "%s"')
                self.g('set format x "%m/%d/%Y %H:%M:%S"')
                exec("self.g('set xrange [%s:%s]')" % (self.tempoinicio, self.tempofim)) in locals()
                self.g("set yrange [-90:-15]")
                self.g("set ytic 20")
                self.g("set xtics rotate by -45")
                self.g('set key noenhanced')

                self.yrssi = self.DICSSIDs[self.ssidpdf][self.bssidpdf]['rssi'][61:len(self.DICSSIDs[self.ssidpdf][self.bssidpdf]['rssi']) -1]

                self.xrssi = self.DICSSIDs[self.ssidpdf][self.bssidpdf]['epoch'][61:len(self.DICSSIDs[self.ssidpdf][self.bssidpdf]['epoch']) -1]

                self.dadosrssi = Gnuplot.Data(numpy.array(self.xrssi, dtype = numpy.float64), numpy.array(self.yrssi, dtype = numpy.float64), title="RSSI do BSSID: "+self.bssidpdf, with_="lines", using='1:2')
                self.g.plot(self.dadosrssi)
            del self.g
        return

if __name__ == '__main__':
    inicia_interf_grafica()
