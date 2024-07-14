import tkinter as tk
import random
from collections import deque
from tkinter import PhotoImage


class PlanoCartesianoApp:
    def __init__(self, master, largura, altura, tamanho_celula):
        self.master = master
        master.title("Plano Cartesiano")

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(fill=tk.X)

        self.canvas = tk.Canvas(master, width=largura, height=altura)
        self.canvas.pack()

        self.imagem_motoboy = tk.PhotoImage(file="./boy.gif")

        self.btn_motoboy = tk.Button(self.control_frame, text="Selecionar ponto inicial do motoboy", command=self.selecionar_motoboy)
        self.btn_motoboy.pack(side=tk.LEFT, padx=5)

        self.btn_entrega = tk.Button(self.control_frame, text="Selecionar pontos de entrega", command=self.selecionar_entregas)
        self.btn_entrega.pack(side=tk.LEFT, padx=5)

        self.btn_iniciar = tk.Button(self.control_frame, text="Iniciar entrega", command=self.iniciar_entrega)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        self.btn_iniciar['state'] = tk.DISABLED

        self.largura = largura
        self.altura = altura
        self.tamanho_celula = tamanho_celula

        self.linhas = altura // tamanho_celula
        self.colunas = largura // tamanho_celula

        self.pontos = [[0] * self.colunas for _ in range(self.linhas)]
        self.motoboy_x = self.motoboy_y = None
        self.pontos_entrega = []
        self.pontos_entregues = []

        self.desenhar_plano_cartesiano()

        self.selecionando_motoboy = False
        self.selecionando_entregas = False
        self.canvas.bind("<Button-1>", self.canvas_click)

        self.btn_reiniciar = tk.Button(self.control_frame, text="Reiniciar", command=self.reiniciar)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=5)
        self.btn_reiniciar['state'] = tk.DISABLED  


    def desenhar_plano_cartesiano(self):
        for linha in range(self.linhas + 1):
            y = linha * self.tamanho_celula
            self.canvas.create_line(0, y, self.largura, y, fill="black")

        for coluna in range(self.colunas + 1):
            x = coluna * self.tamanho_celula
            self.canvas.create_line(x, 0, x, self.altura, fill="black")
    
    def canvas_click(self, event):
        coluna = event.x // self.tamanho_celula
        linha = event.y // self.tamanho_celula

        if self.selecionando_motoboy:
            self.motoboy_x, self.motoboy_y = coluna, linha
            self.canvas.create_rectangle(coluna * self.tamanho_celula, linha * self.tamanho_celula,
                                        (coluna + 1) * self.tamanho_celula, (linha + 1) * self.tamanho_celula,
                                        fill="red")
            self.selecionando_motoboy = False
            self.btn_motoboy['state'] = tk.DISABLED
            self.desenhar_arestas()

        elif self.selecionando_entregas:
            if (coluna, linha) != (self.motoboy_x, self.motoboy_y):
                self.pontos_entrega.append((coluna, linha))
                self.canvas.create_rectangle(coluna * self.tamanho_celula, linha * self.tamanho_celula,
                                            (coluna + 1) * self.tamanho_celula, (linha + 1) * self.tamanho_celula,
                                            fill="blue")
                self.desenhar_arestas()

            if len(self.pontos_entrega) >= 3:  
                self.selecionando_entregas = False
                self.btn_entrega['state'] = tk.DISABLED
                self.btn_iniciar['state'] = tk.NORMAL


    def selecionar_motoboy(self):
        self.selecionando_motoboy = True

    def selecionar_entregas(self):
        self.selecionando_entregas = True
        self.desenhar_arestas()


    def desenhar_arestas(self):
        self.canvas.delete("aresta")
        
        if self.motoboy_x is not None and self.pontos_entrega:
            for ponto in self.pontos_entrega:
                self.canvas.create_line(self.motoboy_x * self.tamanho_celula + self.tamanho_celula // 2,
                                        self.motoboy_y * self.tamanho_celula + self.tamanho_celula // 2,
                                        ponto[0] * self.tamanho_celula + self.tamanho_celula // 2,
                                        ponto[1] * self.tamanho_celula + self.tamanho_celula // 2,
                                        fill="green", tags="aresta")

        for i in range(len(self.pontos_entrega)):
            for j in range(i + 1, len(self.pontos_entrega)):
                self.canvas.create_line(self.pontos_entrega[i][0] * self.tamanho_celula + self.tamanho_celula // 2,
                                        self.pontos_entrega[i][1] * self.tamanho_celula + self.tamanho_celula // 2,
                                        self.pontos_entrega[j][0] * self.tamanho_celula + self.tamanho_celula // 2,
                                        self.pontos_entrega[j][1] * self.tamanho_celula + self.tamanho_celula // 2,
                                        fill="green", tags="aresta")

    def iniciar_entrega(self):
        if self.motoboy_x is not None and self.pontos_entrega:
            menor_caminho = self.encontrar_menor_caminho()
            if menor_caminho:
                self.movimentos = deque(menor_caminho)
                self.mover_motoboy()
                self.btn_reiniciar['state'] = tk.NORMAL


    def encontrar_menor_caminho(self):
        menor_caminho = None
        menor_distancia = float("inf")
        for ponto_entrega in self.pontos_entrega:
            caminho = self.bfs(self.motoboy_x, self.motoboy_y, ponto_entrega[0], ponto_entrega[1])
            if caminho and len(caminho) < menor_distancia:
                menor_caminho = caminho
                menor_distancia = len(caminho)
        return menor_caminho

    def mover_motoboy(self):
        if self.movimentos:
            self.rastro()
            self.motoboy_x, self.motoboy_y = self.movimentos.popleft() 
            self.atualizar_desenho()
            self.master.after(500, self.mover_motoboy)
        if len(self.movimentos) == 0:
            self.entregue()


    def atualizar_desenho(self):
        self.pontos[self.motoboy_y][self.motoboy_x] = "motoboy"  
        for y, linha in enumerate(self.pontos):
            for x, ponto in enumerate(linha):
                if ponto == "motoboy":
                    self.canvas.create_rectangle(x * self.tamanho_celula, y * self.tamanho_celula,
                                                (x + 1) * self.tamanho_celula, (y + 1) * self.tamanho_celula,
                                                fill="red")   

    def rastro(self):
        for y, linha in enumerate(self.pontos):
            for x, ponto in enumerate(linha):
                if ponto == "motoboy" and ponto != "entregue":
                    self.canvas.create_rectangle(x * self.tamanho_celula, y * self.tamanho_celula,
                                                 (x + 1) * self.tamanho_celula, (y + 1) * self.tamanho_celula,
                                                 fill="gray")
                    self.pontos[self.motoboy_y][self.motoboy_x] = 0  

                    
    def entregue(self):
        for i, ponto_entrega in enumerate(self.pontos_entrega):
            x, y = ponto_entrega            
            if self.motoboy_x == x and self.motoboy_y == y:
                self.pontos_entregues.append(ponto_entrega)
                self.pontos[y][x] = "entregue"

                self.canvas.create_image((x * self.tamanho_celula) + (self.tamanho_celula // 2), 
                                        (y * self.tamanho_celula) + (self.tamanho_celula // 2), 
                                        anchor=tk.CENTER)


                self.pontos_entrega.pop(i)
                break

        if len(self.pontos_entrega):
            menor_caminho = self.encontrar_menor_caminho()
            if menor_caminho:
                self.movimentos = deque(menor_caminho)
                self.movimentos.popleft()
                self.mover_motoboy()


    def reiniciar(self):
        self.canvas.delete("all")

        self.desenhar_plano_cartesiano()

        self.pontos = [[0] * self.colunas for _ in range(self.linhas)]
        self.motoboy_x = self.motoboy_y = None
        self.pontos_entrega = []
        self.pontos_entregues = []

        self.btn_motoboy['state'] = tk.NORMAL
        self.btn_entrega['state'] = tk.NORMAL
        self.btn_iniciar['state'] = tk.DISABLED
        self.btn_reiniciar['state'] = tk.DISABLED

        self.selecionando_motoboy = False
        self.selecionando_entregas = False



    def bfs(self, x_inicial, y_inicial, x_final, y_final):
        visitado = [[False] * self.colunas for _ in range(self.linhas)]
        fila = [(x_inicial, y_inicial, [])]

        while fila:
            x, y, caminho = fila.pop(0)
            if x == x_final and y == y_final:
                return caminho + [(x, y)]

            if visitado[y][x]:
                continue
            visitado[y][x] = True

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  
                novo_x, novo_y = x + dx, y + dy
                if 0 <= novo_x < self.colunas and 0 <= novo_y < self.linhas and not visitado[novo_y][novo_x]:
                    fila.append((novo_x, novo_y, caminho + [(x, y)]))

        return None


root = tk.Tk()
largura = 1024
altura = 1024
tamanho_celula = 64
app = PlanoCartesianoApp(root, largura, altura, tamanho_celula)
root.mainloop()