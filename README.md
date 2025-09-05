# 🔌 Projeto: Transformadores Monofásicos – Cálculo e Simulação

## 📖 Sobre o Projeto
Este projeto foi desenvolvido como parte da disciplina **Conversão Eletromecânica de Energia (POLI/UPE)**, com o objetivo de implementar um sistema computacional para **cálculo, análise e simulação de transformadores monofásicos**.  
A ideia central foi transformar conceitos teóricos em uma aplicação prática que auxilia no **dimensionamento, determinação de parâmetros e estudo do desempenho dos transformadores**.

## 🎯 Objetivos
- Aplicar os conceitos teóricos de **transformadores** através de **códigos computacionais**.  
- Criar uma **aplicação integrada (API)** que permita calcular e visualizar:  
  - Dimensionamento construtivo;  
  - Curva de magnetização;  
  - Parâmetros via ensaios experimentais;  
  - Regulação e diagramas fasoriais.  

## 🛠️ Estrutura do Projeto
O projeto foi dividido em **desafios**, cada um implementado em um módulo Python separado:

### 1. `desafio1.py` – **Dimensionamento**
- Calcula o número de espiras no primário (Np) e secundário (Ns).  
- Determina as bitolas dos condutores (AWG).  
- Seleciona o tipo de lâmina do núcleo e dimensões do transformador.  
- Calcula os pesos de ferro e cobre.  
- Gera **visualização 3D interativa** do transformador.

### 2. `desafio2.py` – **Corrente de Magnetização**
- Lê a curva B-H do material magnético.  
- Calcula a corrente de magnetização em função do tempo.  
- Gera e salva o **gráfico Im(t)**.  

### 3. `desafio3.py` – **Ensaios de Curto-Circuito e Circuito Aberto**
- Determina parâmetros equivalentes (Rc, Xm, Req, Xeq).  
- Gera um **relatório em HTML** com os resultados.  
- Cria um **diagrama fasorial interativo** mostrando as componentes de corrente.

### 4. `desafio4.py` – **Regulação e Diagrama de Operação**
- Calcula a **regulação percentual** do transformador.  
- Plota um **diagrama fasorial interativo** incluindo tensões, correntes e quedas de tensão.

### 5. `app.py` – **Integração (API Flask)**
- Implementa uma API que conecta todos os módulos anteriores.  
- Disponibiliza rotas para acessar resultados e visualizações gráficas em HTML/PNG.  

## 🚀 Tecnologias Utilizadas
- **Python 3**  
- **Flask** (API)  
- **Plotly e Matplotlib** (visualizações gráficas)  
- **Pandas e NumPy** (cálculos e manipulação de dados)

## 📊 Conclusão
Este projeto unifica teoria e prática, permitindo:  
- Dimensionar transformadores;  
- Simular comportamento magnético;  
- Determinar parâmetros experimentais;  
- Avaliar desempenho por regulação e diagramas fasoriais.  

Assim, trata-se de uma ferramenta educacional e prática para estudo e análise de **transformadores monofásicos**.
