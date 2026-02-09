import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="Consultation Data_matchs",
    page_icon="⚔️",
    layout="wide"
)

st.title("⚔️ Consultation Data_matchs")

# Chargement des données
@st.cache_data
def charger_donnees():
    df = pd.read_excel('Résultats_Escrime_V5_2.xlsm', sheet_name='Data_matchs')
    return df

df = charger_donnees()

st.info(f"**{len(df):,} matchs** dans la base de données")

# Section des filtres
st.subheader("🔍 Filtres")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Filtre Date
    dates_uniques = sorted(df['Date'].dt.date.unique())
    date_min = st.date_input(
        "Date minimum",
        value=min(dates_uniques),
        min_value=min(dates_uniques),
        max_value=max(dates_uniques)
    )
    date_max = st.date_input(
        "Date maximum",
        value=max(dates_uniques),
        min_value=min(dates_uniques),
        max_value=max(dates_uniques)
    )

with col2:
    # Filtre Compétition
    competitions = ['Toutes'] + sorted(df['Compétition'].unique().tolist())
    competition_filtre = st.multiselect('Compétition', competitions, default=['Toutes'])

with col3:
    # Filtre CN / CdF
    types = ['Tous'] + sorted(df['CN / CdF'].dropna().unique().tolist())
    type_filtre = st.multiselect('CN / CdF', types, default=['Tous'])

with col4:
    # Filtre Catégorie
    categories = ['Toutes'] + sorted(df['Catégorie'].unique().tolist())
    categorie_filtre = st.multiselect('Catégorie', categories, default=['Toutes'])

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Filtre Poule / Tableau
    phases = ['Toutes'] + sorted(df['Poule / Tableau'].dropna().unique().tolist())
    phase_filtre = st.multiselect('Poule / Tableau', phases, default=['Toutes'])

with col2:
    # Filtre Tireur
    tireurs = sorted(set(df['Tireur 1'].unique()) | set(df['Tireur 2'].unique()))
    tireur_filtre = st.multiselect('Tireur (n\'importe lequel)', ['Tous'] + tireurs, default=['Tous'])

with col3:
    # Filtre Saison
    saisons = sorted(df['Saison'].unique().tolist())
    saison_filtre = st.multiselect('Saison', ['Toutes'] + saisons, default=['Toutes'])

with col4:
    # Filtre Vainqueur
    vainqueurs = ['Tous'] + sorted(df['Vainqueur'].dropna().unique().tolist())
    vainqueur_filtre = st.multiselect('Vainqueur', vainqueurs, default=['Tous'])

# Application des filtres
df_filtre = df.copy()

# Filtre Date
df_filtre = df_filtre[
    (df_filtre['Date'].dt.date >= date_min) & 
    (df_filtre['Date'].dt.date <= date_max)
]

# Filtre Compétition
if 'Toutes' not in competition_filtre and len(competition_filtre) > 0:
    df_filtre = df_filtre[df_filtre['Compétition'].isin(competition_filtre)]

# Filtre CN / CdF
if 'Tous' not in type_filtre and len(type_filtre) > 0:
    df_filtre = df_filtre[df_filtre['CN / CdF'].isin(type_filtre)]

# Filtre Catégorie
if 'Toutes' not in categorie_filtre and len(categorie_filtre) > 0:
    df_filtre = df_filtre[df_filtre['Catégorie'].isin(categorie_filtre)]

# Filtre Poule / Tableau
if 'Toutes' not in phase_filtre and len(phase_filtre) > 0:
    df_filtre = df_filtre[df_filtre['Poule / Tableau'].isin(phase_filtre)]

# Filtre Tireur
if 'Tous' not in tireur_filtre and len(tireur_filtre) > 0:
    df_filtre = df_filtre[
        (df_filtre['Tireur 1'].isin(tireur_filtre)) | 
        (df_filtre['Tireur 2'].isin(tireur_filtre))
    ]

# Filtre Saison
if 'Toutes' not in saison_filtre and len(saison_filtre) > 0:
    df_filtre = df_filtre[df_filtre['Saison'].isin(saison_filtre)]

# Filtre Vainqueur
if 'Tous' not in vainqueur_filtre and len(vainqueur_filtre) > 0:
    df_filtre = df_filtre[df_filtre['Vainqueur'].isin(vainqueur_filtre)]

# Affichage des résultats
st.markdown("---")
st.subheader(f"📊 Résultats : {len(df_filtre):,} matchs")

# Convertir Date en format lisible pour l'affichage
df_affichage = df_filtre.copy()
df_affichage['Date'] = df_affichage['Date'].dt.strftime('%Y-%m-%d')

# Afficher le dataframe avec toutes les colonnes dans l'ordre original
st.dataframe(
    df_affichage,
    use_container_width=True,
    hide_index=True,
    height=600
)

# Bouton export CSV
csv = df_affichage.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 Télécharger les résultats (CSV)",
    data=csv,
    file_name="data_matchs_filtre.csv",
    mime="text/csv"
)
