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

# Navigation en haut avec boutons
st.markdown("### Navigation")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📊 Matchs", use_container_width=True, type="primary"):
        st.session_state.page = "matchs"
with col2:
    if st.button("🏆 Résultats", use_container_width=True):
        st.session_state.page = "resultats"
with col3:
    if st.button("📋 Tous les matchs", use_container_width=True):
        st.session_state.page = "consultation"

# Initialiser la page par défaut
if 'page' not in st.session_state:
    st.session_state.page = "matchs"

st.markdown("---")

# ===== PAGE 1: CONSULTATION DATA_MATCHS =====
if st.session_state.page == "consultation":
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

# ===== PAGE 2: MATCHS =====
elif st.session_state.page == "matchs":
    st.title("📊 Matchs")
    
    # Récupérer tous les tireurs et les trier par ordre alphabétique
    tireurs_liste = sorted(set(df['Tireur 1'].unique()) | set(df['Tireur 2'].unique()))
    
    # Filtres en haut
    col1, col2 = st.columns([2, 1])
    
    with col1:
        escrimeur = st.selectbox("Sélectionner un escrimeur", tireurs_liste)
    
    with col2:
        # Filtre saisons (au lieu d'années)
        saisons = sorted([s for s in df['Saison'].unique() if s != 2021])  # Exclure 2021
        saison_min, saison_max = st.select_slider(
            "Plage de saisons",
            options=saisons,
            value=(min(saisons), max(saisons))
        )
    
    # Filtrer les données pour l'escrimeur sélectionné et la plage de saisons
    df_escrimeur = df[
        ((df['Tireur 1'] == escrimeur) | (df['Tireur 2'] == escrimeur)) &
        (df['Saison'] >= saison_min) &
        (df['Saison'] <= saison_max)
    ].copy()
    
    # Fonction pour obtenir score et touches de l'escrimeur
    def obtenir_stats_escrimeur(row):
        if row['Tireur 1'] == escrimeur:
            return row['Touches Tireur 1'], row['Touches Tireur 2']
        else:
            return row['Touches Tireur 2'], row['Touches Tireur 1']
    
    df_escrimeur[['Touches Marquées', 'Touches Reçues']] = df_escrimeur.apply(
        lambda row: pd.Series(obtenir_stats_escrimeur(row)), axis=1
    )
    
    # Séparer poules et tableaux
    df_poules = df_escrimeur[df_escrimeur['Poule / Tableau'].str.startswith('Poule', na=False)].copy()
    
    # Filtre pour les tableaux : TOUT ce qui ne commence PAS par "Poule"
    df_tableaux = df_escrimeur[~df_escrimeur['Poule / Tableau'].str.startswith('Poule', na=False) & df_escrimeur['Poule / Tableau'].notna()].copy()
    
    # Fonction pour calculer les stats avec rankings
    def calculer_stats_avec_ranking(df_data, est_poule):
        if len(df_data) == 0:
            return None
        
        # CORRECTION : victoire = touches marquées > touches reçues (pas forcément == 5)
        victoires = len(df_data[df_data['Touches Marquées'] > df_data['Touches Reçues']])
        defaites = len(df_data[df_data['Touches Marquées'] < df_data['Touches Reçues']])
        total = len(df_data)
        
        pct_victoires = (victoires / total * 100) if total > 0 else 0
        
        touches_marquees_moy = df_data['Touches Marquées'].mean()
        touches_recues_moy = df_data['Touches Reçues'].mean()
        
        # Stats en cas de victoire
        df_victoires = df_data[df_data['Touches Marquées'] > df_data['Touches Reçues']]
        touches_marquees_victoire = df_victoires['Touches Marquées'].mean() if len(df_victoires) > 0 else 0
        touches_recues_victoire = df_victoires['Touches Reçues'].mean() if len(df_victoires) > 0 else 0
        
        # Stats en cas de défaite
        df_defaites = df_data[df_data['Touches Marquées'] < df_data['Touches Reçues']]
        touches_marquees_defaite = df_defaites['Touches Marquées'].mean() if len(df_defaites) > 0 else 0
        touches_recues_defaite = df_defaites['Touches Reçues'].mean() if len(df_defaites) > 0 else 0
        
        # Calculer les rankings par rapport à tous les autres escrimeurs
        tireurs_liste = sorted(set(df['Tireur 1'].unique()) | set(df['Tireur 2'].unique()))
        
        stats_tous = []
        for tireur_comp in tireurs_liste:
            # Filtrer pour ce tireur
            df_tireur_comp = df[
                ((df['Tireur 1'] == tireur_comp) | (df['Tireur 2'] == tireur_comp)) &
                (df['Saison'] >= saison_min) &
                (df['Saison'] <= saison_max)
            ].copy()
            
            if len(df_tireur_comp) == 0:
                continue
            
            # Ajouter colonnes touches - CORRECTION: vérifier que le df n'est pas vide
            touches_data = []
            for _, row in df_tireur_comp.iterrows():
                if row['Tireur 1'] == tireur_comp:
                    touches_data.append((row['Touches Tireur 1'], row['Touches Tireur 2']))
                else:
                    touches_data.append((row['Touches Tireur 2'], row['Touches Tireur 1']))
            
            df_tireur_comp['Touches Marquées'] = [t[0] for t in touches_data]
            df_tireur_comp['Touches Reçues'] = [t[1] for t in touches_data]
            
            # Filtrer selon type (poule ou tableau)
            if est_poule:
                df_tireur_filtre = df_tireur_comp[df_tireur_comp['Poule / Tableau'].str.startswith('Poule', na=False)].copy()
                min_matchs = 5  # Minimum 5 matchs pour les poules
            else:
                df_tireur_filtre = df_tireur_comp[~df_tireur_comp['Poule / Tableau'].str.startswith('Poule', na=False) & df_tireur_comp['Poule / Tableau'].notna()].copy()
                min_matchs = 1  # Pas de minimum pour les tableaux
            
            if len(df_tireur_filtre) < min_matchs:
                continue
            
            vict = len(df_tireur_filtre[df_tireur_filtre['Touches Marquées'] > df_tireur_filtre['Touches Reçues']])
            tot = len(df_tireur_filtre)
            pct = (vict / tot * 100) if tot > 0 else 0
            
            tm_moy = df_tireur_filtre['Touches Marquées'].mean()
            tr_moy = df_tireur_filtre['Touches Reçues'].mean()
            
            df_v = df_tireur_filtre[df_tireur_filtre['Touches Marquées'] > df_tireur_filtre['Touches Reçues']]
            tr_vict = df_v['Touches Reçues'].mean() if len(df_v) > 0 else 0
            
            df_d = df_tireur_filtre[df_tireur_filtre['Touches Marquées'] < df_tireur_filtre['Touches Reçues']]
            tm_def = df_d['Touches Marquées'].mean() if len(df_d) > 0 else 0
            
            stats_tous.append({
                'tireur': tireur_comp,
                'total': tot,
                'pct_victoires': pct,
                'touches_marquees_moy': tm_moy,
                'touches_recues_moy': tr_moy,
                'touches_recues_victoire': tr_vict,
                'touches_marquees_defaite': tm_def
            })
        
        # Calculer les rangs
        df_stats = pd.DataFrame(stats_tous)
        
        if len(df_stats) == 0:
            return {
                'victoires': victoires,
                'defaites': defaites,
                'total': total,
                'pct_victoires': pct_victoires,
                'touches_marquees_moy': touches_marquees_moy,
                'touches_recues_moy': touches_recues_moy,
                'touches_marquees_victoire': touches_marquees_victoire,
                'touches_recues_victoire': touches_recues_victoire,
                'touches_marquees_defaite': touches_marquees_defaite,
                'rang_total': 0,
                'rang_pct': 0,
                'rang_tm': 0,
                'rang_tr': 0,
                'rang_trv': 0,
                'rang_tmd': 0,
                'total_tireurs': 0
            }
        
        # Rang nombre de matchs (décroissant)
        df_stats = df_stats.sort_values('total', ascending=False).reset_index(drop=True)
        df_stats['rang_total'] = range(1, len(df_stats) + 1)
        
        # Rang % victoires (décroissant)
        df_stats = df_stats.sort_values('pct_victoires', ascending=False).reset_index(drop=True)
        df_stats['rang_pct'] = range(1, len(df_stats) + 1)
        
        # Rang touches marquées (décroissant)
        df_stats = df_stats.sort_values('touches_marquees_moy', ascending=False).reset_index(drop=True)
        df_stats['rang_tm'] = range(1, len(df_stats) + 1)
        
        # Rang touches reçues (croissant = moins c'est mieux)
        df_stats = df_stats.sort_values('touches_recues_moy', ascending=True).reset_index(drop=True)
        df_stats['rang_tr'] = range(1, len(df_stats) + 1)
        
        # Rang touches reçues en victoire (croissant = moins c'est mieux)
        df_stats = df_stats.sort_values('touches_recues_victoire', ascending=True).reset_index(drop=True)
        df_stats['rang_trv'] = range(1, len(df_stats) + 1)
        
        # Rang touches marquées en défaite (décroissant)
        df_stats = df_stats.sort_values('touches_marquees_defaite', ascending=False).reset_index(drop=True)
        df_stats['rang_tmd'] = range(1, len(df_stats) + 1)
        
        # Récupérer les rangs de l'escrimeur
        rang_tireur = df_stats[df_stats['tireur'] == escrimeur].iloc[0] if len(df_stats[df_stats['tireur'] == escrimeur]) > 0 else None
        total_tireurs = len(df_stats)
        
        return {
            'victoires': victoires,
            'defaites': defaites,
            'total': total,
            'pct_victoires': pct_victoires,
            'touches_marquees_moy': touches_marquees_moy,
            'touches_recues_moy': touches_recues_moy,
            'touches_marquees_victoire': touches_marquees_victoire,
            'touches_recues_victoire': touches_recues_victoire,
            'touches_marquees_defaite': touches_marquees_defaite,
            'rang_total': int(rang_tireur['rang_total']) if rang_tireur is not None else 0,
            'rang_pct': int(rang_tireur['rang_pct']) if rang_tireur is not None else 0,
            'rang_tm': int(rang_tireur['rang_tm']) if rang_tireur is not None else 0,
            'rang_tr': int(rang_tireur['rang_tr']) if rang_tireur is not None else 0,
            'rang_trv': int(rang_tireur['rang_trv']) if rang_tireur is not None else 0,
            'rang_tmd': int(rang_tireur['rang_tmd']) if rang_tireur is not None else 0,
            'total_tireurs': total_tireurs
        }
    
    # Calculer les stats pour poules et tableaux avec rankings
    stats_poules = calculer_stats_avec_ranking(df_poules, True)
    stats_tableaux = calculer_stats_avec_ranking(df_tableaux, False)
    
    st.markdown("---")
    st.subheader(f"Statistiques - {escrimeur}")
    
    # Afficher les deux camemberts côte à côte avec encadrements
    col1, col2 = st.columns(2)
    
    with col1:
        # Conteneur avec bordure pour poules
        with st.container(border=True):
            st.markdown("#### Matchs de Poule")
            st.markdown("")  # Petite marge
            if stats_poules and stats_poules['total'] > 0:
                fig_poules = go.Figure(data=[go.Pie(
                    labels=['Victoires', 'Défaites'],
                    values=[stats_poules['victoires'], stats_poules['defaites']],
                    hole=0.3,
                    marker_colors=['#2ecc71', '#e74c3c'],
                    textinfo='value',
                    textposition='inside'
                )])
                
                fig_poules.update_layout(
                    showlegend=True,
                    height=350,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig_poules, use_container_width=True)
                
                st.markdown("")  # Petite marge
                
                # Statistiques poules
                st.markdown("**Statistiques Poules :**")
                st.write(f"• Nombre de matchs tirés : **{stats_poules['total']}** (rang {stats_poules['rang_total']}/{stats_poules['total_tireurs']})")
                st.write(f"• % de victoires : **{stats_poules['pct_victoires']:.1f}%** (rang {stats_poules['rang_pct']}/{stats_poules['total_tireurs']})")
                st.write(f"• Touches marquées en moyenne par match : **{stats_poules['touches_marquees_moy']:.2f}** (rang {stats_poules['rang_tm']}/{stats_poules['total_tireurs']})")
                st.write(f"• Touches reçues en moyenne par match : **{stats_poules['touches_recues_moy']:.2f}** (rang {stats_poules['rang_tr']}/{stats_poules['total_tireurs']})")
                st.write(f"• Touches marquées en moyenne en cas de défaite : **{stats_poules['touches_marquees_defaite']:.2f}** (rang {stats_poules['rang_tmd']}/{stats_poules['total_tireurs']})")
                st.write(f"• Touches reçues en moyenne en cas de victoire : **{stats_poules['touches_recues_victoire']:.2f}** (rang {stats_poules['rang_trv']}/{stats_poules['total_tireurs']})")
            else:
                st.info("Aucun match de poule trouvé pour cet escrimeur sur cette période.")
    
    with col2:
        # Conteneur avec bordure pour tableaux
        with st.container(border=True):
            st.markdown("#### Matchs de Tableau")
            st.markdown("")  # Petite marge
            if stats_tableaux and stats_tableaux['total'] > 0:
                fig_tableaux = go.Figure(data=[go.Pie(
                    labels=['Victoires', 'Défaites'],
                    values=[stats_tableaux['victoires'], stats_tableaux['defaites']],
                    hole=0.3,
                    marker_colors=['#2ecc71', '#e74c3c'],
                    textinfo='value',
                    textposition='inside'
                )])
                
                fig_tableaux.update_layout(
                    showlegend=True,
                    height=350,
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig_tableaux, use_container_width=True)
                
                st.markdown("")  # Petite marge
                
                # Statistiques tableaux
                st.markdown("**Statistiques Tableaux :**")
                st.write(f"• Nombre de matchs tirés : **{stats_tableaux['total']}** (rang {stats_tableaux['rang_total']}/{stats_tableaux['total_tireurs']})")
                st.write(f"• % de victoires : **{stats_tableaux['pct_victoires']:.1f}%** (rang {stats_tableaux['rang_pct']}/{stats_tableaux['total_tireurs']})")
                st.write(f"• Touches marquées en moyenne par match : **{stats_tableaux['touches_marquees_moy']:.2f}** (rang {stats_tableaux['rang_tm']}/{stats_tableaux['total_tireurs']})")
                st.write(f"• Touches reçues en moyenne par match : **{stats_tableaux['touches_recues_moy']:.2f}** (rang {stats_tableaux['rang_tr']}/{stats_tableaux['total_tireurs']})")
                st.write(f"• Touches marquées en moyenne en cas de défaite : **{stats_tableaux['touches_marquees_defaite']:.2f}** (rang {stats_tableaux['rang_tmd']}/{stats_tableaux['total_tireurs']})")
                st.write(f"• Touches reçues en moyenne en cas de victoire : **{stats_tableaux['touches_recues_victoire']:.2f}** (rang {stats_tableaux['rang_trv']}/{stats_tableaux['total_tireurs']})")
            else:
                st.info("Aucun match de tableau trouvé pour cet escrimeur sur cette période.")
    
    # Histogramme des résultats
    
    with st.container(border=True):
        st.subheader("Historique des matchs")
        st.markdown("")  # Petite marge
        
        if len(df_escrimeur) > 0:
            # Garder l'ordre de la base de données (pas de tri par date)
            df_histo = df_escrimeur.copy()
            
            # Calculer l'ordonnée pour chaque match - UTILISER LA COLONNE VAINQUEUR
            def calculer_ordonnee(row):
                est_poule = row['Poule / Tableau'].startswith('Poule') if pd.notna(row['Poule / Tableau']) else False
                est_victoire = row['Vainqueur'] == escrimeur  # CORRECTION: Utiliser Vainqueur
                
                if est_poule:
                    return 1 if est_victoire else -1
                else:  # Tableau
                    return 2 if est_victoire else -2
            
            df_histo['Ordonnée'] = df_histo.apply(calculer_ordonnee, axis=1)
            
            # Calculer l'adversaire pour chaque match
            df_histo['Adversaire'] = df_histo.apply(
                lambda r: r['Tireur 2'] if r['Tireur 1'] == escrimeur else r['Tireur 1'], 
                axis=1
            )
            
            # Créer les couleurs (vert pour positif, rouge pour négatif)
            colors = ['#2ecc71' if val > 0 else '#e74c3c' for val in df_histo['Ordonnée']]
            
            # Formater les dates pour affichage
            df_histo['Date_str'] = df_histo['Date'].dt.strftime('%d/%m/%Y')
            
            # Créer l'histogramme
            fig_histo = go.Figure(data=[
                go.Bar(
                    x=list(range(len(df_histo))),
                    y=df_histo['Ordonnée'],
                    marker_color=colors,
                    hovertemplate='<b>Match %{x}</b><br>' +
                                 'Date: %{customdata[0]}<br>' +
                                 'Compétition: %{customdata[1]}<br>' +
                                 'Adversaire: %{customdata[2]}<br>' +
                                 'Score: %{customdata[3]} - %{customdata[4]}<br>' +
                                 'Type: %{customdata[5]}<br>' +
                                 '<extra></extra>',
                    customdata=df_histo[['Date_str', 'Compétition', 'Adversaire',
                                        'Touches Marquées', 'Touches Reçues', 'Poule / Tableau']].values
                )
            ])
            
            fig_histo.update_layout(
                xaxis_title="Numéro du match",
                yaxis_title="Résultat",
                height=400,
                showlegend=False,
                yaxis=dict(
                    tickvals=[-2, -1, 0, 1, 2],
                    ticktext=['Défaite Tableau', 'Défaite Poule', '', 'Victoire Poule', 'Victoire Tableau']
                )
            )
            
            st.plotly_chart(fig_histo, use_container_width=True)
        else:
            st.info("Aucun match trouvé pour cet escrimeur sur cette période.")
    
    # Graphiques d'évolution par saison
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Évolution du % de victoires par saison")
            st.markdown("")  # Petite marge
            
            if len(df_escrimeur) > 0:
                # Calculer les stats par saison pour les poules
                stats_saison_poules = []
                stats_saison_tableaux = []
                
                # Obtenir toutes les saisons disponibles dans la plage, sauf 2021
                saisons_liste = sorted([s for s in df_escrimeur['Saison'].unique() if s != 2021])
                
                for saison in saisons_liste:
                    # Poules
                    df_saison_poules = df_poules[df_poules['Saison'] == saison]
                    if len(df_saison_poules) > 0:
                        victoires_poules = len(df_saison_poules[df_saison_poules['Touches Marquées'] > df_saison_poules['Touches Reçues']])
                        pct_poules = (victoires_poules / len(df_saison_poules) * 100)
                        stats_saison_poules.append({'Saison': int(saison), '% Victoires': pct_poules})
                    
                    # Tableaux
                    df_saison_tableaux = df_tableaux[df_tableaux['Saison'] == saison]
                    if len(df_saison_tableaux) > 0:
                        victoires_tableaux = len(df_saison_tableaux[df_saison_tableaux['Touches Marquées'] > df_saison_tableaux['Touches Reçues']])
                        pct_tableaux = (victoires_tableaux / len(df_saison_tableaux) * 100)
                        stats_saison_tableaux.append({'Saison': int(saison), '% Victoires': pct_tableaux})
                
                # Créer le graphique
                fig_evolution = go.Figure()
                
                # Ligne pour les poules
                if len(stats_saison_poules) > 0:
                    df_stats_poules = pd.DataFrame(stats_saison_poules)
                    fig_evolution.add_trace(go.Scatter(
                        x=df_stats_poules['Saison'],
                        y=df_stats_poules['% Victoires'],
                        mode='lines+markers',
                        name='Poules',
                        line=dict(color='#3498db', width=2),
                        marker=dict(size=8)
                    ))
                
                # Ligne pour les tableaux
                if len(stats_saison_tableaux) > 0:
                    df_stats_tableaux = pd.DataFrame(stats_saison_tableaux)
                    fig_evolution.add_trace(go.Scatter(
                        x=df_stats_tableaux['Saison'],
                        y=df_stats_tableaux['% Victoires'],
                        mode='lines+markers',
                        name='Tableaux',
                        line=dict(color='#e74c3c', width=2),
                        marker=dict(size=8)
                    ))
                
                fig_evolution.update_layout(
                    xaxis_title="Saison",
                    yaxis_title="% de victoires",
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    yaxis=dict(range=[0, 100]),
                    xaxis=dict(
                        dtick=1,  # Forcer l'affichage par pas de 1
                        tickmode='linear'
                    )
                )
                
                st.plotly_chart(fig_evolution, use_container_width=True)
            else:
                st.info("Aucune donnée pour cet escrimeur sur cette période.")
        
        with col2:
            st.subheader("Nombre de victoires par saison")
            st.markdown("")  # Petite marge
            
            if len(df_escrimeur) > 0:
                # Obtenir toutes les saisons de la plage, sauf 2021
                saisons_liste = sorted([s for s in df_escrimeur['Saison'].unique() if s != 2021])
                
                # Créer les listes pour le graphique
                saisons_graph = []
                victoires_poules_graph = []
                victoires_tableaux_graph = []
                
                for saison in saisons_liste:
                    saisons_graph.append(int(saison))
                    
                    # Poules
                    df_saison_poules = df_poules[df_poules['Saison'] == saison]
                    nb_vict_poules = len(df_saison_poules[df_saison_poules['Touches Marquées'] > df_saison_poules['Touches Reçues']])
                    victoires_poules_graph.append(nb_vict_poules)
                    
                    # Tableaux
                    df_saison_tableaux = df_tableaux[df_tableaux['Saison'] == saison]
                    nb_vict_tableaux = len(df_saison_tableaux[df_saison_tableaux['Touches Marquées'] > df_saison_tableaux['Touches Reçues']])
                    victoires_tableaux_graph.append(nb_vict_tableaux)
                
                # Créer l'histogramme
                fig_victoires = go.Figure()
                
                fig_victoires.add_trace(go.Bar(
                    x=saisons_graph,
                    y=victoires_poules_graph,
                    name='Poules',
                    marker_color='#3498db'
                ))
                
                fig_victoires.add_trace(go.Bar(
                    x=saisons_graph,
                    y=victoires_tableaux_graph,
                    name='Tableaux',
                    marker_color='#e74c3c'
                ))
                
                fig_victoires.update_layout(
                    xaxis_title="Saison",
                    yaxis_title="Nombre de victoires",
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    barmode='group',
                    xaxis=dict(
                        dtick=1,
                        tickmode='linear'
                    )
                )
                
                st.plotly_chart(fig_victoires, use_container_width=True)
            else:
                st.info("Aucune donnée pour cet escrimeur sur cette période.")
    
    # Tableaux des derniers matchs
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("15 derniers matchs de Poule")
            
            if len(df_poules) > 0:
                # Prendre les 15 derniers matchs de poule
                df_derniers_poules = df_poules.sort_values('Date', ascending=False).head(15).copy()
                
                # Créer le tableau d'affichage
                tableau_poules = []
                for _, row in df_derniers_poules.iterrows():
                    victoire = row['Vainqueur'] == escrimeur  # CORRECTION: Utiliser Vainqueur
                    adversaire = row['Tireur 2'] if row['Tireur 1'] == escrimeur else row['Tireur 1']
                    
                    tableau_poules.append({
                        'Saison': int(row['Saison']),
                        'V/D': 'V' if victoire else 'D',
                        'Date': row['Date'].strftime('%d/%m/%y'),
                        'Compétition': row['Compétition'],
                        'Score': f"{int(row['Touches Marquées'])} - {int(row['Touches Reçues'])}",
                        'Adversaire': adversaire,
                        '_victoire': victoire  # Colonne cachée pour le style
                    })
                
                df_affichage_poules = pd.DataFrame(tableau_poules)
                
                # Supprimer la colonne _victoire
                victoires_list = df_affichage_poules['_victoire'].tolist()
                df_affichage_final = df_affichage_poules.drop(columns=['_victoire'])
                
                # Créer un DataFrame de styles basé sur les victoires
                def get_color(val, row_idx):
                    if victoires_list[row_idx]:
                        return 'color: green'
                    else:
                        return 'color: red'
                
                # Créer une matrice de styles
                styles = pd.DataFrame('', index=df_affichage_final.index, columns=df_affichage_final.columns)
                for idx in df_affichage_final.index:
                    for col in df_affichage_final.columns:
                        styles.at[idx, col] = get_color(df_affichage_final.at[idx, col], idx)
                
                # Appliquer le style
                df_styled = df_affichage_final.style.apply(lambda x: styles, axis=None)
                
                st.dataframe(df_styled, use_container_width=True, hide_index=True, height=600)
            else:
                st.info("Aucun match de poule pour cet escrimeur.")
    
    with col2:
        with st.container(border=True):
            st.subheader("15 derniers matchs de Tableau")
            
            if len(df_tableaux) > 0:
                # Prendre les 15 derniers matchs de tableau
                df_derniers_tableaux = df_tableaux.sort_values('Date', ascending=False).head(15).copy()
                
                # Dictionnaire de transformation pour Tour
                transformation_tour = {
                    "Tableau de 32": "1/16e",
                    "Tableau de 16": "1/8e",
                    "Quart de finale": "1/4",
                    "Demi finale": "1/2",
                    "Finale": "F"
                }
                
                # Créer le tableau d'affichage
                tableau_tableaux = []
                for _, row in df_derniers_tableaux.iterrows():
                    victoire = row['Vainqueur'] == escrimeur  # CORRECTION: Utiliser Vainqueur
                    adversaire = row['Tireur 2'] if row['Tireur 1'] == escrimeur else row['Tireur 1']
                    tour = transformation_tour.get(row['Poule / Tableau'], row['Poule / Tableau'])
                    
                    tableau_tableaux.append({
                        'Saison': int(row['Saison']),
                        'V/D': 'V' if victoire else 'D',
                        'Date': row['Date'].strftime('%d/%m/%y'),
                        'Compétition': row['Compétition'],
                        'Tour': tour,
                        'Score': f"{int(row['Touches Marquées'])} - {int(row['Touches Reçues'])}",
                        'Adversaire': adversaire,
                        '_victoire': victoire  # Colonne cachée pour le style
                    })
                
                df_affichage_tableaux = pd.DataFrame(tableau_tableaux)
                
                # Supprimer la colonne _victoire
                victoires_list_tableaux = df_affichage_tableaux['_victoire'].tolist()
                df_affichage_final_tableaux = df_affichage_tableaux.drop(columns=['_victoire'])
                
                # Créer un DataFrame de styles basé sur les victoires
                def get_color_tableau(val, row_idx):
                    if victoires_list_tableaux[row_idx]:
                        return 'color: green'
                    else:
                        return 'color: red'
                
                # Créer une matrice de styles
                styles_tableaux = pd.DataFrame('', index=df_affichage_final_tableaux.index, columns=df_affichage_final_tableaux.columns)
                for idx in df_affichage_final_tableaux.index:
                    for col in df_affichage_final_tableaux.columns:
                        styles_tableaux.at[idx, col] = get_color_tableau(df_affichage_final_tableaux.at[idx, col], idx)
                
                # Appliquer le style
                df_styled_tableaux = df_affichage_final_tableaux.style.apply(lambda x: styles_tableaux, axis=None)
                
                st.dataframe(df_styled_tableaux, use_container_width=True, hide_index=True, height=600)
            else:
                st.info("Aucun match de tableau pour cet escrimeur.")

