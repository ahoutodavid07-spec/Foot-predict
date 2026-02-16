import streamlit as st
import pandas as pd
from scipy.stats import poisson

# Configuration de l'application
st.set_page_config(page_title="IA Foot Europe 2026", page_icon="⚽")

st.title("🏆 IA de Prédiction Foot - Europe 2026")
st.write("Analyse basée sur les statistiques réelles de février 2026.")

# --- BASE DE DONNÉES ÉTENDUE ---
# Données basées sur les ratios de buts réels (ex: Bayern ~3.7 buts/match)
teams_data = {
    'Equipe': [
        'PSG', 'Lens', 'Marseille', 'Lyon', 'Lille',        # France
        'Arsenal', 'Man City', 'Aston Villa', 'Man Utd', 'Liverpool', # Angleterre
        'FC Barcelone', 'Real Madrid', 'Villarreal', 'Real Betis',    # Espagne
        'Inter Milan', 'AC Milan', 'Juventus', 'Naples',              # Italie
        'Bayern Munich', 'Borussia Dortmund'                          # Allemagne
    ],
    'Attaque': [
        2.2, 1.9, 2.1, 1.8, 1.6,  # France
        2.1, 2.3, 1.6, 1.9, 1.8,  # Angleterre
        2.7, 2.3, 1.9, 1.6,       # Espagne
        2.4, 1.7, 1.7, 1.5,       # Italie
        3.7, 2.1                  # Allemagne
    ], 
    'Defense': [
        0.8, 0.7, 1.3, 0.9, 1.4,  # France
        0.7, 0.9, 1.0, 1.4, 1.3,  # Angleterre
        0.5, 0.5, 1.0, 1.3,       # Espagne
        0.8, 0.7, 0.8, 0.9,       # Italie
        0.9, 0.9                  # Allemagne
    ]
}
df = pd.DataFrame(teams_data).sort_values('Equipe')

# --- LOGIQUE DE PRÉDICTION ---
def calculer_probabilites(domicile, exterieur):
    att_dom = df[df['Equipe'] == domicile]['Attaque'].values[0]
    def_dom = df[df['Equipe'] == domicile]['Defense'].values[0]
    att_ext = df[df['Equipe'] == exterieur]['Attaque'].values[0]
    def_ext = df[df['Equipe'] == exterieur]['Defense'].values[0]
    
    # Moyenne de buts attendus (xG) ajustée
    mu_dom = att_dom * def_ext / 1.3
    mu_ext = att_ext * def_dom / 1.3
    
    p_dom, p_nul, p_ext = 0, 0, 0
    for h in range(8):
        for a in range(8):
            prob = poisson.pmf(h, mu_dom) * poisson.pmf(a, mu_ext)
            if h > a: p_dom += prob
            elif h == a: p_nul += prob
            else: p_ext += prob
    return p_dom, p_nul, p_ext, mu_dom, mu_ext

# --- INTERFACE UTILISATEUR ---
st.sidebar.header("Configuration du Match")
equipe_h = st.sidebar.selectbox("Équipe à Domicile", df['Equipe'])
equipe_a = st.sidebar.selectbox("Équipe à l'Extérieur", df['Equipe'])

if st.button("Lancer l'Analyse"):
    win, draw, loss, xG_h, xG_a = calculer_probabilites(equipe_h, equipe_a)
    
    st.subheader(f"🏟️ {equipe_h} vs {equipe_a}")
    
    # Affichage des scores attendus
    c1, c2 = st.columns(2)
    c1.metric(f"xG {equipe_h}", round(xG_h, 2))
    c2.metric(f"xG {equipe_a}", round(xG_a, 2))
    
    # Probabilités finales
    st.write("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Victoire Domicile", f"{win:.1%}")
    col2.metric("Match Nul", f"{draw:.1%}")
    col3.metric("Victoire Extérieur", f"{loss:.1%}")
    
    st.progress(int(win * 100))
    
    # Verdict IA
    if win > loss and win > draw:
        st.success(f"Verdict : Avantage net pour {equipe_h}.")
    elif loss > win and loss > draw:
        st.warning(f"Verdict : Avantage net pour {equipe_a}.")
    else:
        st.info("Verdict : Match très équilibré, nul probable.")
