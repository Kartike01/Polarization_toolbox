# Polarization_toolbox

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen)](#installation)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20MacOS-lightgrey)]()

A Python-based GUI application for processing and visualizing **polarization camera images**.  
The app extracts **Stokes parameters**, **degree of polarization (DoP)**, **orientation angles**, and **ellipticity**, while providing rich interactive visualization and export options.

---

## 📖 Project Description

**Polarization Camera App** is a Python-based GUI tool designed for **polarization image analysis**.  
It allows users to import polarization camera images (single or dual-image mode), process them to extract **Stokes parameters**, **degree of polarization**, **orientation/ellipticity angles**, and other derived quantities.  
The app then generates and saves **heatmaps**, **matrix data files**, and even **interactive plots** for better visualization.  

This tool is tailored for researchers and engineers working with polarization imaging systems — especially useful for optical experiments involving birefringence, scattering, or stress analysis.  

---

## ✨ Features

- **Single & Dual Image Modes**:
  - Single image mode: I₀₀, I₄₅, I₉₀
  - Dual image mode: Adds I₄₅₋₉₀ and Stokes S₃

- **Stokes Parameter Computation**:
  - S₀, S₁, S₂, S₃

- **Derived Parameters**:
  - Degree of Polarization (DoP)
  - Orientation Angle (OA)
  - Ellipticity Angle (EA)
  - Phase Difference (PD)
  - Amplitude components (Ex, Ey)

- **Visualization**:
  - Static PNG heatmaps for each parameter
  - Interactive Plotly heatmaps
  - Polarization ellipse plotting
  - Combined I-parameter subplots

- **Data Export**:
  - Saves each matrix as `.txt`
  - Exports all matrices into a single `.xlsx` file

---

## 🖼 Example Workflow

1. **Process Images**
   - Click **"Process Images"**.
   - Choose between:
     - **Yes** → Upload both main and 90° images.
     - **No** → Upload only the main image.

2. **View Results**
   - Select a parameter from the dropdown.
   - Click **"Display Image"** to preview the heatmap.
   - Click **"Show Interactive Plot"** for zoomable view.
   - Click **"Show Matrix"** to open the data in Excel.
   - (Dual mode) Click **"Show Interactive Ellipses"** to view ellipse plots.

3. **Access Saved Data**
   - All results saved inside `/outputs/<image_name>/`
   - Includes:
     - `.png` heatmaps
     - `.txt` matrix files
     - `matrices.xlsx` (Excel)
     - Ellipse plots (if applicable)

---

## 📂 Output Directory Structure
outputs/
└── sample_image/
├── I_00.png
├── I_00.txt
├── S0.png
├── S0.txt
├── ...
├── Ellipses.png
├── Ellipses.txt
└── matrices.xlsx


##Libraries used
- numpy
- opencv-python
- pandas
- Pillow
- plotly
- matplotlib
- tkhtmlview
- openpyxl

