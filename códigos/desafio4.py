# Bibliotecas necessárias
import numpy as np
import cmath  # Para lidar com números complexos (fasores)
import plotly.graph_objects as go  # Para gráficos interativos
import json
from pathlib import Path

# Lê os parâmetros do transformador a partir de um arquivo JSON
def ler_parametros_json(caminho_arquivo='parametros_transformador.json'):
    """
    Lê os parâmetros do transformador e da carga de um arquivo JSON.
    """
    try:
        with open(caminho_arquivo, 'r') as f:
            parametros = json.load(f)
        return parametros
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Arquivo '{caminho_arquivo}' mal formatado.")
        return None

# Calcula os fasores e plota o diagrama interativo
def calcular_e_plotar_interativo(parametros):
    """
    Cria um diagrama fasorial interativo com base nos parâmetros fornecidos.
    """

    # Extrai os parâmetros do dicionário
    V2 = parametros['V2']           # Tensão no secundário
    I2 = parametros['I2']           # Corrente no secundário
    R_eq = parametros['R_eq']       # Resistência equivalente
    X_eq = parametros['X_eq']       # Reatância equivalente
    cos_phi = parametros['cos_phi'] # Fator de potência
    tipo_fp = parametros['tipo_fp'] # Tipo de fator de potência: 'atrasado' ou 'adiantado'

    # Determina o ângulo de fase em radianos
    phi = np.arccos(cos_phi)
    if tipo_fp == 'adiantado':
        angulo_corrente = phi  # Inverte sinal do ângulo se FP for adiantado
    else:
        angulo_corrente = -phi
    # Calcula os fasores em coordenadas retangulares (complexas)
    V2_fasor = cmath.rect(V2, 0)             # Tensão da carga como vetor real
    I2_fasor = cmath.rect(I2, angulo_corrente)           # Corrente com ângulo phi
    Z_eq = R_eq + 1j * X_eq                  # Impedância equivalente
    V_drop = I2_fasor * Z_eq                 # Queda de tensão no transformador
    V20_fasor = V2_fasor + V_drop            # Tensão a vazio (com a carga desligada)
    V20 = abs(V20_fasor)                     # Módulo da tensão a vazio

    # Cálculo da regulação percentual
    regulacao = ((V20 - V2) / V2) * 100

    # Cria gráfico com Plotly
    fig = go.Figure()

    # Função auxiliar para adicionar vetores ao gráfico
    def add_vector(fig, origin, vector, name, color):
        x_end = origin[0] + vector.real
        y_end = origin[1] + vector.imag

        # Adiciona o vetor como uma linha com marcador
        fig.add_trace(
            go.Scatter(
                x=[origin[0], x_end],
                y=[origin[1], y_end],
                mode="lines+markers",
                name=name,
                line=dict(color=color, width=3),
                marker=dict(symbol="arrow-up", size=10, angleref="previous"),
                hovertemplate=f"<b>{name}</b><br>Magnitude: {abs(vector):.1f} V<br>Ângulo: {np.degrees(cmath.phase(vector)):.1f}°",
                showlegend=True
            )
        )

        # Anotação de texto sobre o vetor
        fig.add_annotation(
            x=(origin[0] + x_end) / 2,
            y=(origin[1] + y_end) / 2,
            text=name,
            showarrow=False,
            font=dict(size=12, color=color),
            xanchor="center",
            yanchor="middle",
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor=color
        )

    # Adiciona os vetores fasoriais relevantes ao gráfico
    add_vector(fig, [0, 0], V2_fasor, "V₂ (Carga)", "blue")  # Tensão da carga
    add_vector(fig, [0, 0], I2_fasor * (V2 / (3 * I2)), "I₂", "green")  # Corrente (escalada)
    add_vector(fig, [V2_fasor.real, V2_fasor.imag], I2_fasor * R_eq, "I₂Rₑq", "red")  # Queda resistiva
    add_vector(fig,
               [V2_fasor.real + (I2_fasor * R_eq).real, V2_fasor.imag + (I2_fasor * R_eq).imag],
               I2_fasor * 1j * X_eq, "I₂Xₑq", "purple")  # Queda reativa
    add_vector(fig, [0, 0], V20_fasor, "V₂₀ (Vazio)", "cyan")  # Tensão a vazio

    # Configurações visuais do gráfico
    fig.update_layout(
        title=f"Diagrama Fasorial Interativo - FP {cos_phi} {tipo_fp}<br>Regulação: {regulacao:.2f}%",
        xaxis_title="Componente Real (V)",
        yaxis_title="Componente Imaginária (V)",
        template="plotly_white",
        hovermode="closest",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.5)"
        ),
        margin=dict(l=50, r=50, b=50, t=100),
        width=900,
        height=800
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)  # Escala igual nos eixos X e Y

    return regulacao, fig

# Gera um JSON de exemplo se ele não existir ainda
def gerar_arquivo_json_exemplo(caminho='parametros_transformador.json'):
    """Gera um arquivo JSON de exemplo se não existir"""
    if True:
        dados_exemplo = {
        "V2": 2400,
        "I2": 20.8,
        "R_eq": 1.42,
        "X_eq": 1.82,
        "cos_phi": 0.80,
        "tipo_fp": "adiantado"
        }
        with open(caminho, 'w') as f:
            json.dump(dados_exemplo, f, indent=4)
        print(f"Arquivo de exemplo criado: {caminho}")

# Executa todas as etapas do desafio 4
def executar_desafio4(caminho_json='parametros_transformador.json'):
    """
    Função principal que executa todo o fluxo do desafio 4.
    """
    # Garante que o arquivo JSON de exemplo existe
    gerar_arquivo_json_exemplo(caminho_json)

    # Lê os parâmetros do arquivo
    parametros = ler_parametros_json(caminho_json)
    if parametros is None:
        return None

    # Realiza cálculos e gera o gráfico
    try:
        regulacao, fig = calcular_e_plotar_interativo(parametros)

        # Mostra os resultados no terminal
        print("\nResultados:")
        print(f"- Tensão secundário (V2): {parametros['V2']} V")
        print(f"- Corrente secundário (I2): {parametros['I2']} A")
        print(f"- Fator de potência: {parametros['cos_phi']} {parametros['tipo_fp']}")
        print(f"\nRegulação calculada: {regulacao:.2f}%")

        # Salva o gráfico em um arquivo HTML
        caminho_html = "diagrama_fasorial.html"
        fig.write_html(caminho_html)
        print(f"Gráfico salvo em: {caminho_html}")

        return regulacao, caminho_html
    except Exception as e:
        print(f"Erro durante os cálculos: {str(e)}")
        return None

# Execução direta se o script for executado como principal
if __name__ == "__main__":
    # Executa o desafio completo
    resultado = executar_desafio4()

    # Para testar outro JSON, descomente a linha abaixo e informe o caminho
    # resultado = executar_desafio4('outro_arquivo.json')
