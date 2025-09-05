import math
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
import plotly.graph_objects as go

class TransformadorMonofasico:
    def __init__(self, N1=1000, N2=200,Va=40, Ia=5, Pa=100,Vb=220, Ib=1.2, Pb=60,circuit_type='Serie',
                 referred_to='primario',sec_type='circuito-aberto'):
        
        self.N1 = N1 # Nª espiras primário
        self.N2 = N2 # Nº espiras secundárioo
        self.Va = Va # Tensão no ensaio de curto-circuito
        self.Ia = Ia # Corrente no ensaio de curto-circuito
        self.Pa = Pa # Potência ativa no ensaio de curto-circuito
        self.Vb = Vb # Tensão no ensaio de circuito aberto
        self.Ib = Ib # Corrente no ensaio de circuito aberto
        self.Pb = Pb # Potência ativa no ensaio de circuito aberto
        self.circuit_type = circuit_type
        self.referred_to = referred_to # Para qual lado referir os parâmetros: primário ou secundário
        self.sec_type = sec_type   # Qual lado foi usado no ensaio de circuito aberto
        self.prim_type = "curto-circuito" if sec_type == "circuito-aberto" else "circuito-aberto"

        self.processar_ensaios()

    # Calculo da relação de transformação a = N1/N2
    def calcular_relacao_transformacao(self):
        return self.N1 / self.N2

    # Reflete uma impedância medida para o lado desejado
    # Z_eq_referido = Z_eq * a^2 (para primário), Z_eq / a^2 (para secundário)
    def referir_impedancia(self, valor, a, lado_ensaio, lado_referido):
        if lado_ensaio == lado_referido:
            return valor
        elif lado_referido == "primario":
            return valor * a ** 2
        elif lado_referido == "secundario":
            return valor / a ** 2
        return valor

    # Ensaio de circuito aberto para obter Rc_ref e Xm_ref
    def calcular_ensaio_circuito_aberto(self):
        if self.Ib == 0 or self.Vb == 0:
            return 0, 0, 0, 0, 0

        a = self.calcular_relacao_transformacao()
        lado_ensaio = "secundario" if self.sec_type == "circuito-aberto" else "primario"
        Rc = self.Vb ** 2 / self.Pb if self.Pb > 0 else float('inf')  #P = V * I * cos(phi) => Rc = V^2 / P (perdas no ferro)
        Ic = self.Pb / self.Vb
        Im = math.sqrt(self.Ib ** 2 - Ic ** 2) if self.Ib > Ic else 0 # Im = sqrt(Itotal^2 - Ic^2) => componente magnetizante (reativa)
        Xm = self.Vb / Im if Im != 0 else float('inf')
        Zphi = self.Vb / self.Ib if self.Ib != 0 else float('inf')

        Rc_ref = self.referir_impedancia(Rc, a, lado_ensaio, self.referred_to)
        Xm_ref = self.referir_impedancia(Xm, a, lado_ensaio, self.referred_to)

        return Rc_ref, Xm_ref, Zphi, Ic, Im

    # Ensaio de curto-circuito: obtém Req e Xeq
    def calcular_ensaio_curto_circuito(self):
        if self.Ia == 0 or self.Va == 0:
            return 0, 0, 0

        a = self.calcular_relacao_transformacao()
        lado_ensaio = "secundario" if self.sec_type == "curto-circuito" else "primario"

        Req = self.Pa / self.Ia ** 2 if self.Ia != 0 else float('inf') #Req = P / I^2 (perdas no cobre), Zcc = V / I
        Zcc = self.Va / self.Ia
        delta = Zcc ** 2 - Req ** 2
        Xeq = math.sqrt(delta) if delta > 0 else 0 # Xeq = sqrt(Zcc^2 - Req^2)

        Req_ref = self.referir_impedancia(Req, a, lado_ensaio, self.referred_to)
        Xeq_ref = self.referir_impedancia(Xeq, a, lado_ensaio, self.referred_to)

        return Req_ref, Xeq_ref, Zcc

 # Divide os parâmetros equivalentes de acordo com o tipo do circuito
    def calcular_parametros_equivalentes(self):
        if self.circuit_type == 'Serie':
            return self.Req, self.Xeq, None, None, None, None
        elif self.circuit_type in ['T', 'L']:
            Rp = self.Req / 2
            Xp = self.Xeq / 2
            Rs = self.Req / 2
            Xs = self.Xeq / 2
            return None, None, Rp, Xp, Rs, Xs
        else:
            return None, None, None, None, None, None

    # Método central para calcular os ensaios e organiza os parâmetros
    def processar_ensaios(self):
        self.Rc, self.Xm, self.Zphi, self.Ic, self.Im = self.calcular_ensaio_circuito_aberto()
        self.Req, self.Xeq, self.Zcc = self.calcular_ensaio_curto_circuito()
        self.ReqTotal_out, self.XeqTotal_out, self.Rp, self.Xp, self.Rs, self.Xs = self.calcular_parametros_equivalentes()

    #Método que gera uma tabela com os dados calculados (encontrados)
    def gerar_relatorio_ensaios(self, nome_arquivo='relatorio_ensaios.html'):
        ensaio_ca_lado = "secundario" if self.sec_type == "circuito-aberto" else "primario"
        ensaio_cc_lado = "secundario" if self.sec_type == "curto-circuito" else "primario"

        # Correntes em mA para exibição
        Ic_mA = self.Ic * 1000
        Im_mA = self.Im * 1000

        html = "<html><head><title>Relatório dos Ensaios</title>"
        html += "<style>table {border-collapse: collapse; width: 60%;} td, th {border: 1px solid black; padding: 6px; text-align: left;}</style>"
        html += "</head><body>"
        html += "<h2>Relatório dos Ensaios do Transformador</h2>"

        # Ensaio de Circuito Aberto
        html += f"<h3>Ensaio de Circuito Aberto (lado {ensaio_ca_lado})</h3>"
        html += "<table>"
        html += "<tr><th>Parâmetro</th><th>Valor</th></tr>"
        html += f"<tr><td>Rc (Ω) — resistência do núcleo (perdas no ferro)</td><td>{self.Rc:.2f}</td></tr>"
        html += f"<tr><td>Xm (Ω) — reatância magnetizante (campo magnético)</td><td>{self.Xm:.2f}</td></tr>"
        html += f"<tr><td>Zφ (Ω) — impedância do circuito aberto</td><td>{self.Zphi:.2f}</td></tr>"
        html += f"<tr><td>Ic (mA) — corrente ativa do núcleo</td><td>{Ic_mA:.2f}</td></tr>"
        html += f"<tr><td>Im (mA) — corrente reativa do núcleo</td><td>{Im_mA:.2f}</td></tr>"
        html += "</table><br>"

        # Ensaio de Curto-Circuito
        html += f"<h3>Ensaio de Curto-Circuito (lado {ensaio_cc_lado})</h3>"
        html += "<table>"
        html += "<tr><th>Parâmetro</th><th>Valor</th></tr>"

        if self.circuit_type == 'Serie':
            html += f"<tr><td>Req Total (Ω) — resistência equivalente total</td><td>{self.ReqTotal_out:.2f}</td></tr>"
            html += f"<tr><td>Xeq Total (Ω) — reatância equivalente total</td><td>{self.XeqTotal_out:.2f}</td></tr>"
        else:
            html += f"<tr><td>Rp (Ω) — resistência do primário</td><td>{self.Rp:.2f}</td></tr>"
            html += f"<tr><td>Xp (Ω) — reatância do primário</td><td>{self.Xp:.2f}</td></tr>"
            html += f"<tr><td>Rs (Ω) — resistência do secundário</td><td>{self.Rs:.2f}</td></tr>"
            html += f"<tr><td>Xs (Ω) — reatância do secundário</td><td>{self.Xs:.2f}</td></tr>"

        html += f"<tr><td>Zcc (Ω) — impedância do curto-circuito</td><td>{self.Zcc:.2f}</td></tr>"
        html += "</table>"

        html += "</body></html>"

        # Salvar arquivo
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Relatório HTML salvo como {nome_arquivo}")
        return nome_arquivo

   # gera o gráfico do diagrama fasorial
    def plotar_diagrama_fasorial(self, nome_arquivo='diagrama_fasorial.html'):
        if self.Ic is None or self.Im is None:
            print("Corrente de excitação inválida ou ausente. Verifique os dados de entrada.")
            return

        Ic = self.Ic
        Im = self.Im

        Iphi = np.sqrt(Ic**2 + Im**2)
        max_val = max(abs(Iphi), abs(Ic), abs(Im))
        fator_ampliacao = 1.2
        escala = 1 / max_val if max_val != 0 else 1

        # Correntes normalizadas
        Ic_n = Ic * escala
        Im_n = Im * escala
        Iphi_n_x = Ic_n
        Iphi_n_y = Im_n

        fig = go.Figure()

        # Vetor de tensão (referência angular apenas)
        fig.add_trace(go.Scatter(x=[0, 0.4], y=[0, 0], mode='lines+text',
                                line=dict(color='orange', width=2, dash='dot'),
                                name='V (referência)',
                                text=["", "V"],
                                textposition="top right"))

        # Ic (ativa)
        fig.add_trace(go.Scatter(x=[0, Ic_n], y=[0, 0], mode='lines+text',
                                line=dict(color='red', width=2),
                                name='Ic (ativa)',
                                text=["", "Ic"],
                                textposition="bottom right"))

        # Im (reativa)
        fig.add_trace(go.Scatter(x=[0, 0], y=[0, Im_n], mode='lines+text',
                                line=dict(color='blue', width=2),
                                name='Im (reativa)',
                                text=["", "Im"],
                                textposition="top left"))

        # Iφ (resultante)
        fig.add_trace(go.Scatter(x=[0, Iphi_n_x], y=[0, Iphi_n_y], mode='lines+text',
                                line=dict(color='green', width=3),
                                name='Iφ (resultante)',
                                text=["", "Iφ"],
                                textposition="top center"))

        # Ângulo φ
        if Iphi != 0:
            cos_phi = Ic / Iphi
            cos_phi = np.clip(cos_phi, -1, 1)
            phi_rad = np.arccos(cos_phi)
            phi_deg = np.degrees(phi_rad)

            # Arco do ângulo φ
            theta = np.linspace(0, phi_rad, 100)
            raio = 0.25
            x_arc = raio * np.cos(theta)
            y_arc = raio * np.sin(theta)

            fig.add_trace(go.Scatter(x=x_arc, y=y_arc, mode='lines',
                                    line=dict(color='purple', dash='dot'),
                                    name='φ'))

            # Texto do ângulo φ
            fig.add_annotation(x=raio * np.cos(phi_rad / 2),
                            y=raio * np.sin(phi_rad / 2),
                            text=f'φ = {phi_deg:.2f}°',
                            showarrow=False,
                            font=dict(color='purple', size=14))

        # Layout final
        fig.update_layout(
            title='Diagrama Fasorial da Corrente de Excitação',
            xaxis_title='Eixo Real (normalizado)',
            yaxis_title='Eixo Imaginário (normalizado)',
            showlegend=True,
            width=700,
            height=600,
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(range=[-fator_ampliacao, fator_ampliacao],
                    zeroline=True, showgrid=True, gridcolor='lightgray',
                    scaleanchor="y", scaleratio=1),
            yaxis=dict(range=[-fator_ampliacao, fator_ampliacao],
                    zeroline=True, showgrid=True, gridcolor='lightgray'),
            plot_bgcolor='white'
        )

        fig.write_html(nome_arquivo)
        print(f"Gráfico salvo como {nome_arquivo}")
        return nome_arquivo

