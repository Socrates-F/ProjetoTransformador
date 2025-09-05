import math
import json
import numpy as np
import plotly.graph_objects as go
import base64
import matplotlib.pyplot as plt
import webbrowser
import os
from typing import List, Dict, Tuple, Optional
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from io import BytesIO
from PIL import Image



class TransformadorMonofasico1:
    def __init__(self):
        # Dados de entrada
        self.tipo_transformador: str = None
        self.Vp: List[float] = None      # Tensões primárias (V)
        self.Vs: List[float] = None      # Tensões secundárias (V)
        self.Potencia: float = None      # Potência (VA)
        self.frequencia: int = 50        # Frequência (Hz)
        self.tipo_lamina: str = None     # Tipo de lâmina ("Padronizada" ou "Comprida")
        
        # Dados calculados
        self.Np: List[int] = None        # Número de espiras primário
        self.Ns: List[int] = None        # Número de espiras secundário
        self.Ip: List[float] = None      # Corrente primária (A)
        self.Is: List[float] = None      # Corrente secundária (A)
        self.bitola_primario: List[Dict] = None  # Bitola do cabo primário
        self.bitola_secundario: List[Dict] = None  # Bitola do cabo secundário
        self.lamina_selecionada: Dict = None  # Lâmina selecionada
        self.quant_laminas: int = None   # Quantidade de lâminas
        self.Sm: float = None           # Seção magnética do núcleo (cm²)
        self.Sg: float = None           # Seção geométrica do núcleo (cm²)
        self.dimensoes_nucleo: Tuple[float, float] = None  # Dimensões do núcleo (a x b)
        self.peso_ferro: float = None   # Peso do ferro (kg)
        self.peso_cobre: float = None   # Peso do cobre (kg)
        self.viabilidade: bool = None   # Se o transformador é viável
        self.mensagem_viabilidade: str = None  # Mensagem sobre viabilidade
        
        # Lista de tipos válidos
        self.tipos_validos = [
            "Transformador de um primário e um secundário",
            "Transformador de dois primários e um secundário",
            "Transformador de um primário e dois secundários",
            "Transformador de dois primários e dois secundários"
        ]
        
        # Tabelas de referência
        self.laminas_padronizadas = [
            {"numero": 0, "a_cm": 1.5, "secao_mm2": 168, "peso_kgcm": 0.095},
            {"numero": 1, "a_cm": 2, "secao_mm2": 300, "peso_kgcm": 0.170},
            {"numero": 2, "a_cm": 2.5, "secao_mm2": 468, "peso_kgcm": 0.273},
            {"numero": 3, "a_cm": 3, "secao_mm2": 675, "peso_kgcm": 0.380},
            {"numero": 4, "a_cm": 3.5, "secao_mm2": 900, "peso_kgcm": 0.516},
            {"numero": 5, "a_cm": 4, "secao_mm2": 1200, "peso_kgcm": 0.674},
            {"numero": 6, "a_cm": 5, "secao_mm2": 1880, "peso_kgcm": 1.053}
        ]
        
        self.laminas_compridas = [
            {"numero": 5, "a_cm": 4, "secao_mm2": 2400, "peso_kgcm": 1.000},
            {"numero": 6, "a_cm": 5, "secao_mm2": 3750, "peso_kgcm": 1.580}
        ]
        
        self.awg_table = [
            {"AWG": 25, "area_mm2": 0.162}, {"AWG": 24, "area_mm2": 0.205},
            {"AWG": 23, "area_mm2": 0.258}, {"AWG": 22, "area_mm2": 0.326},
            {"AWG": 21, "area_mm2": 0.410}, {"AWG": 20, "area_mm2": 0.518},
            {"AWG": 19, "area_mm2": 0.653}, {"AWG": 18, "area_mm2": 0.823},
            {"AWG": 17, "area_mm2": 1.04}, {"AWG": 16, "area_mm2": 1.31},
            {"AWG": 15, "area_mm2": 1.65}, {"AWG": 14, "area_mm2": 2.08},
            {"AWG": 13, "area_mm2": 2.62}, {"AWG": 12, "area_mm2": 3.31},
            {"AWG": 11, "area_mm2": 4.17}, {"AWG": 10, "area_mm2": 5.26},
            {"AWG": 9, "area_mm2": 6.63}, {"AWG": 8, "area_mm2": 8.37},
            {"AWG": 7, "area_mm2": 10.55}, {"AWG": 6, "area_mm2": 13.30},
            {"AWG": 5, "area_mm2": 16.80}, {"AWG": 4, "area_mm2": 21.15},
            {"AWG": 3, "area_mm2": 26.67}, {"AWG": 2, "area_mm2": 33.62},
            {"AWG": 1, "area_mm2": 42.41}, {"AWG": 0, "area_mm2": 53.49},
        ]
    
    def carregar_dados_entrada(self, arquivo_json: str) -> bool:
        """Carrega os dados de entrada de um arquivo JSON com validações adicionais"""
        try:
            with open(arquivo_json, 'r') as f:
                dados = json.load(f)
            
            # Validar dados obrigatórios
            campos_obrigatorios = ['tipo_transformador', 'Vp', 'Vs', 'Potencia', 'tipo_lamina']
            for campo in campos_obrigatorios:
                if campo not in dados:
                    raise ValueError(f"Campo obrigatório '{campo}' não encontrado no JSON")
            
            self.tipo_transformador = dados['tipo_transformador']
            
            # Validação adicional do tipo de transformador
            if self.tipo_transformador not in self.tipos_validos:
                raise ValueError(f"Tipo de transformador inválido. Deve ser um dos: {', '.join(self.tipos_validos)}")
            
            # Processar tensões (aceita string com / ou lista)
            if isinstance(dados['Vp'], str):
                self.Vp = [float(v) for v in str(dados['Vp']).split('/') if v]
            else:
                self.Vp = [float(v) for v in dados['Vp']]
                
            if isinstance(dados['Vs'], str):
                self.Vs = [float(v) for v in str(dados['Vs']).split('/') if v]
            else:
                self.Vs = [float(v) for v in dados['Vs']]
            
            if not self.Vp or not self.Vs:
                raise ValueError("Tensões primárias ou secundárias não foram fornecidas corretamente")
            
            # Validação do número de tensões de acordo com o tipo
            tipo = self.tipo_transformador.lower()
            if "um primário" in tipo and len(self.Vp) != 1:
                raise ValueError("Deve haver exatamente uma tensão primária para este tipo de transformador")
            if "dois primários" in tipo and len(self.Vp) != 2:
                raise ValueError("Deve haver exatamente duas tensões primárias para este tipo de transformador")
            if "um secundário" in tipo and len(self.Vs) != 1:
                raise ValueError("Deve haver exatamente uma tensão secundária para este tipo de transformador")
            if "dois secundários" in tipo and len(self.Vs) != 2:
                raise ValueError("Deve haver exatamente duas tensões secundárias para este tipo de transformador")
            
            self.Potencia = float(dados['Potencia'])
            if self.Potencia <= 0:
                raise ValueError("Potência deve ser maior que zero")
            
            self.tipo_lamina = dados['tipo_lamina']
            if self.tipo_lamina not in ["Padronizada", "Comprida"]:
                raise ValueError("Tipo de lâmina deve ser 'Padronizada' ou 'Comprida'")
            
            # Frequência é opcional (padrão 50Hz)
            self.frequencia = int(dados.get('frequencia', 50))
            if self.frequencia not in [50, 60]:
                print("Aviso: Frequência diferente de 50Hz ou 60Hz. Cálculos podem não ser precisos.")
            
            return True
        
        except FileNotFoundError:
            print(f"Erro: Arquivo '{arquivo_json}' não encontrado.")
            return False
        except json.JSONDecodeError:
            print("Erro: Arquivo JSON mal formatado.")
            return False
        except ValueError as e:
            print(f"Erro nos dados de entrada: {str(e)}")
            return False
        except Exception as e:
            print(f"Erro inesperado: {str(e)}")
            return False
    
    def calcular_correntes_e_secao(self):
        """Calcula correntes e seções dos condutores"""
        # Potência primária com margem de 10%
        W1 = 1.1 * self.Potencia
        
        # Correntes primárias
        self.Ip = [round(W1 / v, 2) for v in self.Vp]
        
        # Correntes secundárias
        self.Is = [round(self.Potencia / v, 2) for v in self.Vs]
        
        # Densidade de corrente (pode variar com tipo de transformador)
        if self.Potencia <= 500:
            d = 3.0
        elif self.Potencia <= 1000:
            d = 2.5
        else:
            d = 2.0
        
        # Seções dos condutores
        secao_primario = [round(i / d, 2) for i in self.Ip]
        secao_secundario = [round(i / d, 2) for i in self.Is]
        
        # Encontrar bitolas AWG mais próximas
        self.bitola_primario = [self._encontrar_awg_por_secao(s) for s in secao_primario]
        self.bitola_secundario = [self._encontrar_awg_por_secao(s) for s in secao_secundario]
    
    def _encontrar_awg_por_secao(self, secao_mm2: float) -> Dict:
        """Encontra o fio AWG mais adequado para uma dada seção"""
        for fio in self.awg_table:
            if fio["area_mm2"] >= secao_mm2:
                return fio
        return self.awg_table[-1]  # Retorna o maior disponível se não encontrar
    
    def calcular_espiras(self):
        """Calcula o número de espiras para primário e secundário"""
        # Fator baseado no tipo de transformador (atualizado para todos os casos)
        fator_tipo = {
            "Transformador de um primário e um secundário": 1,
            "Transformador de dois primários e um secundário": 1.25,
            "Transformador de um primário e dois secundários": 1.25,
            "Transformador de dois primários e dois secundários": 1.5
        }.get(self.tipo_transformador, 1)
        
        # Coeficiente baseado no tipo de lâmina
        coef = 7.5 if self.tipo_lamina == "Padronizada" else 6
        
        # Seção magnética do núcleo
        self.Sm = round(coef * math.sqrt((fator_tipo * self.Potencia) / self.frequencia), 1)
        
        # Seção geométrica do núcleo (10% maior que Sm)
        self.Sg = round(self.Sm * 1.1, 1)
        
        # Dimensões do núcleo
        a = math.ceil(math.sqrt(self.Sg))  # Largura da coluna central
        b = round(self.Sg / a)             # Comprimento do pacote laminado
        
        # Selecionar lâmina mais adequada
        laminas = self.laminas_padronizadas if self.tipo_lamina == "Padronizada" else self.laminas_compridas
        for lamina in laminas:
            if a <= lamina["a_cm"]:
                self.lamina_selecionada = lamina
                break
        else:
            self.lamina_selecionada = laminas[-1]
        
        # Ajustar dimensões reais baseado na lâmina selecionada
        a = self.lamina_selecionada["a_cm"]
        self.quant_laminas = math.ceil(b / a)
        b = a * self.quant_laminas  # Ajusta b para múltiplo inteiro da largura da lâmina
        self.dimensoes_nucleo = (a, b)
        self.Sg = a * b
        self.Sm = round(self.Sg / 1.1, 2)
        
        # Espiras por volt
        if self.frequencia == 50:
            esp_por_volt = round(40 / self.Sm, 2)
        elif self.frequencia == 60:
            esp_por_volt = round(33.5 / self.Sm, 2)
        else:
            esp_por_volt = round((1e8 / (4.44 * 11300 * self.frequencia)) / self.Sm, 2)
        
        # Número de espiras
        self.Np = [math.ceil(esp_por_volt * v) for v in self.Vp]
        self.Ns = [math.ceil(esp_por_volt * v * 1.1) for v in self.Vs]  # +10% para compensar perdas
    
    def verificar_viabilidade(self):
        """Verifica se o transformador é viável (relação Sj/Scu >= 3)"""
        # Calcular área total de cobre (Scu)
        Scu = 0
        
        # Área dos enrolamentos primários
        for i, n in enumerate(self.Np):
            if i < len(self.bitola_primario):
                Scu += n * self.bitola_primario[i]["area_mm2"]
        
        # Área dos enrolamentos secundários
        for i, n in enumerate(self.Ns):
            if i < len(self.bitola_secundario):
                Scu += n * self.bitola_secundario[i]["area_mm2"]
        
        # Área da janela (Sj)
        Sj = self.lamina_selecionada["secao_mm2"]
        
        # Relação Sj/Scu
        relacao = Sj / Scu if Scu > 0 else 0
        
        self.viabilidade = relacao >= 3
        self.mensagem_viabilidade = (
            f"Transformador viável (Sj/Scu = {relacao:.2f} >= 3)" 
            if self.viabilidade 
            else f"Transformador não viável (Sj/Scu = {relacao:.2f} < 3)"
        )
    
    def calcular_pesos(self):
        """Calcula o peso do ferro e do cobre"""
        a, b = self.dimensoes_nucleo
        
        # Peso do ferro (kg)
        self.peso_ferro = self.lamina_selecionada["peso_kgcm"] * b * a
        
        # Peso do cobre
        Scu = 0
        for i, n in enumerate(self.Np):
            if i < len(self.bitola_primario):
                Scu += n * self.bitola_primario[i]["area_mm2"]
        
        for i, n in enumerate(self.Ns):
            if i < len(self.bitola_secundario):
                Scu += n * self.bitola_secundario[i]["area_mm2"]
        
        # Comprimento médio da espira (aproximado)
        lm = (2*a) + (2*b) + (math.pi*a)  # em cm
        
        # Peso do cobre (considerando densidade do cobre = 9g/cm³)
        self.peso_cobre = (Scu / 100 * lm * 9) / 1000  # em kg
    
    def gerar_imagem_3d(self, angle_rad=0) -> str:
        """Gera visualização 3D do transformador e salva em HTML interativo"""
        import plotly.graph_objects as go
        import numpy as np
        import os

        # Cria os 8 vértices de um paralelepípedo a partir da posição (x, y, z) e das dimensões (dx, dy, dz)
        def criar_secoes(x, y, z, dx, dy, dz):
            return np.array([
                [x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z],
                [x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]
            ])

        # Aplica rotação 3D em torno do eixo Z
        def rotacionar(vertices, angle):
            R = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle),  np.cos(angle), 0],
                [0, 0, 1]
            ])
            return vertices @ R.T

        # Adiciona um bloco 3D (núcleo ou bobina) ao gráfico
        def plot_bloco(fig, vertices, color='gray', opacity=0.6):
            # Extrai coordenadas dos vértices
            vx, vy, vz = vertices[:, 0], vertices[:, 1], vertices[:, 2]
            # Define faces do paralelepípedo (em quads, convertidas para triângulos)
            faces_quad = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4],
                        [3, 2, 6, 7], [0, 3, 7, 4], [1, 2, 6, 5]]
            i_tri, j_tri, k_tri = [], [], []
            for face in faces_quad:
                i_tri += [face[0], face[0]]
                j_tri += [face[1], face[2]]
                k_tri += [face[2], face[3]]
            # Adiciona a malha (superfície 3D)
            fig.add_trace(go.Mesh3d(
                x=vx, y=vy, z=vz, i=i_tri, j=j_tri, k=k_tri,
                color=color, opacity=opacity, flatshading=True, alphahull=0
            ))
            # Adiciona as bordas do bloco como linhas pretas
            edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                    (0,4),(1,5),(2,6),(3,7)]
            edge_x, edge_y, edge_z = [], [], []
            for p1, p2 in edges:
                edge_x += [vertices[p1,0], vertices[p2,0], None]
                edge_y += [vertices[p1,1], vertices[p2,1], None]
                edge_z += [vertices[p1,2], vertices[p2,2], None]
            fig.add_trace(go.Scatter3d(
                x=edge_x, y=edge_y, z=edge_z, mode='lines',
                line=dict(color='black', width=2), showlegend=False
            ))

        # Adiciona espiras helicoidais para representar enrolamentos
        def add_espiras(fig, cx, cy, z0, z1, raio, cor, nome):
            t = np.linspace(0, 2*np.pi*8, 300)  # Ângulo
            z = np.linspace(z0, z1, 300)       # Altura crescente
            x = cx + raio * np.cos(t)          # Hélice em X
            y = cy + raio * np.sin(t)          # Hélice em Y
            pontos = np.stack([x, y, z], axis=1)
            rot = rotacionar(pontos, angle_rad)
            fig.add_trace(go.Scatter3d(
                x=rot[:,0], y=rot[:,1], z=rot[:,2],
                mode='lines', line=dict(color=cor, width=4), name=nome
            ))

        # === GEOMETRIA DO NÚCLEO E BOBINAS ===
        a, b = self.dimensoes_nucleo  # Largura da coluna e altura do núcleo
        fig = go.Figure()

        # Dimensões da coluna central do núcleo
        pc_dx, pc_dy, pc_dz = a * 0.8, b * 0.7, 0.8 * a
        pc_x = 1.5 * a - pc_dx / 2
        pc_y = b / 2 - pc_dy / 2
        pc_z = 1.25 * a - pc_dz / 2

        # Dimensões das pernas laterais
        pl_dx = pc_dx / 2
        pl_dy = pc_dy
        pl_dz = pc_dz
        janela_x = a * 0.35

        # Posição das pernas esquerda e direita
        ple_x = pc_x - janela_x - pl_dx
        pld_x = pc_x + pc_dx + janela_x
        centro_x_ple = ple_x + pl_dx/2
        centro_y_ple = pc_y + pl_dy/2
        centro_x_pld = pld_x + pl_dx/2
        centro_y_pld = pc_y + pl_dy/2

        # Altura das espiras e das bases
        esp_z0 = pc_z
        esp_z1 = pc_z + pc_dz
        espessura = a * 0.3
        base_z = pc_z - espessura
        topo_z = esp_z1

        # === DESLOCAMENTO PARA A ORIGEM (0,0,0) ===
        offset_x = ple_x
        offset_y = pc_y
        offset_z = base_z

        centro_x_ple -= offset_x
        centro_y_ple -= offset_y
        centro_x_pld -= offset_x
        centro_y_pld -= offset_y
        esp_z0 -= offset_z
        esp_z1 -= offset_z
        topo_z -= offset_z

        # Lista de blocos que compõem o transformador
        partes = [
            [pc_x - offset_x, pc_y - offset_y, pc_z - offset_z, pc_dx, pc_dy, pc_dz],  # Coluna central
            [ple_x - offset_x, pc_y - offset_y, pc_z - offset_z, pl_dx, pl_dy, pl_dz],  # Perna esquerda
            [pld_x - offset_x, pc_y - offset_y, pc_z - offset_z, pl_dx, pl_dy, pl_dz],  # Perna direita
            [ple_x - offset_x, pc_y - offset_y, base_z - offset_z, (pld_x+pl_dx)-ple_x, pc_dy, espessura],  # Base inferior
            [ple_x - offset_x, pc_y - offset_y, topo_z, (pld_x+pl_dx)-ple_x, pc_dy, espessura]              # Base superior
        ]

        # Adiciona todos os blocos ao gráfico 3D
        for x, y, z, dx, dy, dz in partes:
            v = criar_secoes(x, y, z, dx, dy, dz)
            v_rot = rotacionar(v, angle_rad)
            plot_bloco(fig, v_rot, color='rgb(160,160,170)', opacity=0.65)

        # Adiciona as espiras primárias e secundárias
        add_espiras(fig, centro_x_ple, centro_y_ple, esp_z0, esp_z1, pl_dx * 0.6, 'brown', 'Primário')
        add_espiras(fig, centro_x_pld, centro_y_pld, esp_z0, esp_z1, pl_dx * 0.6, 'gold', 'Secundário')

        # === Adiciona o texto Np e Ns como legendas flutuantes ===
        if self.Np and self.Ns:
            fig.add_trace(go.Scatter3d(
                x=[centro_x_ple],
                y=[centro_y_ple],
                z=[esp_z1 + 0.3 * a],
                mode='text',
                text=[f"<b>Np = {self.Np[0]}</b>"],
                showlegend=False,
                textfont=dict(size=20, color='brown')
            ))
            fig.add_trace(go.Scatter3d(
                x=[centro_x_pld],
                y=[centro_y_pld],
                z=[esp_z1 + 0.3 * a],
                mode='text',
                text=[f"<b>Ns = {self.Ns[0]}</b>"],
                showlegend=False,
                textfont=dict(size=20, color='goldenrod')
            ))

        # === Configuração do layout e da câmera ===
        fig.update_layout(
            scene=dict(
                xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
                aspectmode='data',
                bgcolor='white',
                camera=dict(eye=dict(x=-2.0, y=-2.0, z=1.5)),  # Câmera olhando na direção oposta do eixo X
                xaxis_showspikes=False, yaxis_showspikes=False, zaxis_showspikes=False
            ),
            width=1000, height=800,
            margin=dict(l=0, r=0, b=0, t=40),
            title="Transformador Monofásico 3D"
        )

        # === Exporta o HTML interativo ===
        html_path = "transformador_3d_interativo.html"
        fig.write_html(html_path, include_plotlyjs="cdn")
        return html_path




    def gerar_resultados_json(self) -> Dict:
        resultados = {
            "dados_entrada": {
                "tipo_transformador": self.tipo_transformador,
                "tensao_primaria": self.Vp,
                "tensao_secundaria": self.Vs,
                "potencia": self.Potencia,
                "frequencia": self.frequencia,
                "tipo_lamina": self.tipo_lamina
            },
            "resultados": {
                "espiras": {
                    "primario": self.Np,
                    "secundario": self.Ns
                },
                "bitolas": {
                    "primario": [{"AWG": b["AWG"], "area_mm2": b["area_mm2"]} for b in self.bitola_primario],
                    "secundario": [{"AWG": b["AWG"], "area_mm2": b["area_mm2"]} for b in self.bitola_secundario]
                },
                "nucleo": {
                    "lamina": self.lamina_selecionada["numero"],
                    "quantidade": self.quant_laminas,
                    "secao_magnetica": self.Sm,
                    "secao_geometrica": self.Sg,
                    "dimensoes": {
                        "a": self.dimensoes_nucleo[0],
                        "b": self.dimensoes_nucleo[1]
                    }
                },
                "pesos": {
                    "ferro": round(self.peso_ferro, 2),
                    "cobre": round(self.peso_cobre, 2)
                },
                "viabilidade": {
                    "executavel": self.viabilidade,
                    "mensagem": self.mensagem_viabilidade
                },
                "dimensoes_finais": {
                    "largura": self.dimensoes_nucleo[0] + 4,
                    "profundidade": self.dimensoes_nucleo[1] + 4,
                    "altura": self.dimensoes_nucleo[1] * 1.5
                }
            },
            # "imagem_3d_base64": self.imagem_3d_base64
        }
        return resultados

    def executar_desafio1(self, arquivo_json: str) -> Optional[Dict]:
        if not self.carregar_dados_entrada(arquivo_json):
            return None

        self.calcular_correntes_e_secao()
        self.calcular_espiras()
        self.verificar_viabilidade()
        self.calcular_pesos()
        self.gerar_imagem_3d()

        resultados = self.gerar_resultados_json()

        # Mostrar resultados no terminal
        print("\n=== RESULTADOS DO TRANSFORMADOR ===")
        print(json.dumps(resultados, indent=2, ensure_ascii=False))
        
        return resultados

