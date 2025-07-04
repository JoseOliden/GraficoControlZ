import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
import ipywidgets as widgets
from google.colab import files
from IPython.display import clear_output

# Subir archivo de datos
print("Sube el archivo de datos (muestras):")
uploaded = files.upload()
filename_datos = list(uploaded.keys())[0]
df_datos = pd.read_excel(filename_datos) if filename_datos.endswith('.xlsx') else pd.read_csv(filename_datos)

# Subir archivo de referencias
print("Sube el archivo de referencias:")
uploaded_ref = files.upload()
filename_ref = list(uploaded_ref.keys())[0]
df_ref = pd.read_excel(filename_ref) if filename_ref.endswith('.xlsx') else pd.read_csv(filename_ref)

# Verificar estructura
print("\nDatos cargados:")
display(df_datos.head())
print("\nReferencias cargadas:")
display(df_ref)

# Obtener lista de elementos
columnas = [col for col in df_datos.columns if not col.startswith("u_") and col != "Muestra"]

# Crear selector
elemento_dropdown = widgets.Dropdown(options=columnas, description='Elemento:')
boton_graficar = widgets.Button(description="Graficar Z")

display(elemento_dropdown, boton_graficar)

def graficar_z_multiref(b):

    clear_output(wait=True)  # Limpiar antes de graficar
    display(elemento_dropdown, boton_graficar)


    elemento = elemento_dropdown.value
    u_col = f"u_{elemento}"

    if u_col not in df_datos.columns:
        print(f"No se encontró la columna '{u_col}'")
        return

    muestras = df_datos["Muestra"]
    x = df_datos[elemento]
    u_x = df_datos[u_col]

    # Crear listas para los valores de referencia y sus incertidumbres por muestra
    mu_list = []
    u_mu_list = []

    for muestra in muestras:
        fila_ref = df_ref[df_ref["Muestra"] == muestra]
        if fila_ref.empty:
            print(f"No se encontró referencia para la muestra '{muestra}'")
            mu_list.append(np.nan)
            u_mu_list.append(np.nan)
        else:
            mu_list.append(float(fila_ref[elemento].values[0]))
            u_mu_list.append(float(fila_ref[u_col].values[0]))

    mu_arr = np.array(mu_list)
    u_mu_arr = np.array(u_mu_list)

    # Calcular Z-score
    z = (x - mu_arr) / np.sqrt(u_x**2 + u_mu_arr**2)

    # Graficar
    plt.figure(figsize=(10, 5))
    plt.plot(muestras, z, marker='o', linestyle='-', color='blue', label='Z')
    plt.axhline(0, color='black', linestyle='--')
    plt.axhline(2, color='orange', linestyle='--', label='±2')
    plt.axhline(-2, color='orange', linestyle='--')
    plt.axhline(3, color='red', linestyle='--', label='±3')
    plt.axhline(-3, color='red', linestyle='--')
    plt.xticks(rotation=45)
    plt.xlabel("Muestra")
    plt.ylabel("Z")
    plt.title(f"Z-score para {elemento} con múltiples valores de referencia")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Conectar el botón
boton_graficar.on_click(graficar_z_multiref)
