import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Z-score con incertidumbre", layout="wide")

st.title("📊 Diagrama de Control - Z-score con Incertidumbre Combinada")

# Cargar archivos
datos_file = st.file_uploader("📥 Carga el archivo de datos (muestras)", type=["csv", "xlsx"])
ref_file = st.file_uploader("📥 Carga el archivo de referencia (valores certificados)", type=["csv", "xlsx"])

if datos_file and ref_file:
    # Leer archivos
    df_datos = pd.read_excel(datos_file) if datos_file.name.endswith('xlsx') else pd.read_csv(datos_file)
    df_ref = pd.read_excel(ref_file) if ref_file.name.endswith('xlsx') else pd.read_csv(ref_file)

    # Selección de elemento
    columnas_elementos = [col for col in df_datos.columns if not col.startswith("u_") and col != "Muestra"]
    elemento = st.selectbox("🧪 Selecciona el elemento a graficar:", columnas_elementos)

    if elemento:
        u_col = f"u_{elemento}"

        if u_col not in df_datos.columns or u_col not in df_ref.columns:
            st.error(f"No se encontró la columna de incertidumbre: '{u_col}' en ambos archivos.")
        else:
            # Extraer datos
            muestras = df_datos["Muestra"]
            x = df_datos[elemento]
            u_x = df_datos[u_col]

            # Buscar referencias por muestra
            mu = []
            u_mu = []

            for muestra in muestras:
                ref = df_ref[df_ref["Muestra"] == muestra]
                if not ref.empty:
                    mu.append(ref[elemento].values[0])
                    u_mu.append(ref[u_col].values[0])
                else:
                    mu.append(np.nan)
                    u_mu.append(np.nan)

            mu = np.array(mu, dtype='float64')
            u_mu = np.array(u_mu, dtype='float64')

            # Calcular Z-score
            z = (x - mu) / np.sqrt(u_x**2 + u_mu**2)

            # Mostrar tabla de resultados
            resultado = pd.DataFrame({
                "Muestra": muestras,
                f"{elemento}": x,
                f"u_{elemento}": u_x,
                "Valor_ref": mu,
                "u_ref": u_mu,
                "Z-score": z
            })

            st.dataframe(resultado)

            # Gráfico
            st.subheader("📈 Gráfico del Z-score")
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.plot(muestras, z, marker='o', linestyle='-', color='blue', label='Z')
            ax.axhline(0, color='black', linestyle='--')
            ax.axhline(2, color='orange', linestyle='--', label='±2')
            ax.axhline(-2, color='orange', linestyle='--')
            ax.axhline(3, color='red', linestyle='--', label='±3')
            ax.axhline(-3, color='red', linestyle='--')
            ax.set_xlabel("Muestra")
            ax.set_ylabel("Z-score")
            ax.set_title(f"Z-score para {elemento}")
            ax.set_xticks(np.arange(len(muestras)))
            ax.set_xticklabels(muestras, rotation=45)
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
