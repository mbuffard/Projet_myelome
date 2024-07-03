import pandas as pd
import streamlit as st

file="../../data/depmap/dependencies enriched in multiple_myeloma.csv"

df=pd.read_csv(file)
df=df[df['Type'] != 'compound']
print(df['Dataset'].unique())



# Titre de l'application
st.title('Analyse des dépendances enrichies dans le myélome multiple')

# Ajout d'un bouton pour charger un fichier
uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")

# Vérifiez si un fichier a été téléchargé
if uploaded_file is not None:
    # Lire le contenu du fichier téléchargé
    f = uploaded_file.getvalue().decode('utf-8').splitlines()
    
    # Vérifier que le fichier contient bien un mot par ligne
    valid_file = True
    for line_number, line in enumerate(f, start=1):
        if len(line.split()) > 1: 
            st.write(f"Erreur à la ligne {line_number}: Les lignes doivent contenir un seul gène.")
            valid_file = False
    
    # Si le fichier est valide, le lire dans un DataFrame pandas
    if valid_file:
        #Aller chercher les lignes dans df dont la colonne 'Gene/Compound' est egal à un gene du fichier chargé
        for line in f:
            st.write(df[df['Gene/Compound']==line].style.format({'P-Value':'{:.2e}'})) 
            #test the value of "T-statistic" and "P-value" and display a message if the p-value is less than 0.05
            


else:
    st.write("Veuillez télécharger un fichier CSV.")