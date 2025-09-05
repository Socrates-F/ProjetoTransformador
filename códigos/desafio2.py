# Importações necessárias para cálculo, manipulação de arquivos e geração de gráficos
import numpy as np                          # Biblioteca para operações com arrays e funções matemáticas
import matplotlib.pyplot as plt             # Biblioteca para geração de gráficos
import pandas as pd                         # Para leitura de arquivos Excel
from scipy.interpolate import interp1d      # Para interpolação linear entre pontos da curva
import json, os, io, base64                 # Utilitários para manipulação de arquivos, entrada/saída e codificação
from pathlib import Path                    # Para lidar com caminhos de arquivos de forma multiplataforma

# Classe que representa o comportamento magnético de um transformador
class TransformadorMagnetico2:
    
    def _carregar_curva_magnetizacao(self, caminho_arquivo=None):
        """
        Carrega o arquivo Excel com a curva de magnetização (MMF vs Fluxo) e 
        cria a função de interpolação para posterior uso.

        MMF (Força MagnetoMotriz) vs Fluxo magnético Φ
        """
        try:
            # Lista de locais padrão onde o arquivo MagCurve.xlsx pode estar localizado
            locais_padrao = [
                "MagCurve.xlsx",
                os.path.join(os.path.dirname(__file__), "MagCurve.xlsx"),
                "../MagCurve.xlsx",
                "data/MagCurve.xlsx"
            ]
            if caminho_arquivo is not None:
                locais_padrao = [caminho_arquivo]  # Usa caminho fornecido, se existir

            # Verifica onde o arquivo realmente existe
            arquivo_encontrado = None
            for local in locais_padrao:
                if Path(local).exists():
                    arquivo_encontrado = local
                    break

            if arquivo_encontrado is None:
                raise FileNotFoundError(f"Arquivo 'MagCurve.xlsx' não encontrado. Procurado em: {locais_padrao}")

            # Lê o conteúdo do arquivo Excel
            df = pd.read_excel(arquivo_encontrado)

            # Verifica se as colunas necessárias estão presentes
            if 'MMF' not in df.columns or 'Fluxo' not in df.columns:
                raise ValueError("Arquivo Excel deve conter colunas 'MMF' e 'Fluxo'")

            # Extrai os dados das colunas
            self.fmm_data = df['MMF'].values     # Força magnetomotriz (FMM), em Ampère-espiras
            self.fluxo_data = df['Fluxo'].values # Fluxo magnético (Φ), em Weber

            # Cria uma função interpoladora: FMM = f(Φ)
            # Interpolação linear entre os pontos medidos, extrapolando quando necessário
            self.fluxo_para_fmm = interp1d(
                self.fluxo_data, self.fmm_data, kind='linear', fill_value="extrapolate"
            )

        except Exception as e:
            raise RuntimeError(f"Erro ao carregar curva de magnetização: {str(e)}")

    def calcular_corrente_magnetizacao(self, vm=None, n=None, freq=None, tempo_max=0.340, passo=1/3000):
        """
        Calcula a corrente de magnetização (Im) ao longo do tempo usando a equação do fluxo magnético.
        
        Fórmulas utilizadas:
        - ω = 2πf  (frequência angular)
        - Φ(t) = -(Vm / (ω * N)) * cos(ωt)   → Lei de Faraday
        - MMF(t) = f(Φ(t))                   → obtido por interpolação dos dados reais
        - Im(t) = MMF(t) / N                 → relação da corrente com a força magnetomotriz
        """
        if vm is None or n is None or freq is None:
            raise ValueError("Parâmetros vm, n e freq devem ser fornecidos")

        self.VM = vm      # Tensão máxima da onda senoidal (V)
        self.N = n        # Número de espiras do enrolamento primário
        self.freq = freq  # Frequência da rede (Hz)

        w = 2 * np.pi * self.freq  # Frequência angular (rad/s)

        # Cria vetor de tempo de 0 até tempo_max com passo definido
        self.t = np.arange(0, tempo_max, passo)

        # Calcula o fluxo magnético Φ(t)
        # Derivada da tensão senoidal -> fluxo = integral da tensão
        # Φ(t) = -(Vm / (w * N)) * cos(wt)
        self.fluxo_t = -self.VM / (w * self.N) * np.cos(w * self.t)

        # Usa interpolação para obter MMF(t) correspondente ao fluxo
        self.fmm_t = self.fluxo_para_fmm(self.fluxo_t)

        # Corrente de magnetização: Im(t) = MMF(t) / N
        self.corrente_t = self.fmm_t / self.N

    def gerar_grafico_base64(self, salvar_png_em='grafico_magnetizacao.png'):
        """
        Gera um gráfico da corrente de magnetização ao longo do tempo e retorna sua versão em base64.
        Também salva o gráfico em arquivo PNG.

        Eixos:
        - x: Tempo (ms)
        - y: Corrente de Magnetização (A)
        """
        if not hasattr(self, 'corrente_t'):
            raise RuntimeError("Execute calcular_corrente_magnetizacao() primeiro")

        # Cria a figura do gráfico
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(self.t * 1000, self.corrente_t, color='blue')  # Tempo em milissegundos
        ax.set_title('Corrente de Magnetização x Tempo')
        ax.set_xlabel('Tempo (ms)')
        ax.set_ylabel('Corrente de Magnetização (A)')
        ax.grid(True)

        # Salva o gráfico como arquivo PNG
        fig.savefig(salvar_png_em)

        # Codifica o gráfico em base64 para uso em HTML ou APIs
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        img_bytes = buffer.read()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        plt.close(fig)  # Fecha o gráfico para liberar memória
        return img_base64