# Exemplo 1 - Transformador simples (1 primário + 1 secundário)
dados_exemplo1 = {
    "tipo_transformador": "Transformador de um primário e um secundário",
    "Vp": "120",
    "Vs": "12",
    "Potencia": 100,
    "tipo_lamina": "Padronizada",
    "frequencia": 60
}

# Salvar em arquivo JSON
with open('exemplo1_transformador.json', 'w') as f:
    json.dump(dados_exemplo1, f, indent=2)

# Executar dimensionamento
transformador1 = TransformadorMonofasico1()
resultados1 = transformador1.executar_desafio1('exemplo1_transformador.json')

# if __name__ == "__main__":
#     try:
#         parametros_json = {
#             "tipo_transformador": "Transformador de um primário e um secundário",
#             "Vp": "120",
#             "Vs": "12",
#             "Potencia": 100,
#             "tipo_lamina": "Padronizada",
#             "frequencia": 60
#         }

#         transformador1 = TransformadorMonofasico1()
#         resultados1 = transformador1.executar_desafio1(parametros_json)

#     except Exception as e:
#         print(f"Erro: {e}")





if resultados1:
    print("\n=== Resultados Exemplo 1 ===")
    print(f"Espiras Primário: {resultados1['resultados']['espiras']['primario'][0]}")
    print(f"Espiras Secundário: {resultados1['resultados']['espiras']['secundario'][0]}")
    print(f"Bitola Primário: AWG {resultados1['resultados']['bitolas']['primario'][0]['AWG']}")
    print(f"Bitola Secundário: AWG {resultados1['resultados']['bitolas']['secundario'][0]['AWG']}")
    print(f"Viabilidade: {resultados1['resultados']['viabilidade']['mensagem']}")
