import tkinter as tk
from tkinter import PhotoImage
import heapq
import copy


class PlanoCartesianoApp:
    def __init__(self, master, largura, altura, tamanho_celula):
        self.master = master
        master.title("Plano Cartesiano")

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(fill=tk.X)

        self.canvas = tk.Canvas(master, width=largura, height=altura)
        self.canvas.pack()

        self.imagem_motoboy = PhotoImage(file="./images/polvo.gif")

        self.btn_motoboy = tk.Button(self.control_frame, text="Selecionar ponto inicial do motoboy", command=self.selecionar_motoboy)
        self.btn_motoboy.pack(side=tk.LEFT, padx=5)

        self.btn_entrega = tk.Button(self.control_frame, text="Montar o grafo", command=self.selecionar_vertices)
        self.btn_entrega.pack(side=tk.LEFT, padx=5)

        self.btn_pontos_entrega = tk.Button(self.control_frame, text="Selecionar pontos de entrega", command=self.selecionar_pontos_entrega)
        self.btn_pontos_entrega.pack(side=tk.LEFT, padx=5)

        self.btn_iniciar = tk.Button(self.control_frame, text="Iniciar Entrega", command=self.iniciar_entrega)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        self.btn_iniciar['state'] = tk.DISABLED

        self.largura = largura
        self.altura = altura
        self.tamanho_celula = tamanho_celula

        self.linhas = altura // tamanho_celula
        self.colunas = largura // tamanho_celula

        self.pontos = [[0] * self.colunas for _ in range(self.linhas)]
        self.motoboy_x = self.motoboy_y = None
        self.pontos = []
        self.pontos_entrega = []
        self.global_pontos = []
        self.grafo = []
        self.aresta_pontos = {}  # Dictionary to store the points for each edge
        self.pontos_entregues = []

        self.desenhar_plano_cartesiano()

        self.cor_selecionada = None
        self.criar_legenda()

        self.selecionando_motoboy = False
        self.selecionando_entregas = False
        self.selecionando_pontos_entrega = False
        self.canvas.bind("<Button-1>", self.canvas_click)

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
            if self.is_vertex(coluna, linha):
                self.motoboy_x, self.motoboy_y = coluna, linha
                self.canvas.create_image(coluna * self.tamanho_celula + self.tamanho_celula // 2,
                                         linha * self.tamanho_celula + self.tamanho_celula // 2,
                                         image=self.imagem_motoboy, tags="motoboy")
                self.selecionando_motoboy = False
                self.btn_motoboy['state'] = tk.DISABLED

        elif self.selecionando_entregas:
            if (coluna, linha) != (self.motoboy_x, self.motoboy_y):
                self.pontos.append((coluna, linha))
                self.canvas.create_rectangle(coluna * self.tamanho_celula, linha * self.tamanho_celula,
                                             (coluna + 1) * self.tamanho_celula, (linha + 1) * self.tamanho_celula,
                                             fill="black")
                if len(self.pontos) == 2:
                    self.grafo.append((self.pontos[0], self.pontos[1], self.cor_selecionada))
                    self.pontos = []

                self.desenhar_arestas()

            if len(self.grafo) >= 3:
                self.selecionando_entregas = False
                self.btn_entrega['state'] = tk.DISABLED

        elif self.selecionando_pontos_entrega:
            if self.is_vertex(coluna, linha) and (coluna, linha) != (self.motoboy_x, self.motoboy_y) and (coluna, linha) not in self.pontos_entrega:
                self.pontos_entrega.append((coluna, linha))
                self.canvas.create_rectangle(coluna * self.tamanho_celula, linha * self.tamanho_celula,
                                             (coluna + 1) * self.tamanho_celula, (linha + 1) * self.tamanho_celula,
                                             fill="blue")
            if len(self.pontos_entrega) >= len(self.grafo):
                self.selecionando_pontos_entrega = False
                self.btn_pontos_entrega['state'] = tk.DISABLED
                if len(self.pontos_entrega) > 0:
                    self.btn_iniciar['state'] = tk.NORMAL

    def is_vertex(self, coluna, linha):
        for (ponto1, ponto2, cor) in self.grafo:
            if (coluna, linha) == ponto1 or (coluna, linha) == ponto2:
                return True
        return False

    def selecionar_motoboy(self):
        self.selecionando_motoboy = True

    def selecionar_vertices(self):
        self.selecionando_entregas = True
        self.desenhar_arestas()

    def selecionar_pontos_entrega(self):
        self.selecionando_pontos_entrega = True

    def criar_legenda(self):
        cores = ["#00FF00", "#33CC00", "#66CC00", "#99CC00", "#CCCC00", "#FFCC00", "#FF9900", "#FF6600", "#FF3300", "#FF0000"]
        self.legenda_frame = tk.Frame(self.control_frame)
        self.legenda_frame.pack(side=tk.RIGHT, padx=5)
        self.legenda_labels = []
        for i, cor in enumerate(cores):
            label = tk.Label(self.legenda_frame, bg=cor, width=2, height=1)
            label.grid(row=0, column=i, padx=1)
            label.bind("<Button-1>", lambda e, idx=i: self.selecionar_cor_legenda(idx))
            self.legenda_labels.append(label)
        self.selecionar_cor_legenda(0)  # Seleciona a cor verde mais clara por padrão

    def selecionar_cor_legenda(self, idx):
        cores = ["#00FF00", "#33CC00", "#66CC00", "#99CC00", "#CCCC00", "#FFCC00", "#FF9900", "#FF6600", "#FF3300", "#FF0000"]
        self.cor_selecionada = [cores[idx], idx]
        for label in self.legenda_labels:
            label.config(relief=tk.FLAT)
        self.legenda_labels[idx].config(relief=tk.SUNKEN)

    def desenhar_arestas(self):
        self.canvas.delete("aresta")
        for (ponto1, ponto2, cor) in self.grafo:
            x1, y1 = ponto1
            x2, y2 = ponto2
            aresta_chave = f"{ponto1}-{ponto2}"
            self.aresta_pontos[aresta_chave] = []  # Initialize the list of points for this edge
            self.aresta_pontos[aresta_chave].append(ponto1)
            while (x1 != x2 or y1 != y2):
                if x1 != x2:
                    x1 += 1 if x1 < x2 else -1
                elif y1 != y2:
                    y1 += 1 if y1 < y2 else -1

                if (x1, y1) != (x2, y2):
                    tag = f"{x1},{y1}"
                    self.canvas.create_rectangle(x1 * self.tamanho_celula, y1 * self.tamanho_celula,
                                                (x1 + 1) * self.tamanho_celula, (y1 + 1) * self.tamanho_celula,
                                                fill=cor[0], tags=("aresta", tag))
                    self.aresta_pontos[aresta_chave].append((x1, y1))
            self.aresta_pontos[aresta_chave].append(ponto2)

    def iniciar_entrega(self):
        if self.motoboy_x is not None and self.pontos_entrega:
            self.entregar_proximo_ponto()

    def entregar_proximo_ponto(self):
        if self.pontos_entrega:
            ponto_mais_proximo = self.encontrar_ponto_mais_proximo()
            if ponto_mais_proximo:
                self.movimentos = self.dijkstra((self.motoboy_x, self.motoboy_y), ponto_mais_proximo)
                self.pontos_entrega.remove(ponto_mais_proximo)
                self.mover_motoboy()

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
            for neighbor, weight in self.get_neighbors(current):
                distance = current_dist + weight
                if neighbor not in dist or distance < dist[neighbor]:
                    dist[neighbor] = distance
                    prev[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
        return []

    def get_neighbors(self, node):
        neighbors = []
        for (ponto1, ponto2, cor) in self.grafo:
            weight = cor[1] + 1  # O índice da cor representa o peso
            if node == ponto1:
                neighbors.append((ponto2, weight))
            elif node == ponto2:
                neighbors.append((ponto1, weight))
        return neighbors

    def encontrar_ponto_mais_proximo(self):
        min_dist = float('inf')
        closest_point = None
        for ponto in self.pontos_entrega:
            caminho = self.dijkstra((self.motoboy_x, self.motoboy_y), ponto)
            if caminho:
                dist = sum(self.get_edge_weight(caminho[i], caminho[i + 1]) for i in range(len(caminho) - 1))
                if dist < min_dist:
                    min_dist = dist
                    closest_point = ponto
        return closest_point

    def get_edge_weight(self, ponto1, ponto2):
        for (p1, p2, cor) in self.grafo:
            if (ponto1 == p1 and ponto2 == p2) or (ponto1 == p2 and ponto2 == p1):
                return cor[1] + 1
        return float('inf')

    def mover_motoboy(self):
        if self.movimentos:
            x1, y1 = self.motoboy_x, self.motoboy_y
            x2, y2 = self.movimentos[0]

            aresta_chave_1 = f"{(x1, y1)}-{(x2, y2)}"
            aresta_chave_2 = f"{(x2, y2)}-{(x1, y1)}"
            
            if aresta_chave_1 in self.aresta_pontos:
                self.global_pontos = copy.deepcopy(self.aresta_pontos.get(aresta_chave_1, []))
            elif aresta_chave_2 in self.aresta_pontos:
                self.global_pontos = list(reversed(copy.deepcopy(self.aresta_pontos.get(aresta_chave_2, []))))
            else:
                self.global_pontos = []
    
            self.mover_passo_a_passo()
        else:
            if self.pontos_entrega:
                self.entregar_proximo_ponto()
            else:
                self.motoboy_entrega_concluida()

    def mover_passo_a_passo(self):
        if self.global_pontos:
            next_x, next_y = self.global_pontos.pop(0)
            self.rastro(self.motoboy_x, self.motoboy_y)
            self.canvas.delete("motoboy")
            self.canvas.create_image(next_x * self.tamanho_celula + self.tamanho_celula // 2,
                                    next_y * self.tamanho_celula + self.tamanho_celula // 2,
                                    image=self.imagem_motoboy, tags="motoboy")
            self.motoboy_x, self.motoboy_y = next_x, next_y
            self.master.after(500, self.mover_passo_a_passo)
        else:
            if self.movimentos:
                self.movimentos.pop(0)  # Move to the next movement step
                self.mover_motoboy()



    def rastro(self, x, y):
        tag = f"{x},{y}"
        items = self.canvas.find_withtag(tag)
        if items:
            self.canvas.itemconfig(items[0], fill="gray")
        else:
            self.canvas.create_rectangle(x * self.tamanho_celula, y * self.tamanho_celula,
                                        (x + 1) * self.tamanho_celula, (y + 1) * self.tamanho_celula,
                                        fill="gray", tags=("aresta", tag))



    def motoboy_entrega_concluida(self):
        self.canvas.create_text(self.motoboy_x * self.tamanho_celula + self.tamanho_celula // 2,
                                self.motoboy_y * self.tamanho_celula + self.tamanho_celula // 2,
                                text="✔️", font=("Arial", 24), fill="green")

root = tk.Tk()
largura = 1024
altura = 1024
tamanho_celula = 64
app = PlanoCartesianoApp(root, largura, altura, tamanho_celula)
root.mainloop()