def ler_dados_json(nome_arquivo):
    if not os.path.isfile(nome_arquivo):
        print(f"Arquivo {nome_arquivo} não encontrado. Usando valores padrão.")
        return None
    with open(nome_arquivo, 'r') as f:
        try:
            dados = json.load(f)
            if not dados:
                print("Arquivo JSON vazio. Usando valores padrão.")
                return None
            return dados
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON. Usando valores padrão.")
            return None

def executar_desafio3(arquivo_json):
    try:
        if arquivo_json:
            with open(arquivo_json, 'r') as f:
                dados = json.load(f)
        else:
            dados = None
    except Exception as e:
        return {"erro": f"Erro ao ler arquivo JSON: {e}"}

    # Cria a instância da classe com dados do JSON ou usa valores padrão do __init__
    if dados:
        tf = TransformadorMonofasico(**dados)
    else:
        tf = TransformadorMonofasico()

    # Processa os ensaios e parâmetros
    tf.processar_ensaios()

    # Gera relatório em arquivo HTML e obtém nome do arquivo
    arquivo_relatorio_html = tf.gerar_relatorio_ensaios()

    # Gera o diagrama fasorial, retorna o nome do arquivo HTML gerado
    arquivo_html = tf.plotar_diagrama_fasorial()

    return {
        "relatorio_html": arquivo_relatorio_html,
        "diagrama_html": arquivo_html
    }

'''
if __name__ == "__main__":
    exemplo_fitgerald_2_6 = {
        "N1": 2400,
        "N2": 240,
        "Va": 48,
        "Ia": 20.8,
        "Pa": 617,
        "Vb": 240,
        "Ib": 5.41,
        "Pb": 186,
        "circuit_type": "Serie",
        "referred_to": "secundario",
        "sec_type": "circuito-aberto"
    }

    # SALVA o dicionário como arquivo JSON
    nome_arquivo_json = "exemplo_fitgerald_2_6.json"
    with open(nome_arquivo_json, "w") as f:
        json.dump(exemplo_fitgerald_2_6, f, indent=2)

    # Agora sim, usa o arquivo criado
    resultado = executar_desafio3(nome_arquivo_json)
    print(resultado)
'''