# Função principal que orquestra a execução completa
def executar_desafio2(json_input=None, salvar_grafico_em='grafico_magnetizacao.png'):
    """
    Função principal do desafio.

    Passos:
    1. Lê os parâmetros de entrada (padrão, string JSON, dicionário ou arquivo JSON)
    2. Cria instância do transformador
    3. Carrega curva de magnetização
    4. Calcula a corrente de magnetização
    5. Gera e salva gráfico, retornando-o em base64
    """
    # Parâmetros padrão
    parametros = {
        "VM": 325,           # Tensão de pico (V)
        "N": 850,            # Número de espiras
        "freq": 50,          # Frequência (Hz)
        "tempo_max": 0.340,  # Tempo total da simulação (s)
        "passo": 1/3000      # Passo de tempo (s)
    }

    # Se houver entrada externa, atualiza os parâmetros
    if json_input is not None:
        if isinstance(json_input, str):
            if os.path.exists(json_input):  # Verifica se é um arquivo
                with open(json_input) as f:
                    parametros.update(json.load(f))
            else:
                try:
                    parametros.update(json.loads(json_input))  # Tenta ler como string JSON
                except json.JSONDecodeError:
                    raise ValueError("String JSON inválida ou caminho de arquivo não encontrado")
        elif isinstance(json_input, dict):
            parametros.update(json_input)
        else:
            raise TypeError("Entrada deve ser dict, string JSON ou caminho para arquivo JSON")

    # Cria o objeto do transformador e realiza os cálculos
    transformador = TransformadorMagnetico2()
    transformador._carregar_curva_magnetizacao()

    transformador.calcular_corrente_magnetizacao(
        vm=parametros["VM"],
        n=parametros["N"],
        freq=parametros["freq"],
        tempo_max=parametros["tempo_max"],
        passo=parametros["passo"]
    )

    # Gera o gráfico e retorna imagem em base64
    imagem_base64 = transformador.gerar_grafico_base64(salvar_png_em=salvar_grafico_em)

    return imagem_base64

# Executa diretamente como script se for chamado pelo terminal
if __name__ == "__main__":
    print("Executando com valores padrão...")
    img_base64 = executar_desafio2()
    print("Gráfico gerado com sucesso (valores padrão)")
