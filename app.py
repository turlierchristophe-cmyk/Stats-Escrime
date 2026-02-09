import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuration de la page
st.set_page_config(
    page_title="Analyse Escrime",
    page_icon="⚔️",
    layout="wide"
)

# Chargement des données
@st.cache_data
def charger_donnees():
    df = pd.read_excel('Résultats_Escrime_V5_2.xlsm', sheet_name='Data_matchs')
    return df

df = charger_donnees()

# Menu de navigation
page = st.sidebar.radio("Navigation", ["Consultation Data_matchs", "Analyse Escrimeur"])

# ===== PAGE 1: CONSULTATION DATA_MATCHS =====
if page == "Consultation Data_matchs":
    st.title("⚔️ Consultation Data_matchs")

    # Formater le nombre sans séparateur de milliers
    st.info(f"**{len(df)} matchs** dans la base de données")

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
    st.subheader(f"📊 Résultats : {len(df_filtre)} matchs")

    # Convertir Date en format français JJ/MM/AAAA
    df_affichage = df_filtre.copy()
    df_affichage['Date'] = df_affichage['Date'].dt.strftime('%d/%m/%Y')

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

# ===== PAGE 2: ANALYSE ESCRIMEUR =====
else:
    st.title("📊 Analyse Escrimeur")
    
    # Récupérer tous les tireurs et les trier par ordre alphabétique
    tireurs_liste = sorted(set(df['Tireur 1'].unique()) | set(df['Tireur 2'].unique()))
    
    # Filtres en haut
    col1, col2 = st.columns([2, 1])
    
    with col1:
        escrimeur = st.selectbox("Sélectionner un escrimeur", tireurs_liste)
    
    with col2:
        # Filtre années
        annees = sorted(df['Date'].dt.year.unique())
        annee_min, annee_max = st.select_slider(
            "Plage d'années",
            options=annees,
            value=(min(annees), max(annees))
        )
    
    # Filtrer les données pour l'escrimeur sélectionné et la plage d'années
    df_escrimeur = df[
        ((df['Tireur 1'] == escrimeur) | (df['Tireur 2'] == escrimeur)) &
        (df['Date'].dt.year >= annee_min) &
        (df['Date'].dt.year <= annee_max)
    ].copy()
    
    # Filtrer uniquement les matchs de poule
    df_poules = df_escrimeur[df_escrimeur['Poule / Tableau'].str.startswith('Poule', na=False)].copy()
    
    # Déterminer le score de l'escrimeur pour chaque match
    def obtenir_score_escrimeur(row):
        if row['Tireur 1'] == escrimeur:
            return row['Touches Tireur 1']
        else:
            return row['Touches Tireur 2']
    
    df_poules['Score Escrimeur'] = df_poules.apply(obtenir_score_escrimeur, axis=1)
    
    # Calculer victoires et défaites
    victoires = len(df_poules[df_poules['Score Escrimeur'] == 5])
    defaites = len(df_poules[df_poules['Score Escrimeur'] < 5])
    total_matchs = victoires + defaites
    
    # Afficher le graphique camembert
    st.markdown("---")
    st.subheader(f"Matchs de Poule - {escrimeur}")
    st.info(f"**{total_matchs} matchs de poule** sur la période sélectionnée")
    
    if total_matchs > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['Victoires', 'Défaites'],
            values=[victoires, defaites],
            hole=0.3,
            marker_colors=['#2ecc71', '#e74c3c']
        )])
        
        fig.update_layout(
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Afficher les statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Victoires", victoires)
        with col2:
            st.metric("Défaites", defaites)
        with col3:
            taux_victoire = (victoires / total_matchs * 100) if total_matchs > 0 else 0
            st.metric("Taux de victoire", f"{taux_victoire:.1f}%")
    else:
        st.warning("Aucun match de poule trouvé pour cet escrimeur sur cette période.")
