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

# ===== SIDEBAR : ESCRIMEUR PRINCIPAL =====
with st.sidebar:
    st.markdown("---")
    
    # Obtenir tous les escrimeurs
    tous_les_escrimeurs = sorted(set(df['Tireur 1'].unique()) | set(df['Tireur 2'].unique()))
    
    # Définir un escrimeur par défaut intelligent (celui avec le plus de matchs)
    if 'escrimeur_principal' not in st.session_state:
        # Compter les matchs pour chaque escrimeur
        compteur_matchs = {}
        for esc in tous_les_escrimeurs:
            nb_matchs = len(df[(df['Tireur 1'] == esc) | (df['Tireur 2'] == esc)])
            compteur_matchs[esc] = nb_matchs
        
        # Prendre celui avec le plus de matchs
        escrimeur_defaut = max(compteur_matchs, key=compteur_matchs.get)
        st.session_state.escrimeur_principal = escrimeur_defaut
    
    # Sélection de l'escrimeur principal
    st.markdown("### 👤 Escrimeur principal")
    
    index_actuel = tous_les_escrimeurs.index(st.session_state.escrimeur_principal)
    escrimeur_principal = st.selectbox(
        "Changer d'escrimeur",
        tous_les_escrimeurs,
        index=index_actuel,
        key="select_esc_principal"
    )
    
    # Mettre à jour si changement
    if escrimeur_principal != st.session_state.escrimeur_principal:
        st.session_state.escrimeur_principal = escrimeur_principal
        st.rerun()
    
    st.markdown("---")
    
    # Calculer des stats rapides pour l'escrimeur principal
    df_esc = df[(df['Tireur 1'] == escrimeur_principal) | (df['Tireur 2'] == escrimeur_principal)]
    nb_matchs_total = len(df_esc)
    
    victoires = 0
    for _, row in df_esc.iterrows():
        if row['Vainqueur'] == escrimeur_principal:
            victoires += 1
    
    pct_victoires = (victoires / nb_matchs_total * 100) if nb_matchs_total > 0 else 0
    
    # Affichage stylisé
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
        <h2 style='margin:0; font-size: 24px;'>👤 {escrimeur_principal}</h2>
        <p style='margin:5px 0 0 0; opacity:0.9; font-size: 14px;'>Escrimeur principal</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats rapides
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Matchs", nb_matchs_total)
    with col2:
        st.metric("🏆 % Vict.", f"{pct_victoires:.1f}%")
    
    st.markdown("---")
    
    # Info
    st.markdown("""
    <div style='background-color: rgba(103, 126, 234, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;'>
        <p style='margin: 0; font-size: 13px; color: #667eea;'>
            <b>💡 Astuce</b><br/>
            Cet escrimeur est utilisé par défaut dans toutes les pages.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Navigation en haut avec boutons
st.markdown("### Navigation")

# Définir les couleurs des boutons selon la page active
page_actuelle = st.session_state.get('page', 'matchs')

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    bouton_type_matchs = "secondary" if page_actuelle != "matchs" else "primary"
    if st.button("📊 Matchs", use_container_width=True, type=bouton_type_matchs, key="btn_matchs"):
        st.session_state.page = "matchs"
        st.rerun()
with col2:
    bouton_type_resultats = "secondary" if page_actuelle != "resultats" else "primary"
    if st.button("🏆 Résultats", use_container_width=True, type=bouton_type_resultats, key="btn_resultats"):
        st.session_state.page = "resultats"
        st.rerun()
with col3:
    bouton_type_versus = "secondary" if page_actuelle != "versus" else "primary"
    if st.button("⚔️ Versus", use_container_width=True, type=bouton_type_versus, key="btn_versus"):
        st.session_state.page = "versus"
        st.rerun()
with col4:
    bouton_type_rankings = "secondary" if page_actuelle != "rankings" else "primary"
    if st.button("🏅 Rankings", use_container_width=True, type=bouton_type_rankings, key="btn_rankings"):
        st.session_state.page = "rankings"
        st.rerun()
with col5:
    bouton_type_consultation = "secondary" if page_actuelle != "consultation" else "primary"
    if st.button("📋 Base de données des matchs", use_container_width=True, type=bouton_type_consultation, key="btn_consultation"):
        st.session_state.page = "consultation"
        st.rerun()

# Initialiser la page par défaut
if 'page' not in st.session_state:
    st.session_state.page = "matchs"

# ===== PAGE 1: BASE DE DONNÉES DES MATCHS =====
if st.session_state.page == "consultation":
    st.title("⚔️ Base de données des matchs")

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
        height=550
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
        # Utiliser l'escrimeur principal comme défaut
        escrimeur_defaut = st.session_state.get('escrimeur_principal', 'TURLIER Christophe')
        if escrimeur_defaut not in tireurs_liste:
            escrimeur_defaut = tireurs_liste[0]
        index_defaut = tireurs_liste.index(escrimeur_defaut)
        
        escrimeur = st.selectbox("Sélectionner un escrimeur", tireurs_liste, index=index_defaut)
    
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
                    yaxis=dict(range=[0, 110], dtick=20),  # De 0 à 110% avec graduation tous les 20%
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
    
    # Tableaux des derniers matchs (SANS ligne de séparation)
    
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
                
                st.dataframe(df_styled, use_container_width=True, hide_index=True, height=550)
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
                
                st.dataframe(df_styled_tableaux, use_container_width=True, hide_index=True, height=550)
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
    
    df_class = charger_classements()
    
    # Récupérer tous les tireurs de la base classements
    tireurs_classements = sorted(df_class['Tireur'].unique())
    
    # Filtres en haut
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Utiliser l'escrimeur principal comme défaut
        escrimeur_defaut_res = st.session_state.get('escrimeur_principal', 'TURLIER Christophe')
        if escrimeur_defaut_res not in tireurs_classements:
            escrimeur_defaut_res = tireurs_classements[0]
        index_defaut_res = tireurs_classements.index(escrimeur_defaut_res)
        
        escrimeur_res = st.selectbox("Sélectionner un escrimeur", tireurs_classements, index=index_defaut_res, key="escrimeur_resultats")
    
    with col2:
        # Filtre saisons
        saisons_class = sorted([s for s in df_class['Saison'].unique() if s != 2021])
        saison_min_res, saison_max_res = st.select_slider(
            "Plage de saisons",
            options=saisons_class,
            value=(min(saisons_class), max(saisons_class)),
            key="saisons_resultats"
        )
    
    # Filtrer les données pour l'escrimeur et les saisons
    df_class_filtre = df_class[
        (df_class['Tireur'] == escrimeur_res) &
        (df_class['Saison'] >= saison_min_res) &
        (df_class['Saison'] <= saison_max_res)
    ].copy()
    
    # Calculer les statistiques
    total_competitions = len(df_class_filtre)
    medailles = len(df_class_filtre[df_class_filtre['Rang'] <= 3])
    pct_medailles = (medailles / total_competitions * 100) if total_competitions > 0 else 0
    
    # Calculer les statistiques par tour
    finales = len(df_class_filtre[df_class_filtre['Rang'].isin([1, 2])])
    demi_finales = len(df_class_filtre[df_class_filtre['Rang'] == 3])
    quarts = len(df_class_filtre[(df_class_filtre['Rang'] >= 5) & (df_class_filtre['Rang'] <= 8)])
    tableau_16 = len(df_class_filtre[(df_class_filtre['Rang'] >= 9) & (df_class_filtre['Rang'] <= 16)])
    tableau_32 = len(df_class_filtre[df_class_filtre['Rang'] > 16])
    
    # Afficher le résumé
    st.markdown("---")
    
    col_gauche, col_droite = st.columns(2)
    
    with col_gauche:
        with st.container(border=True, height=650):  # HAUTEUR FIXE EN PIXELS
            # Phrase sur 2 lignes pour éviter les problèmes d'alignement
            st.markdown(f"<p style='font-size: 21px; text-align: center;'><b>{escrimeur_res} est médaillé dans {pct_medailles:.0f}% des {total_competitions} compétitions<br>auxquelles il a participé</b></p>", unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Statistiques CN
            st.markdown("<p style='font-size: 21px; text-align: center;'><b>Circuits Nationaux</b></p>", unsafe_allow_html=True)
            df_cn = df_class_filtre[df_class_filtre['CN / CdF'] == 'CN']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                premiers_cn = len(df_cn[df_cn['Rang'] == 1])
                st.markdown(f"<p style='font-size: 19px; text-align: center;'>🥇 1er</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 27px; text-align: center; font-weight: bold;'>{premiers_cn}</p>", unsafe_allow_html=True)
            with col2:
                seconds_cn = len(df_cn[df_cn['Rang'] == 2])
                st.markdown(f"<p style='font-size: 19px; text-align: center;'>🥈 2ème</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 27px; text-align: center; font-weight: bold;'>{seconds_cn}</p>", unsafe_allow_html=True)
            with col3:
                troisiemes_cn = len(df_cn[df_cn['Rang'] == 3])
                st.markdown(f"<p style='font-size: 19px; text-align: center;'>🥉 3ème</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 27px; text-align: center; font-weight: bold;'>{troisiemes_cn}</p>", unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # Statistiques CdF
            st.markdown("<p style='font-size: 21px; text-align: center;'><b>Championnats de France</b></p>", unsafe_allow_html=True)
            df_cdf = df_class_filtre[df_class_filtre['CN / CdF'] == 'CdF']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                premiers_cdf = len(df_cdf[df_cdf['Rang'] == 1])
                st.markdown(f"<p style='font-size: 19px; text-align: center;'>🥇 1er</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 27px; text-align: center; font-weight: bold;'>{premiers_cdf}</p>", unsafe_allow_html=True)
            with col2:
                seconds_cdf = len(df_cdf[df_cdf['Rang'] == 2])
                st.markdown(f"<p style='font-size: 19px; text-align: center;'>🥈 2ème</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 27px; text-align: center; font-weight: bold;'>{seconds_cdf}</p>", unsafe_allow_html=True)
            with col3:
                troisiemes_cdf = len(df_cdf[df_cdf['Rang'] == 3])
                st.markdown(f"<p style='font-size: 19px; text-align: center;'>🥉 3ème</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 27px; text-align: center; font-weight: bold;'>{troisiemes_cdf}</p>", unsafe_allow_html=True)
    
    with col_droite:
        with st.container(border=True, height=650):  # MÊME HAUTEUR FIXE EN PIXELS
            st.markdown(f"<p style='font-size: 21px; text-align: center;'><b>Participation à {total_competitions} compétitions</b></p>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Créer le camembert sans légende, avec labels intégrés, en excluant les valeurs à 0
            if total_competitions > 0:
                # Créer les données uniquement pour les valeurs > 0
                data_camembert = []
                labels_camembert = []
                couleurs_camembert = []
                
                if finales > 0:
                    data_camembert.append(finales)
                    labels_camembert.append(f'Finale : {finales}')
                    couleurs_camembert.append('#FFD700')
                
                if demi_finales > 0:
                    data_camembert.append(demi_finales)
                    labels_camembert.append(f'Demi-Finale : {demi_finales}')
                    couleurs_camembert.append('#C0C0C0')
                
                if quarts > 0:
                    data_camembert.append(quarts)
                    labels_camembert.append(f'Quart de Finale : {quarts}')
                    couleurs_camembert.append('#CD7F32')
                
                if tableau_16 > 0:
                    data_camembert.append(tableau_16)
                    labels_camembert.append(f'Tableau de 16 : {tableau_16}')
                    couleurs_camembert.append('#3498db')
                
                if tableau_32 > 0:
                    data_camembert.append(tableau_32)
                    labels_camembert.append(f'Tableau de 32 : {tableau_32}')
                    couleurs_camembert.append('#95a5a6')
                
                fig_tours = go.Figure(data=[go.Pie(
                    labels=labels_camembert,
                    values=data_camembert,
                    hole=0.3,
                    marker_colors=couleurs_camembert,
                    textinfo='label',
                    textposition='outside',  # Forcer à l'extérieur
                    insidetextorientation='horizontal',
                    textfont=dict(size=19),  # Même taille que 1er, 2ème, 3ème
                    pull=[0 for _ in data_camembert]
                )])
                
                fig_tours.update_layout(
                    showlegend=False,
                    height=450,  # Encore plus petit
                    width=450,   # Largeur réduite
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                
                st.plotly_chart(fig_tours, use_container_width=True)
            else:
                st.info("Aucune compétition sur cette période.")
    
    # Graphique avec toutes les compétitions (SANS ligne de séparation)
    
    with st.container(border=True):
        st.subheader("Historique des résultats")
        st.markdown("")
        
        # Récupérer toutes les compétitions de la période
        df_toutes_compets = df_class[
            (df_class['Saison'] >= saison_min_res) &
            (df_class['Saison'] <= saison_max_res)
        ].copy()
        
        # Créer une liste unique de compétitions triées par date
        compets_uniques = df_toutes_compets.sort_values('Date')[['Date', 'Compétition', 'Saison']].drop_duplicates(subset=['Date', 'Compétition'])
        
        if len(compets_uniques) > 0:
            # Créer les labels
            compets_uniques['Label'] = compets_uniques['Saison'].astype(str) + ' - ' + compets_uniques['Compétition']
            
            # Pour chaque compétition, chercher si l'escrimeur a participé
            resultats = []
            labels = []
            for _, comp in compets_uniques.iterrows():
                labels.append(comp['Label'])
                
                # Chercher le résultat de l'escrimeur pour cette compétition
                resultat_escrimeur = df_class_filtre[
                    (df_class_filtre['Date'] == comp['Date']) &
                    (df_class_filtre['Compétition'] == comp['Compétition'])
                ]
                
                if len(resultat_escrimeur) > 0:
                    resultats.append(resultat_escrimeur.iloc[0]['Rang'])
                else:
                    resultats.append(None)  # Pas de participation
            
            # Créer le graphique
            fig_toutes = go.Figure()
            
            fig_toutes.add_trace(go.Scatter(
                x=labels,
                y=resultats,
                mode='lines+markers+text',
                line=dict(color='#e74c3c', width=2),
                marker=dict(size=8, color='#e74c3c'),
                text=[str(int(r)) if r is not None else '' for r in resultats],
                textposition='top center',
                textfont=dict(size=12),
                connectgaps=True,
                hovertemplate='<b>%{x}</b><br>Place: %{y}<extra></extra>'
            ))
            
            # Déterminer le max pour les shapes
            max_rang = max([r for r in resultats if r is not None], default=20)
            
            # Créer les lignes grises horizontales pour 5, 10, 15, 20... (PAS 0)
            shapes_lignes = []
            for val in range(5, int(max_rang) + 5, 5):
                shapes_lignes.append(dict(
                    type='line',
                    x0=-0.5,
                    x1=len(labels)-0.5,
                    y0=val,
                    y1=val,
                    line=dict(color='lightgray', width=1)
                ))
            
            fig_toutes.update_layout(
                xaxis_title="",
                yaxis_title="Place",
                height=500,
                showlegend=False,
                xaxis=dict(
                    side='top',
                    tickangle=-90,
                    tickfont=dict(size=14)
                ),
                yaxis=dict(
                    autorange='reversed',
                    dtick=5,
                    range=[-0.5, max_rang + 2],
                    showgrid=False
                ),
                shapes=shapes_lignes
            )
            
            st.plotly_chart(fig_toutes, use_container_width=True)
        else:
            st.info("Aucune compétition sur cette période.")
    
    # Tableau de tous les résultats (SANS ligne de séparation)
    
    col_tableau_resultats, col_vide = st.columns([1, 1])  # Moitié de page
    
    with col_tableau_resultats:
        with st.container(border=True):
            st.subheader("Résultats")
            st.markdown("")
            
            if len(df_class_filtre) > 0:
                # Créer le tableau
                resultats_tableau = []
                
                for _, row in df_class_filtre.sort_values('Date', ascending=False).iterrows():
                    # Trouver le nombre total d'escrimeurs (= rang du dernier)
                    compet_categorie = df_class[
                        (df_class['Date'] == row['Date']) &
                        (df_class['Compétition'] == row['Compétition']) &
                        (df_class['Catégorie'] == row['Catégorie'])
                    ]
                    total_escrimeurs = compet_categorie['Rang'].max() if len(compet_categorie) > 0 else row['Rang']
                    
                    resultats_tableau.append({
                        'Saison': str(int(row['Saison'])),  # Format string sans virgule
                        'Date': row['Date'].strftime('%d/%m/%y'),
                        'Compétition': row['Compétition'],
                        'Catégorie': row['Catégorie'],
                        'Type': row['CN / CdF'],
                        'Résultat': f"{int(row['Rang'])} sur {int(total_escrimeurs)}"
                    })
                
                df_resultats = pd.DataFrame(resultats_tableau)
                
                # Appliquer un style pour centrer la colonne Résultat
                st.dataframe(df_resultats, use_container_width=True, hide_index=True, height=400)
            else:
                st.info("Aucun résultat sur cette période.")

# ===== PAGE 4: VERSUS =====
elif st.session_state.page == "versus":
    st.title("⚔️ Versus")
    
    # Récupérer tous les tireurs
    tireurs_versus = sorted(set(df['Tireur 1'].unique()) | set(df['Tireur 2'].unique()))
    
    # Filtres en haut - Sélection des escrimeurs avec image VS
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            # Escrimeur 1 - utiliser l'escrimeur principal par défaut
            escrimeur1_defaut = st.session_state.get('escrimeur_principal', 'TURLIER Christophe')
            if escrimeur1_defaut not in tireurs_versus:
                escrimeur1_defaut = tireurs_versus[0]
            index1 = tireurs_versus.index(escrimeur1_defaut)
            escrimeur1 = st.selectbox("Sélectionner Escrimeur 1", tireurs_versus, index=index1, key="esc1")
        
        with col2:
            # Image VS
            try:
                from PIL import Image
                import base64
                from io import BytesIO
                vs_image = Image.open('/mnt/user-data/uploads/1770818459684_image.png')
                st.image(vs_image, use_column_width=True)
            except:
                st.markdown("<h1 style='text-align: center;'>VS</h1>", unsafe_allow_html=True)
        
        with col3:
            # Escrimeur 2
            escrimeur2_defaut = tireurs_versus[1] if len(tireurs_versus) > 1 else tireurs_versus[0]
            index2 = tireurs_versus.index(escrimeur2_defaut)
            escrimeur2 = st.selectbox("Sélectionner Escrimeur 2", tireurs_versus, index=index2, key="esc2")
        
        # Slider saisons
        st.markdown("")
        saisons_versus = sorted([s for s in df['Saison'].unique() if s != 2021])
        saison_min_vs, saison_max_vs = st.select_slider(
            "Plage de saisons",
            options=saisons_versus,
            value=(min(saisons_versus), max(saisons_versus)),
            key="saisons_versus"
        )
    
    # Filtrer les confrontations directes
    df_versus = df[
        (((df['Tireur 1'] == escrimeur1) & (df['Tireur 2'] == escrimeur2)) |
         ((df['Tireur 1'] == escrimeur2) & (df['Tireur 2'] == escrimeur1))) &
        (df['Saison'] >= saison_min_vs) &
        (df['Saison'] <= saison_max_vs)
    ].copy()
    
    # Calculer les statistiques
    total_confrontations = len(df_versus)
    
    if total_confrontations > 0:
        # Victoires escrimeur 1
        victoires_esc1 = len(df_versus[df_versus['Vainqueur'] == escrimeur1])
        victoires_esc2 = len(df_versus[df_versus['Vainqueur'] == escrimeur2])
        pct_victoires_esc1 = (victoires_esc1 / total_confrontations * 100)
        
        # Couleurs distinctives
        couleur_esc1 = '#3498db'  # Bleu
        couleur_esc2 = '#e74c3c'  # Rouge
        
        # BLOC 1 : Pourcentage et histogramme uniquement
        with st.container(border=True):
            st.markdown(f"<p style='font-size: 20px; text-align: center;'><b><span style='color:{couleur_esc1}'>{pct_victoires_esc1:.0f}%</span> de victoires pour <span style='color:{couleur_esc1}'>{escrimeur1}</span></b></p>", unsafe_allow_html=True)
            
            st.markdown("")
            
            # Histogramme HORIZONTAL des confrontations
            fig_confrontations = go.Figure()
            
            fig_confrontations.add_trace(go.Bar(
                y=['Confrontations'],
                x=[victoires_esc1],
                name=escrimeur1,
                marker_color=couleur_esc1,
                text=victoires_esc1,
                textposition='inside',
                textfont=dict(size=20, color='white'),
                showlegend=False,
                orientation='h'
            ))
            
            fig_confrontations.add_trace(go.Bar(
                y=['Confrontations'],
                x=[victoires_esc2],
                name=escrimeur2,
                marker_color=couleur_esc2,
                text=victoires_esc2,
                textposition='inside',
                textfont=dict(size=20, color='white'),
                showlegend=False,
                orientation='h'
            ))
            
            fig_confrontations.update_layout(
                barmode='stack',
                height=100,
                showlegend=False,
                xaxis=dict(visible=False, range=[0, total_confrontations * 1.2]),
                yaxis=dict(visible=False),
                margin=dict(t=0, b=0, l=100, r=100),
                bargap=0.3
            )
            
            # Centrer l'histogramme
            col_vide1, col_histo, col_vide2 = st.columns([0.5, 2, 0.5])
            with col_histo:
                st.plotly_chart(fig_confrontations, use_container_width=True)
        
        # BLOC 2 et 3 : Stats à gauche (moitié page), Camemberts à droite (moitié page)
        st.markdown("")
        
        col_stats_gauche, col_camemberts_droite = st.columns([1, 1])
        
        # Calculer les stats par type
        df_poules_vs = df_versus[df_versus['Poule / Tableau'].str.startswith('Poule', na=False)]
        df_tableaux_vs = df_versus[~df_versus['Poule / Tableau'].str.startswith('Poule', na=False) & df_versus['Poule / Tableau'].notna()]
        
        vict_poules_esc1 = len(df_poules_vs[df_poules_vs['Vainqueur'] == escrimeur1])
        vict_tableaux_esc1 = len(df_tableaux_vs[df_tableaux_vs['Vainqueur'] == escrimeur1])
        
        pct_poules_esc1 = (vict_poules_esc1 / len(df_poules_vs) * 100) if len(df_poules_vs) > 0 else 0
        pct_tableaux_esc1 = (vict_tableaux_esc1 / len(df_tableaux_vs) * 100) if len(df_tableaux_vs) > 0 else 0
        
        # Touches marquées
        touches_esc1 = 0
        touches_esc2 = 0
        for _, row in df_versus.iterrows():
            if row['Tireur 1'] == escrimeur1:
                touches_esc1 += row['Touches Tireur 1']
                touches_esc2 += row['Touches Tireur 2']
            else:
                touches_esc1 += row['Touches Tireur 2']
                touches_esc2 += row['Touches Tireur 1']
        
        # Score moyen quand chacun gagne - UNIQUEMENT MATCHS EN 10 TOUCHES (TABLEAUX)
        df_gagne_esc1 = df_tableaux_vs[df_tableaux_vs['Vainqueur'] == escrimeur1].copy()
        df_gagne_esc2 = df_tableaux_vs[df_tableaux_vs['Vainqueur'] == escrimeur2].copy()
        
        score_moy_esc1 = 0
        score_moy_esc2 = 0
        score_moy_perdant_esc1 = 0
        score_moy_perdant_esc2 = 0
        
        for _, row in df_gagne_esc1.iterrows():
            if row['Tireur 1'] == escrimeur1:
                score_moy_esc1 += row['Touches Tireur 1']
                score_moy_perdant_esc2 += row['Touches Tireur 2']
            else:
                score_moy_esc1 += row['Touches Tireur 2']
                score_moy_perdant_esc2 += row['Touches Tireur 1']
        score_moy_esc1 = score_moy_esc1 / len(df_gagne_esc1) if len(df_gagne_esc1) > 0 else 0
        score_moy_perdant_esc2 = score_moy_perdant_esc2 / len(df_gagne_esc1) if len(df_gagne_esc1) > 0 else 0
        
        for _, row in df_gagne_esc2.iterrows():
            if row['Tireur 1'] == escrimeur2:
                score_moy_esc2 += row['Touches Tireur 1']
                score_moy_perdant_esc1 += row['Touches Tireur 2']
            else:
                score_moy_esc2 += row['Touches Tireur 2']
                score_moy_perdant_esc1 += row['Touches Tireur 1']
        score_moy_esc2 = score_moy_esc2 / len(df_gagne_esc2) if len(df_gagne_esc2) > 0 else 0
        score_moy_perdant_esc1 = score_moy_perdant_esc1 / len(df_gagne_esc2) if len(df_gagne_esc2) > 0 else 0
        
        # BLOC 2 : Statistiques détaillées (gauche)
        with col_stats_gauche:
            with st.container(border=True):
                st.markdown("### Statistiques détaillées")
                st.markdown("")
                
                matchs_10_touches = len(df_tableaux_vs)
                
                st.markdown(f"<p style='font-size:16px;'><b>{total_confrontations} confrontations, dont {matchs_10_touches} matchs en 10 touches</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:{couleur_esc1}; font-size:16px;'><b>{pct_poules_esc1:.1f}% de victoires en poules pour {escrimeur1}</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:{couleur_esc1}; font-size:16px;'><b>{pct_tableaux_esc1:.1f}% de victoires en tableau pour {escrimeur1}</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:{couleur_esc1}; font-size:16px;'><b>{touches_esc1} touches marquées par {escrimeur1}</b></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:{couleur_esc2}; font-size:16px;'><b>{touches_esc2} touches marquées par {escrimeur2}</b></p>", unsafe_allow_html=True)
                
                # Afficher les scores moyens avec gestion du "-"
                if len(df_gagne_esc1) > 0:
                    st.markdown(f"<p style='color:{couleur_esc1}; font-size:16px;'><b>Score moyen quand {escrimeur1} gagne : 10 - {score_moy_perdant_esc2:.1f}</b></p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='color:{couleur_esc1}; font-size:16px;'><b>Score moyen quand {escrimeur1} gagne : -</b></p>", unsafe_allow_html=True)
                
                if len(df_gagne_esc2) > 0:
                    st.markdown(f"<p style='color:{couleur_esc2}; font-size:16px;'><b>Score moyen quand {escrimeur2} gagne : 10 - {score_moy_perdant_esc1:.1f}</b></p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='color:{couleur_esc2}; font-size:16px;'><b>Score moyen quand {escrimeur2} gagne : -</b></p>", unsafe_allow_html=True)
        
        # BLOC 3 : Camemberts côte à côte (droite)
        with col_camemberts_droite:
            with st.container(border=True):
                st.markdown("### Matchs")
                st.markdown("")
                
                col_cam1, col_cam2 = st.columns(2)
                
                with col_cam1:
                    # Camembert 1 : Matchs en 5 touches
                    vict_5t_esc1 = len(df_poules_vs[df_poules_vs['Vainqueur'] == escrimeur1])
                    vict_5t_esc2 = len(df_poules_vs[df_poules_vs['Vainqueur'] == escrimeur2])
                    
                    fig_5t = go.Figure(data=[go.Pie(
                        labels=[escrimeur1, escrimeur2],
                        values=[vict_5t_esc1, vict_5t_esc2],
                        marker_colors=[couleur_esc1, couleur_esc2],
                        textinfo='value',
                        textfont=dict(size=18),
                        hole=0
                    )])
                    fig_5t.update_layout(
                        title=dict(text="Matchs 5 touches", font=dict(size=18), x=0.5, xanchor='center'),
                        height=200,
                        margin=dict(t=40, b=0, l=0, r=0),
                        showlegend=False
                    )
                    st.plotly_chart(fig_5t, use_container_width=True)
                
                with col_cam2:
                    # Camembert 2 : Matchs en 10 touches
                    vict_10t_esc1 = len(df_tableaux_vs[df_tableaux_vs['Vainqueur'] == escrimeur1])
                    vict_10t_esc2 = len(df_tableaux_vs[df_tableaux_vs['Vainqueur'] == escrimeur2])
                    
                    fig_10t = go.Figure(data=[go.Pie(
                        labels=[escrimeur1, escrimeur2],
                        values=[vict_10t_esc1, vict_10t_esc2],
                        marker_colors=[couleur_esc1, couleur_esc2],
                        textinfo='value',
                        textfont=dict(size=18),
                        hole=0
                    )])
                    fig_10t.update_layout(
                        title=dict(text="Matchs 10 touches", font=dict(size=18), x=0.5, xanchor='center'),
                        height=200,
                        margin=dict(t=40, b=0, l=0, r=0),
                        showlegend=False
                    )
                    st.plotly_chart(fig_10t, use_container_width=True)

        
        # Deux blocs côte à côte : Tableau et Histogramme
        st.markdown("")
        
        col_tableau, col_histo = st.columns(2)
        
        with col_tableau:
            with st.container(border=True):
                st.subheader("15 derniers matchs")
                
                # Prendre les 15 derniers matchs
                df_derniers = df_versus.sort_values('Date', ascending=False).head(15).copy()
                
                # Transformation Tour
                transformation_tour = {
                    "Tableau de 32": "1/16e",
                    "Tableau de 16": "1/8e",
                    "Quart de finale": "1/4",
                    "Demi finale": "1/2",
                    "Finale": "F"
                }
                
                # Créer le tableau
                tableau_confrontations = []
                for _, row in df_derniers.iterrows():
                    tour = row['Poule / Tableau']
                    if tour and not pd.isna(tour):
                        if tour.startswith('Poule'):
                            tour_affiche = tour
                        else:
                            tour_affiche = transformation_tour.get(tour, tour)
                    else:
                        tour_affiche = ""
                    
                    # Déterminer le score
                    if row['Tireur 1'] == escrimeur1:
                        score = f"{int(row['Touches Tireur 1'])} - {int(row['Touches Tireur 2'])}"
                    else:
                        score = f"{int(row['Touches Tireur 2'])} - {int(row['Touches Tireur 1'])}"
                    
                    tableau_confrontations.append({
                        'Saison': int(row['Saison']),
                        'Date': row['Date'].strftime('%d/%m/%y'),
                        'Compétition': row['Compétition'],
                        'Tour': tour_affiche,
                        'Escrimeur 1': escrimeur1,
                        'Score': score,
                        'Escrimeur 2': escrimeur2,
                        '_gagnant': row['Vainqueur']
                    })
                
                df_affichage_conf = pd.DataFrame(tableau_confrontations)
                
                # Supprimer la colonne _gagnant
                gagnants_list = df_affichage_conf['_gagnant'].tolist()
                df_affichage_final_conf = df_affichage_conf.drop(columns=['_gagnant'])
                
                # Créer une matrice de styles
                styles_conf = pd.DataFrame('', index=df_affichage_final_conf.index, columns=df_affichage_final_conf.columns)
                for idx in df_affichage_final_conf.index:
                    for col in df_affichage_final_conf.columns:
                        if gagnants_list[idx] == escrimeur1:
                            styles_conf.at[idx, col] = f'color: {couleur_esc1}'
                        else:
                            styles_conf.at[idx, col] = f'color: {couleur_esc2}'
                
                df_styled_conf = df_affichage_final_conf.style.apply(lambda x: styles_conf, axis=None)
                
                st.dataframe(df_styled_conf, use_container_width=True, hide_index=True, height=550)
        
        with col_histo:
            with st.container(border=True):
                st.subheader("Résultats des confrontations")
                
                # Créer l'histogramme horizontal
                df_histo = df_versus.sort_values('Date').copy()
                
                touches_esc1_list = []
                touches_esc2_list = []
                
                for _, row in df_histo.iterrows():
                    if row['Tireur 1'] == escrimeur1:
                        touches_esc1_list.append(row['Touches Tireur 1'])
                        touches_esc2_list.append(row['Touches Tireur 2'])
                    else:
                        touches_esc1_list.append(row['Touches Tireur 2'])
                        touches_esc2_list.append(row['Touches Tireur 1'])
                
                # Créer le graphique (jaune pour esc1 à gauche, orange pour esc2 à droite)
                fig_touches = go.Figure()
                
                # Barres de gauche (escrimeur 1) - valeurs négatives pour aller à gauche
                fig_touches.add_trace(go.Bar(
                    y=list(range(len(touches_esc1_list))),
                    x=[-t for t in touches_esc1_list],
                    orientation='h',
                    name=escrimeur1,
                    marker_color='#3498db',  # Bleu
                    text=touches_esc1_list,
                    textposition='inside',
                    textfont=dict(size=14),  # Agrandi
                    hoverinfo='text',
                    hovertext=[f"{escrimeur1}: {t}" for t in touches_esc1_list]
                ))
                
                # Barres de droite (escrimeur 2)
                fig_touches.add_trace(go.Bar(
                    y=list(range(len(touches_esc2_list))),
                    x=touches_esc2_list,
                    orientation='h',
                    name=escrimeur2,
                    marker_color='#e74c3c',  # Rouge
                    text=touches_esc2_list,
                    textposition='inside',
                    textfont=dict(size=14),  # Agrandi
                    hoverinfo='text',
                    hovertext=[f"{escrimeur2}: {t}" for t in touches_esc2_list]
                ))
                
                fig_touches.update_layout(
                    barmode='overlay',
                    height=550,
                    showlegend=False,
                    xaxis=dict(
                        range=[-15, 15],
                        showticklabels=False,
                        zeroline=True,
                        zerolinecolor='black',
                        zerolinewidth=2
                    ),
                    yaxis=dict(
                        showticklabels=False,
                        autorange='reversed'
                    ),
                    margin=dict(t=40, b=20, l=20, r=20),
                    annotations=[
                        dict(
                            text=f"<b>{escrimeur1}</b>",
                            x=-10,
                            y=-1,
                            xref='x',
                            yref='y',
                            showarrow=False,
                            font=dict(size=20, color='#3498db')  # Agrandi et gras
                        ),
                        dict(
                            text=f"<b>{escrimeur2}</b>",
                            x=10,
                            y=-1,
                            xref='x',
                            yref='y',
                            showarrow=False,
                            font=dict(size=20, color='#e74c3c')  # Agrandi et gras
                        )
                    ]
                )
                
                st.plotly_chart(fig_touches, use_container_width=True)
    else:
        st.info("Aucune confrontation entre ces deux escrimeurs sur cette période.")

# ===== PAGE 5: RANKINGS =====
elif st.session_state.page == "rankings":
    st.title("🏅 Rankings")
    
    # Charger les données des classements
    @st.cache_data
    def charger_classements_rankings():
        df_class = pd.read_excel('Résultats_Escrime_V5_2.xlsm', sheet_name='Data_classements')
        df_class['Date'] = pd.to_datetime(df_class['Date'])
        return df_class
    
    df_class = charger_classements_rankings()
    
    # Initialiser le ranking par défaut
    if 'ranking_choisi' not in st.session_state:
        st.session_state.ranking_choisi = "Nombre total de matches tirés"
    
    # Sélection escrimeur et saisons
    with st.container(border=True):
        col_esc, col_saisons = st.columns([2, 1])
        
        with col_saisons:
            saisons_rankings = sorted([s for s in df['Saison'].unique() if s != 2021])
            saison_min_rank, saison_max_rank = st.select_slider(
                "Plage de saisons",
                options=saisons_rankings,
                value=(min(saisons_rankings), max(saisons_rankings)),
                key="saisons_rankings"
            )
        
        with col_esc:
            tous_tireurs_temp = sorted(set(df['Tireur 1'].unique()) | set(df['Tireur 2'].unique()))
            liste_tireurs = [''] + tous_tireurs_temp
            
            # Pré-sélectionner l'escrimeur principal
            escrimeur_principal_rankings = st.session_state.get('escrimeur_principal', '')
            if escrimeur_principal_rankings in tous_tireurs_temp:
                index_esc_rankings = liste_tireurs.index(escrimeur_principal_rankings)
            else:
                index_esc_rankings = 0
            
            escrimeur_selectionne = st.selectbox(
                "Sélectionner un escrimeur (optionnel)",
                liste_tireurs,
                index=index_esc_rankings,
                key="esc_rankings"
            )
    
    # Filtrer les données selon les saisons
    df_filtre = df[(df['Saison'] >= saison_min_rank) & (df['Saison'] <= saison_max_rank)].copy()
    df_class_filtre = df_class[(df_class['Saison'] >= saison_min_rank) & (df_class['Saison'] <= saison_max_rank)].copy()
    
    # Calculer les statistiques pour tous les tireurs
    tous_tireurs = sorted(set(df_filtre['Tireur 1'].unique()) | set(df_filtre['Tireur 2'].unique()))
    
    stats_tireurs = []
    
    for tireur in tous_tireurs:
        df_tireur = df_filtre[((df_filtre['Tireur 1'] == tireur) | (df_filtre['Tireur 2'] == tireur))].copy()
        nb_matchs = len(df_tireur)
        
        if nb_matchs >= 10:
            # Initialisation
            touches_5_marquees = 0
            touches_10_marquees = 0
            touches_5_recues = 0
            touches_10_recues = 0
            victoires = 0
            defaites = 0
            vict_poules = 0
            vict_tableaux = 0
            nb_poules = 0
            nb_tableaux = 0
            vict_5_4 = 0
            vict_10_9 = 0
            def_4_5 = 0
            def_9_10 = 0
            matchs_5_4 = 0
            matchs_10_9 = 0
            
            for _, row in df_tireur.iterrows():
                est_poule = row['Poule / Tableau'] and pd.notna(row['Poule / Tableau']) and row['Poule / Tableau'].startswith('Poule')
                
                if row['Tireur 1'] == tireur:
                    touches_marquees = row['Touches Tireur 1']
                    touches_recues = row['Touches Tireur 2']
                    a_gagne = (row['Vainqueur'] == tireur)
                else:
                    touches_marquees = row['Touches Tireur 2']
                    touches_recues = row['Touches Tireur 1']
                    a_gagne = (row['Vainqueur'] == tireur)
                
                # Compter victoires/défaites
                if a_gagne:
                    victoires += 1
                    if est_poule:
                        vict_poules += 1
                    else:
                        vict_tableaux += 1
                    
                    # Victoires serrées
                    if touches_marquees == 5 and touches_recues == 4:
                        vict_5_4 += 1
                    elif touches_marquees == 10 and touches_recues == 9:
                        vict_10_9 += 1
                else:
                    defaites += 1
                    # Défaites serrées
                    if touches_marquees == 4 and touches_recues == 5:
                        def_4_5 += 1
                    elif touches_marquees == 9 and touches_recues == 10:
                        def_9_10 += 1
                
                # Touches par type
                if est_poule:
                    touches_5_marquees += touches_marquees
                    touches_5_recues += touches_recues
                    nb_poules += 1
                else:
                    touches_10_marquees += touches_marquees
                    touches_10_recues += touches_recues
                    nb_tableaux += 1
                
                # Matchs serrés
                if (touches_marquees == 5 and touches_recues == 4) or (touches_marquees == 4 and touches_recues == 5):
                    matchs_5_4 += 1
                elif (touches_marquees == 10 and touches_recues == 9) or (touches_marquees == 9 and touches_recues == 10):
                    matchs_10_9 += 1
            
            # Calculs pour compétitions
            df_compets_tireur = df_class_filtre[df_class_filtre['Tireur'] == tireur]
            nb_participations = len(df_compets_tireur)
            nb_victoires_compet = len(df_compets_tireur[df_compets_tireur['Rang'] == 1])
            nb_podiums = len(df_compets_tireur[df_compets_tireur['Rang'] <= 3])
            
            total_touches_marquees = touches_5_marquees + touches_10_marquees
            total_touches_recues = touches_5_recues + touches_10_recues
            
            stats_tireurs.append({
                'Tireur': tireur,
                # MATCH
                'Nb matchs': nb_matchs,
                'Nb matchs poule': nb_poules,
                'Nb matchs tableau': nb_tableaux,
                # VICTOIRES
                'Pct victoires total': (victoires / nb_matchs * 100) if nb_matchs > 0 else 0,
                'Pct victoires poules': (vict_poules / nb_poules * 100) if nb_poules > 0 else 0,
                'Pct victoires tableau': (vict_tableaux / nb_tableaux * 100) if nb_tableaux > 0 else 0,
                'Nb victoires': victoires,
                'Nb vict serrees': vict_5_4 + vict_10_9,
                'Vict 5-4': vict_5_4,
                'Vict 10-9': vict_10_9,
                'Nb def serrees': def_4_5 + def_9_10,
                'Def 4-5': def_4_5,
                'Def 9-10': def_9_10,
                'Nerf acier': vict_10_9,
                # TOUCHES
                'Total touches marquees': total_touches_marquees,
                'Moy touches par compet': total_touches_marquees / nb_participations if nb_participations > 0 else 0,
                'Total touches recues': total_touches_recues,
                'Moy touches recues par compet': total_touches_recues / nb_participations if nb_participations > 0 else 0,
                # TOUCHES POULE
                'Touches marquees poule': touches_5_marquees,
                'Touches recues poule': touches_5_recues,
                'Moy touches marquees par match poule': touches_5_marquees / nb_poules if nb_poules > 0 else 0,
                'Moy touches recues par match poule': touches_5_recues / nb_poules if nb_poules > 0 else 0,
                'Nb matchs 5-4': matchs_5_4,
                # TOUCHES TABLEAU
                'Touches marquees tableau': touches_10_marquees,
                'Touches recues tableau': touches_10_recues,
                'Moy touches marquees par match tableau': touches_10_marquees / nb_tableaux if nb_tableaux > 0 else 0,
                'Moy touches recues par match tableau': touches_10_recues / nb_tableaux if nb_tableaux > 0 else 0,
                'Nb matchs 10-9': matchs_10_9,
                # COMPETITIONS
                'Nb compet gagnees': nb_victoires_compet,
                'Nb podiums': nb_podiums,
                'Nb participations': nb_participations
            })
    
    if len(stats_tireurs) > 0:
        df_stats_complet = pd.DataFrame(stats_tireurs)
        
        # Zone de sélection avec BOUTONS par catégories
        with st.container(border=True):
            # Configuration des rankings
            rankings_config = {
                # MATCH
                "Nombre total de matches tirés": {'col': 'Nb matchs', 'titre': 'Plus grand nombre de matches tirés', 'type': 'simple', 'cat': 'match'},
                "Nombre de matches en poule": {'col': 'Nb matchs poule', 'titre': 'Plus grand nombre de matches en poule', 'type': 'simple', 'cat': 'match'},
                "Nombre de matches de tableau": {'col': 'Nb matchs tableau', 'titre': 'Plus grand nombre de matches de tableau', 'type': 'simple', 'cat': 'match'},
                # VICTOIRES
                "% total de victoires": {'col': 'Pct victoires total', 'titre': 'Meilleur % total de victoires', 'type': 'pourcentage', 'cat': 'victoires'},
                "% de victoires en poules": {'col': 'Pct victoires poules', 'titre': 'Meilleur % de victoires en poules', 'type': 'pourcentage', 'cat': 'victoires'},
                "% de victoires dans le tableau": {'col': 'Pct victoires tableau', 'titre': 'Meilleur % de victoires dans le tableau', 'type': 'pourcentage', 'cat': 'victoires'},
                "Nombre de victoires": {'col': 'Nb victoires', 'titre': 'Plus grand nombre de victoires', 'type': 'simple', 'cat': 'victoires'},
                "Nombre de victoires serrées": {'col': 'Nb vict serrees', 'titre': 'Plus grand nombre de victoires serrées', 'type': 'empile', 'col1': 'Vict 5-4', 'col2': 'Vict 10-9', 'label1': 'Victoires 5-4', 'label2': 'Victoires 10-9', 'cat': 'victoires'},
                "Nombre de défaites serrées": {'col': 'Nb def serrees', 'titre': 'Plus grand nombre de défaites serrées', 'type': 'empile', 'col1': 'Def 4-5', 'col2': 'Def 9-10', 'label1': 'Défaites 4-5', 'label2': 'Défaites 9-10', 'cat': 'victoires'},
                "Nerf d'acier": {'col': 'Nerf acier', 'titre': 'Nerf d\'acier (victoires 10-9)', 'type': 'simple', 'cat': 'victoires'},
                # TOUCHES
                "Nombre total de touches marquées": {'col': 'Total touches marquees', 'titre': 'Plus grand nombre de touches marquées', 'type': 'empile_touches', 'col1': 'Touches marquees poule', 'col2': 'Touches marquees tableau', 'cat': 'touches'},
                "Nombre moyen de touches marquées par compétition": {'col': 'Moy touches par compet', 'titre': 'Meilleure moyenne de touches marquées par compétition', 'type': 'decimal', 'cat': 'touches'},
                "Nombre de touches reçues": {'col': 'Total touches recues', 'titre': 'Plus grand nombre de touches reçues', 'type': 'simple', 'cat': 'touches'},
                "Nombre moyen de touches reçues par compétition": {'col': 'Moy touches recues par compet', 'titre': 'Moyenne de touches reçues par compétition', 'type': 'decimal', 'cat': 'touches'},
                # POULE
                "Nombre de touches marquées en poule": {'col': 'Touches marquees poule', 'titre': 'Plus grand nombre de touches marquées en poule', 'type': 'simple', 'cat': 'poule'},
                "Nombre de touches reçues en poule": {'col': 'Touches recues poule', 'titre': 'Plus grand nombre de touches reçues en poule', 'type': 'simple', 'cat': 'poule'},
                "Nombre de touches marquées en moyenne par match de poule": {'col': 'Moy touches marquees par match poule', 'titre': 'Meilleure moyenne de touches marquées par match de poule', 'type': 'decimal', 'cat': 'poule'},
                "Nombre de touches reçues en moyenne par match de poule": {'col': 'Moy touches recues par match poule', 'titre': 'Moyenne de touches reçues par match de poule', 'type': 'decimal', 'cat': 'poule'},
                "Nombre de matchs à 5-4": {'col': 'Nb matchs 5-4', 'titre': 'Plus grand nombre de matchs à 5-4', 'type': 'simple', 'cat': 'poule'},
                # TABLEAU
                "Nombre de touches marquées dans le tableau": {'col': 'Touches marquees tableau', 'titre': 'Plus grand nombre de touches marquées dans le tableau', 'type': 'simple', 'cat': 'tableau'},
                "Nombre de touches reçues dans le tableau": {'col': 'Touches recues tableau', 'titre': 'Plus grand nombre de touches reçues dans le tableau', 'type': 'simple', 'cat': 'tableau'},
                "Nombre de touches marquées en moy. par match de tableau": {'col': 'Moy touches marquees par match tableau', 'titre': 'Meilleure moyenne de touches marquées par match de tableau', 'type': 'decimal', 'cat': 'tableau'},
                "Nombre de touches reçues en moy. par match de tableau": {'col': 'Moy touches recues par match tableau', 'titre': 'Moyenne de touches reçues par match de tableau', 'type': 'decimal', 'cat': 'tableau'},
                "Nombre de matchs à 10-9": {'col': 'Nb matchs 10-9', 'titre': 'Plus grand nombre de matchs à 10-9', 'type': 'simple', 'cat': 'tableau'},
                # COMPETITIONS
                "Nombre de compétitions gagnées": {'col': 'Nb compet gagnees', 'titre': 'Plus grand nombre de compétitions gagnées', 'type': 'simple', 'cat': 'compet'},
                "Nombre de podiums": {'col': 'Nb podiums', 'titre': 'Plus grand nombre de podiums', 'type': 'simple', 'cat': 'compet'},
                "Nombre de participations": {'col': 'Nb participations', 'titre': 'Plus grand nombre de participations', 'type': 'simple', 'cat': 'compet'}
            }
            
            # Catégorie MATCH
            st.markdown("### 📋 MATCH")
            cols = st.columns(3)
            match_options = ["Nombre total de matches tirés", "Nombre de matches en poule", "Nombre de matches de tableau"]
            for i, option in enumerate(match_options):
                with cols[i]:
                    btn_type = "primary" if st.session_state.ranking_choisi == option else "secondary"
                    if st.button(option.replace("Nombre de matches", "Nb"), key=f"btn_{option}", use_container_width=True, type=btn_type):
                        st.session_state.ranking_choisi = option
                        st.rerun()
            
            st.markdown("")
            
            # Catégorie VICTOIRES
            st.markdown("### 🏆 VICTOIRES")
            cols = st.columns(4)
            victoires_options = ["% total de victoires", "% de victoires en poules", "% de victoires dans le tableau", "Nombre de victoires", "Nombre de victoires serrées", "Nombre de défaites serrées", "Nerf d'acier"]
            for i, option in enumerate(victoires_options):
                with cols[i % 4]:
                    label = option.replace("Nombre de victoires", "Nb vict").replace("Nombre de défaites", "Nb déf").replace("% total de victoires", "% total vict").replace("% de victoires", "% vict")
                    btn_type = "primary" if st.session_state.ranking_choisi == option else "secondary"
                    if st.button(label, key=f"btn_{option}", use_container_width=True, type=btn_type):
                        st.session_state.ranking_choisi = option
                        st.rerun()
            
            st.markdown("")
            
            # Catégorie TOUCHES
            st.markdown("### ⚔️ TOUCHES")
            cols = st.columns(4)
            touches_options = ["Nombre total de touches marquées", "Nombre moyen de touches marquées par compétition", "Nombre de touches reçues", "Nombre moyen de touches reçues par compétition"]
            for i, option in enumerate(touches_options):
                with cols[i]:
                    label = option.replace("Nombre total de touches", "Total touches").replace("Nombre moyen de touches", "Moy touches").replace("Nombre de touches", "Touches")
                    btn_type = "primary" if st.session_state.ranking_choisi == option else "secondary"
                    if st.button(label, key=f"btn_{option}", use_container_width=True, type=btn_type):
                        st.session_state.ranking_choisi = option
                        st.rerun()
            
            st.markdown("")
            
            # Catégorie TOUCHES POULE
            st.markdown("### 🐔 TOUCHES POULE")
            cols = st.columns(5)
            poule_options = ["Nombre de touches marquées en poule", "Nombre de touches reçues en poule", "Nombre de touches marquées en moyenne par match de poule", "Nombre de touches reçues en moyenne par match de poule", "Nombre de matchs à 5-4"]
            for i, option in enumerate(poule_options):
                with cols[i]:
                    label = option.replace("Nombre de touches marquées en poule", "Marquées").replace("Nombre de touches reçues en poule", "Reçues").replace("Nombre de touches marquées en moyenne par match de poule", "Moy marquées/match").replace("Nombre de touches reçues en moyenne par match de poule", "Moy reçues/match").replace("Nombre de matchs à 5-4", "Matchs 5-4")
                    btn_type = "primary" if st.session_state.ranking_choisi == option else "secondary"
                    if st.button(label, key=f"btn_{option}", use_container_width=True, type=btn_type):
                        st.session_state.ranking_choisi = option
                        st.rerun()
            
            st.markdown("")
            
            # Catégorie TOUCHES TABLEAU
            st.markdown("### 📊 TOUCHES TABLEAU")
            cols = st.columns(5)
            tableau_options = ["Nombre de touches marquées dans le tableau", "Nombre de touches reçues dans le tableau", "Nombre de touches marquées en moy. par match de tableau", "Nombre de touches reçues en moy. par match de tableau", "Nombre de matchs à 10-9"]
            for i, option in enumerate(tableau_options):
                with cols[i]:
                    label = option.replace("Nombre de touches marquées dans le tableau", "Marquées").replace("Nombre de touches reçues dans le tableau", "Reçues").replace("Nombre de touches marquées en moy. par match de tableau", "Moy marquées/match").replace("Nombre de touches reçues en moy. par match de tableau", "Moy reçues/match").replace("Nombre de matchs à 10-9", "Matchs 10-9")
                    btn_type = "primary" if st.session_state.ranking_choisi == option else "secondary"
                    if st.button(label, key=f"btn_{option}", use_container_width=True, type=btn_type):
                        st.session_state.ranking_choisi = option
                        st.rerun()
            
            st.markdown("")
            
            # Catégorie COMPETITIONS
            st.markdown("### 🏅 COMPETITIONS")
            cols = st.columns(3)
            compet_options = ["Nombre de compétitions gagnées", "Nombre de podiums", "Nombre de participations"]
            for i, option in enumerate(compet_options):
                with cols[i]:
                    label = option.replace("Nombre de compétitions", "Nb compét").replace("Nombre de podiums", "Nb podiums").replace("Nombre de participations", "Nb participations")
                    btn_type = "primary" if st.session_state.ranking_choisi == option else "secondary"
                    if st.button(label, key=f"btn_{option}", use_container_width=True, type=btn_type):
                        st.session_state.ranking_choisi = option
                        st.rerun()
        
        # Obtenir le ranking choisi
        ranking_choisi = st.session_state.ranking_choisi
        config = rankings_config[ranking_choisi]
        df_stats = df_stats_complet.sort_values(config['col'], ascending=False).copy()
        
        # Trouver la position de l'escrimeur sélectionné
        position_escrimeur = None
        valeur_escrimeur = None
        if escrimeur_selectionne and escrimeur_selectionne in df_stats['Tireur'].values:
            position_escrimeur = df_stats[df_stats['Tireur'] == escrimeur_selectionne].index[0] + 1
            valeur_escrimeur = df_stats[df_stats['Tireur'] == escrimeur_selectionne][config['col']].values[0]
        
        # Podium
        with st.container(border=True):
            st.markdown(f"<h3 style='text-align: center;'>{config['titre']}</h3>", unsafe_allow_html=True)
            st.markdown("")
            
            # Colonnes pour le podium + escrimeur sélectionné
            if position_escrimeur and position_escrimeur > 3:
                col1, col2, col3, col_sep, col_esc = st.columns([1, 1, 1, 0.2, 1])
            else:
                col1, col2, col3 = st.columns(3)
                col_esc = None
            
            with col1:
                if len(df_stats) >= 2:
                    deuxieme = df_stats.iloc[1]
                    if config['type'] == 'pourcentage':
                        valeur = f"{deuxieme[config['col']]:.1f}%"
                    elif config['type'] == 'decimal':
                        valeur = f"{deuxieme[config['col']]:.1f}"
                    else:
                        valeur = str(int(deuxieme[config['col']]))
                    st.markdown(f"<h1 style='text-align: center;'>🥈</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align: center;'>{valeur}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{deuxieme['Tireur']}</p>", unsafe_allow_html=True)
            
            with col2:
                if len(df_stats) >= 1:
                    premier = df_stats.iloc[0]
                    if config['type'] == 'pourcentage':
                        valeur = f"{premier[config['col']]:.1f}%"
                    elif config['type'] == 'decimal':
                        valeur = f"{premier[config['col']]:.1f}"
                    else:
                        valeur = str(int(premier[config['col']]))
                    st.markdown(f"<h1 style='text-align: center;'>🥇</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align: center;'>{valeur}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{premier['Tireur']}</p>", unsafe_allow_html=True)
            
            with col3:
                if len(df_stats) >= 3:
                    troisieme = df_stats.iloc[2]
                    if config['type'] == 'pourcentage':
                        valeur = f"{troisieme[config['col']]:.1f}%"
                    elif config['type'] == 'decimal':
                        valeur = f"{troisieme[config['col']]:.1f}"
                    else:
                        valeur = str(int(troisieme[config['col']]))
                    st.markdown(f"<h1 style='text-align: center;'>🥉</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align: center;'>{valeur}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{troisieme['Tireur']}</p>", unsafe_allow_html=True)
            
            # Afficher l'escrimeur sélectionné s'il n'est pas dans le top 3
            if col_esc:
                with col_esc:
                    if config['type'] == 'pourcentage':
                        valeur = f"{valeur_escrimeur:.1f}%"
                    elif config['type'] == 'decimal':
                        valeur = f"{valeur_escrimeur:.1f}"
                    else:
                        valeur = str(int(valeur_escrimeur))
                    st.markdown(f"<h1 style='text-align: center;'>#{position_escrimeur}</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align: center;'>{valeur}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{escrimeur_selectionne}</p>", unsafe_allow_html=True)
        
        # Histogramme
        st.markdown("")
        
        with st.container(border=True):
            if config['type'] == 'empile_touches':
                # Histogramme empilé pour les touches (5 et 10)
                fig = go.Figure()
                
                # Couleurs : rouge pour l'escrimeur sélectionné, bleu pour les autres
                couleurs_5 = ['#FF0000' if tireur == escrimeur_selectionne else '#9370DB' for tireur in df_stats['Tireur']]
                couleurs_10 = ['#FF0000' if tireur == escrimeur_selectionne else '#4169E1' for tireur in df_stats['Tireur']]
                
                fig.add_trace(go.Bar(
                    y=df_stats['Tireur'],
                    x=df_stats[config['col1']],
                    name='Matchs en 5 touches',
                    orientation='h',
                    marker_color=couleurs_5,
                    text=df_stats[config['col']],
                    textposition='outside',
                    textfont=dict(size=12)
                ))
                
                fig.add_trace(go.Bar(
                    y=df_stats['Tireur'],
                    x=df_stats[config['col2']],
                    name='Matchs en 10 touches',
                    orientation='h',
                    marker_color=couleurs_10
                ))
                
                fig.update_layout(
                    barmode='stack',
                    height=max(400, len(df_stats) * 25),
                    xaxis_title="Nombre de touches",
                    yaxis_title="",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis=dict(autorange='reversed')
                )
            elif config['type'] == 'empile':
                # Histogramme empilé pour victoires/défaites serrées
                fig = go.Figure()
                
                couleurs_1 = ['#FF0000' if tireur == escrimeur_selectionne else '#9370DB' for tireur in df_stats['Tireur']]
                couleurs_2 = ['#FF0000' if tireur == escrimeur_selectionne else '#4169E1' for tireur in df_stats['Tireur']]
                
                fig.add_trace(go.Bar(
                    y=df_stats['Tireur'],
                    x=df_stats[config['col1']],
                    name=config['label1'],
                    orientation='h',
                    marker_color=couleurs_1,
                    text=df_stats[config['col']],
                    textposition='outside',
                    textfont=dict(size=12)
                ))
                
                fig.add_trace(go.Bar(
                    y=df_stats['Tireur'],
                    x=df_stats[config['col2']],
                    name=config['label2'],
                    orientation='h',
                    marker_color=couleurs_2
                ))
                
                fig.update_layout(
                    barmode='stack',
                    height=max(400, len(df_stats) * 25),
                    xaxis_title="Nombre",
                    yaxis_title="",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis=dict(autorange='reversed')
                )
            else:
                # Histogramme simple
                fig = go.Figure()
                
                # Couleurs : rouge pour l'escrimeur sélectionné
                couleurs = ['#FF0000' if tireur == escrimeur_selectionne else '#4169E1' for tireur in df_stats['Tireur']]
                
                if config['type'] == 'pourcentage':
                    text_vals = df_stats[config['col']].apply(lambda x: f"{x:.1f}%")
                elif config['type'] == 'decimal':
                    text_vals = df_stats[config['col']].apply(lambda x: f"{x:.1f}")
                else:
                    text_vals = df_stats[config['col']].apply(lambda x: str(int(x)))
                
                fig.add_trace(go.Bar(
                    y=df_stats['Tireur'],
                    x=df_stats[config['col']],
                    orientation='h',
                    marker_color=couleurs,
                    text=text_vals,
                    textposition='outside'
                ))
                
                fig.update_layout(
                    height=max(400, len(df_stats) * 25),
                    xaxis_title="",
                    yaxis_title="",
                    showlegend=False,
                    yaxis=dict(autorange='reversed')
                )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucun tireur n'a fait au moins 10 matchs sur cette période.")
