import tkinter as tk
from tkinter import PhotoImage
import heapq
import copy
import random

class LabirintoApp:
    def __init__(self, master, largura, altura, tamanho_celula):
        self.master = master
        master.title("Labirinto")

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(fill=tk.X)

        self.canvas = tk.Canvas(master, width=largura, height=altura)
        self.canvas.pack()

        self.imagem_motoboy = PhotoImage(file="boy.png")
        self.imagem_inimigo = PhotoImage(file="boy.png")

        self.btn_reiniciar = tk.Button(self.control_frame, text="Reiniciar", command=self.reiniciar_jogo)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=5)

        self.largura = largura
        self.altura = altura
        self.tamanho_celula = tamanho_celula

        self.linhas = altura // tamanho_celula
        self.colunas = largura // tamanho_celula

        self.motoboy_x = self.motoboy_y = None
        self.inimigo_x = self.inimigo_y = None

        self.matriz = [[0] * self.colunas for _ in range(self.linhas)]

        self.criar_labirinto()
        self.canvas.bind("<KeyPress>", self.movimentar_motoboy)
        self.canvas.focus_set()

        self.movimentar_inimigo_continuamente()

    def criar_labirinto(self):
        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                if linha == 0 or linha == self.linhas - 1 or coluna == 0 or coluna == self.colunas - 1:
                    self.matriz[linha][coluna] = 1

        for linha in range(2, self.linhas - 2, 2):
            for coluna in range(2, self.colunas - 2, 2):
                self.matriz[linha][coluna] = 1
                direction = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                dx, dy = random.choice(direction)
                self.matriz[linha + dy][coluna + dx] = 1

        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                x1, y1 = coluna * self.tamanho_celula, linha * self.tamanho_celula
                x2, y2 = x1 + self.tamanho_celula, y1 + self.tamanho_celula
                if self.matriz[linha][coluna] == 1:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")
                elif linha == 1 and coluna == 1:
                    self.motoboy_x, self.motoboy_y = coluna, linha
                    self.canvas.create_image(x1 + self.tamanho_celula // 2, y1 + self.tamanho_celula // 2,
                                            image=self.imagem_motoboy, tags="motoboy")
                elif linha == self.linhas - 2 and coluna == self.colunas - 2:
                    self.inimigo_x, self.inimigo_y = coluna, linha
                    self.canvas.create_image(x1 + self.tamanho_celula // 2, y1 + self.tamanho_celula // 2,
                                            image=self.imagem_inimigo, tags="inimigo")


    def reiniciar_jogo(self):
        self.canvas.delete("all")
        self.matriz = [[0] * self.colunas for _ in range(self.linhas)]
        self.criar_labirinto()

    def movimentar_motoboy(self, event):
        direcao = event.keysym
        nova_x, nova_y = self.motoboy_x, self.motoboy_y

        if direcao == "Up":
            nova_y -= 1
        elif direcao == "Down":
            nova_y += 1
        elif direcao == "Left":
            nova_x -= 1
        elif direcao == "Right":
            nova_x += 1

        if self.matriz[nova_y][nova_x] == 0:
            self.motoboy_x, self.motoboy_y = nova_x, nova_y
            x1, y1 = nova_x * self.tamanho_celula, nova_y * self.tamanho_celula
            self.canvas.delete("motoboy")
            self.canvas.create_image(x1 + self.tamanho_celula // 2, y1 + self.tamanho_celula // 2,
                                     image=self.imagem_motoboy, tags="motoboy")

    def movimentar_inimigo_continuamente(self):
        self.movimentar_inimigo()
        self.master.after(180, self.movimentar_inimigo_continuamente)

    def movimentar_inimigo(self):
        caminho = self.dijkstra((self.inimigo_x, self.inimigo_y), (self.motoboy_x, self.motoboy_y))
        if caminho and len(caminho) > 1:
            self.inimigo_x, self.inimigo_y = caminho[1]
            x1, y1 = self.inimigo_x * self.tamanho_celula, self.inimigo_y * self.tamanho_celula
            self.canvas.delete("inimigo")
            self.canvas.create_image(x1 + self.tamanho_celula // 2, y1 + self.tamanho_celula // 2,
                                     image=self.imagem_inimigo, tags="inimigo")
            if self.inimigo_x == self.motoboy_x and self.inimigo_y == self.motoboy_y:
                self.game_over()

    def game_over(self):
        self.canvas.create_text(self.largura // 2, self.altura // 2, text="Game Over", font=("Arial", 24), fill="red")

    def dijkstra(self, start, end):
        pq = [(0, start)]
        dist = {start: 0}
        prev = {start: None}
        visited = set()
        while pq:
            current_dist, current = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)
            if current == end:
                path = []
                while current is not None:
                    path.append(current)
                    current = prev[current]
                return path[::-1]
            for neighbor in self.get_neighbors(current):
                distance = current_dist + 1
                if neighbor not in dist or distance < dist[neighbor]:
                    dist[neighbor] = distance
                    prev[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        return []

    def get_neighbors(self, node):
        x, y = node
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.colunas and 0 <= ny < self.linhas and self.matriz[ny][nx] == 0:
                neighbors.append((nx, ny))
        return neighbors

root = tk.Tk()
largura = 640
altura = 480
tamanho_celula = 32
app = LabirintoApp(root, largura, altura, tamanho_celula)
root.mainloop()
