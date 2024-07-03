import streamlit as st
import pandas as pd
import re
from difflib import SequenceMatcher
from Bio import Entrez
from Bio import Medline

# Chemin vers le fichier de données
FILE = "../../data/druggable_targets/TTD_DB/P1-01-TTD_target_download_test.txt"

# Fonction pour rechercher les informations du gène
def search_gene(gene_name, exact_match):
    """
    Searches for gene information in a file based on a given gene name.

    Parameters:
        gene_name (str): The name of the gene to search for.
        exact_match (bool): Whether to search for an exact match of the gene name.

    Returns:
        list or str: A list of target information if a match is found, or a string indicating no results were found.

    Raises:
        FileNotFoundError: If the file specified by FILE does not exist.
    """
    try:
        # Lire le fichier
        with open(FILE, 'r') as f:
            lines = f.readlines()
        
        results = []
        if exact_match:
            gene_pattern = re.compile(rf"GENENAME\t.*{gene_name}$")

            # Rechercher les lignes contenant le nom de gène exact avec un préfixe ou suffixe quelconque
            for line in lines:
                if gene_pattern.search(line):
                    identifier = line.split('\t')[0]
                    target_info = [l.strip() for l in lines if l.startswith(identifier) and not ("SEQUENCE" in l or "FUNCTION" in l or "SYNONYMS" in l or "PDBSTRUC" in l or "BIOCLASS" in l or "ECNUMBER" in l)]
                    results.append(target_info)
        else:
            for line in lines:
                if "GENENAME" in line and len(line.split('\t')) > 2:
                    seq = SequenceMatcher(None, gene_name, line.split('\t')[2])
                    if seq.ratio() > 0.6:
                        identifier = line.split('\t')[0]
                        target_info = [l.strip() for l in lines if l.startswith(identifier) and not ("SEQUENCE" in l or "FUNCTION" in l or "SYNONYMS" in l or "PDBSTRUC" in l or "BIOCLASS" in l or "ECNUMBER" in l)]
                        results.append(target_info)

        if not results:
            return "Aucun résultat trouvé pour le gène fourni."
        
        return results
    except FileNotFoundError:
        return f"Le fichier {FILE} n'existe pas."

# Interface Streamlit
st.title('Recherche de gène')

# Champ de texte pour le nom du gène
gene_name = st.text_input('Entrez le nom du gène:')

# Case à cocher pour la recherche exacte
exact_match = st.checkbox("Recherche du terme exact (sensible à la casse, permet la présence d'autres termes)", value=True)

# Si une recherche a été effectuée, stocker les résultats dans session_state
if 'results' not in st.session_state:
    st.session_state.results = []

if 'clicked_buttons' not in st.session_state:
    st.session_state.clicked_buttons = {}

# Bouton pour lancer la recherche
if st.button('Rechercher'):
    if gene_name:
        st.session_state.results = search_gene(gene_name, exact_match)
        st.session_state.clicked_buttons = {}  # Réinitialiser les boutons cliqués lors d'une nouvelle recherche
        for key in list(st.session_state.keys()):
            if key.startswith("details_"):
                del st.session_state[key]  # Réinitialiser l'affichage des détails

# Afficher les résultats de la recherche
if isinstance(st.session_state.results, str):
    st.write(st.session_state.results)
else:
    for idx, target_info in enumerate(st.session_state.results):
        st.write(f"Target {idx + 1}:")

        drug_info_data = []

        for info in target_info:
            info_tab = info.split('\t')
            if info_tab[1] != "DRUGINFO":
                st.write(' '.join(info_tab[1:]))
            else:
                drug_info_data.append(info_tab[2:])

        if drug_info_data:
            df = pd.DataFrame(drug_info_data, columns=['Drug ID', 'Drug Name', 'Highest Clinical Status'])
            st.write("Drug Information:")

            # Afficher les en-têtes de colonnes
            cols = st.columns((1, 2, 2, 1, 2))
            cols[0].write("Drug ID")
            cols[1].write("Drug Name")
            cols[2].write("Highest Clinical Status")
            cols[3].write("Search")
            cols[4].write("Details")

            # Créer une table customisée avec les boutons à droite
            for i, row in df.iterrows():
                cols = st.columns((1, 2, 2, 1, 2))
                cols[0].write(row['Drug ID'])
                cols[1].write(row['Drug Name'])
                cols[2].write(row['Highest Clinical Status'])
                button_key = f"button_{idx}_{i}"
                if cols[3].button('Pubmed', key=button_key, help="Click to fetch PubMed information"):
                    st.session_state.clicked_buttons[button_key] = not st.session_state.clicked_buttons.get(button_key, False)

                # Réinitialiser l'affichage des détails à droite
                if f"details_{button_key}" not in st.session_state:
                    st.session_state[f"details_{button_key}"] = ""

                if st.session_state.clicked_buttons.get(button_key, False):
                    MAX_COUNT = 10
                    TERM = row['Drug Name'] + ' myeloma'
                    Entrez.email = 'marion.buffard@umontpellier.fr'
                    h = Entrez.esearch(db='pubmed', term=TERM)
                    result = Entrez.read(h)
                    publi_count = int(result['Count'])
                    st.session_state[f"details_{button_key}"] = f"Cette drogue est associée au myélome dans {publi_count} publications."

                # Afficher les détails à droite
                cols[4].write(st.session_state[f"details_{button_key}"])
