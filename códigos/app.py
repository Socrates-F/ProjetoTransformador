import json
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from desafio1 import TransformadorMonofasico1
from desafio2 import executar_desafio2
from desafio3 import executar_desafio3
from desafio4 import executar_desafio4


app = Flask(__name__)
CORS(app)  # Permite requisições de outros domínios

@app.route('/mensagem', methods=['POST'])
def mensagem():
    dados = request.get_json()
    classe = dados.get('classe')
    parametros = dados.get('parametros', '')

    resposta = calcular(classe, parametros)
    return jsonify({'resposta': resposta})


def calcular(classe, parametros):
    arquivo = 'dados.json'

    with open(arquivo, 'w') as f:
        json.dump(parametros, f)

    if classe == 'desafio1':
        transformador1 = TransformadorMonofasico1()
        return transformador1.executar_desafio1(arquivo)
    elif classe == 'desafio2':
        return executar_desafio2(arquivo)
    elif classe == 'desafio3':
        return executar_desafio3(arquivo)
    elif classe == 'desafio4':
        return executar_desafio4(arquivo)
    else:
        return "Parametros invalidos!!"
    
#desafio1
@app.route('/transformador_3d')
def visualizar_3d():
    return send_from_directory(directory=os.getcwd(), path='transformador_3d_interativo.html')

#desafio2
@app.route('/grafico_magnetizacao')
def visualizar_grafico_magnetizacao():
    return send_from_directory(directory=os.getcwd(), path='grafico_magnetizacao.png')

#desafio3
@app.route('/relatorio')
def visualizar_relatorio_ensaios():
    return send_from_directory(directory=os.getcwd(), path='relatorio_ensaios.html')

@app.route('/caracteristica_fasorial')
def visualizar_caracteristica_fasorial():
    return send_from_directory(directory=os.getcwd(), path='caracteristica_fasorial.html')

#desafio4
@app.route('/diagrama_fasorial')
def visualizar_diagrama_fasorial():
    return send_from_directory(directory=os.getcwd(), path='diagrama_fasorial.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
