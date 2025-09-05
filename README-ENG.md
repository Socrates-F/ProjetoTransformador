# 🔌 Project: Single-Phase Transformers – Calculation and Simulation

## 📖 About the Project
This project was developed as part of the **Electromechanical Energy Conversion course (POLI/UPE)**.  
Its purpose is to implement a computational system for the **calculation, analysis, and simulation of single-phase transformers**.  
The main idea is to transform theoretical concepts into a practical tool that assists in **design, parameter determination, and performance analysis of transformers**.

## 🎯 Objectives
- Apply transformer theory through **computational implementations**.  
- Build an **integrated application (API)** capable of calculating and visualizing:  
  - Constructive design;  
  - Magnetization curve;  
  - Parameters via experimental tests;  
  - Voltage regulation and phasor diagrams.  

## 🛠️ Project Structure
The project was divided into **challenges**, each implemented in a separate Python module:

### 1. `desafio1.py` – **Design**
- Calculates the number of primary (Np) and secondary (Ns) turns.  
- Determines conductor wire gauges (AWG).  
- Selects core lamination type and transformer dimensions.  
- Estimates iron and copper weights.  
- Generates an **interactive 3D visualization** of the transformer.

### 2. `desafio2.py` – **Magnetization Current**
- Loads the B-H curve of the magnetic material.  
- Calculates magnetization current as a function of time.  
- Generates and saves the **Im(t) plot**.  

### 3. `desafio3.py` – **Short-Circuit and Open-Circuit Tests**
- Computes equivalent parameters (Rc, Xm, Req, Xeq).  
- Produces an **HTML report** with results.  
- Builds an **interactive phasor diagram** of excitation currents.

### 4. `desafio4.py` – **Regulation and Operation Diagram**
- Calculates the **percentage voltage regulation** of the transformer.  
- Plots an **interactive phasor diagram** including voltages, currents, and voltage drops.

### 5. `app.py` – **Integration (Flask API)**
- Implements an API that connects all modules.  
- Provides routes to access results and graphical visualizations in HTML/PNG.  

## 🚀 Technologies Used
- **Python 3**  
- **Flask** (API)  
- **Plotly and Matplotlib** (graphical visualization)  
- **Pandas and NumPy** (data handling and calculations)

## 📊 Conclusion
This project bridges theory and practice by enabling:  
- Transformer design;  
- Magnetic behavior simulation;  
- Experimental parameter determination;  
- Performance evaluation via regulation and phasor diagrams.  

It serves as both an **educational and practical tool** for the study and analysis of **single-phase transformers**.