# ===== PAGE 3: RÉSULTATS =====
elif st.session_state.page == "resultats":
    st.title("🏆 Résultats")
    
    # Charger les données des classements
    @st.cache_data
    def charger_classements():
        df_class = pd.read_excel('Résultats_Escrime_V5_2.xlsm', sheet_name='Data_classements')
        df_class['Date'] = pd.to_datetime(df_class['Date'])
        return df_class
    
    df_classements = charger_classements()
    
    # Récupérer tous les tireurs de la base classements
    tireurs_classements = sorted(df_classements['Tireur'].unique())
    
    # Filtres en haut
    col1, col2 = st.columns([2, 1])
    
    with col1:
        escrimeur_res = st.selectbox("Sélectionner un escrimeur", tireurs_classements, key="escrimeur_resultats")
    
    with col2:
        # Filtre saisons
        saisons_class = sorted([s for s in df_classements['Saison'].unique() if s != 2021])
        saison_min_res, saison_max_res = st.select_slider(
            "Plage de saisons",
            options=saisons_class,
            value=(min(saisons_class), max(saisons_class)),
            key="saisons_resultats"
        )
    
    # Filtrer les données pour l'escrimeur et les saisons
    df_class_filtre = df_classements[
        (df_classements['Tireur'] == escrimeur_res) &
        (df_classements['Saison'] >= saison_min_res) &
        (df_classements['Saison'] <= saison_max_res)
    ].copy()
    
    # Calculer les statistiques
    total_competitions = len(df_class_filtre)
    medailles = len(df_class_filtre[df_class_filtre['Rang'] <= 3])
    pct_medailles = (medailles / total_competitions * 100) if total_competitions > 0 else 0
    
    # Afficher le résumé
    st.markdown("---")
    with st.container(border=True):
        st.markdown(f"### {escrimeur_res} est médaillé dans {pct_medailles:.0f}% des {total_competitions} compétitions auxquelles il a participé")
        
        st.markdown("")
        
        # Statistiques CN
        st.markdown("#### Circuits Nationaux")
        df_cn = df_class_filtre[df_class_filtre['CN / CdF'] == 'CN']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            premiers_cn = len(df_cn[df_cn['Rang'] == 1])
            st.metric("🥇 1er", premiers_cn)
        with col2:
            seconds_cn = len(df_cn[df_cn['Rang'] == 2])
            st.metric("🥈 2ème", seconds_cn)
        with col3:
            troisiemes_cn = len(df_cn[df_cn['Rang'] == 3])
            st.metric("🥉 3ème", troisiemes_cn)
        
        st.markdown("")
        
        # Statistiques CdF
        st.markdown("#### Championnats de France")
        df_cdf = df_class_filtre[df_class_filtre['CN / CdF'] == 'CdF']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            premiers_cdf = len(df_cdf[df_cdf['Rang'] == 1])
            st.metric("🥇 1er", premiers_cdf)
        with col2:
            seconds_cdf = len(df_cdf[df_cdf['Rang'] == 2])
            st.metric("🥈 2ème", seconds_cdf)
        with col3:
            troisiemes_cdf = len(df_cdf[df_cdf['Rang'] == 3])
            st.metric("🥉 3ème", troisiemes_cdf)
