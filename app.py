import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(page_title="Suivi de Parc Réfrigérateurs", layout="wide")

st.title("❄️ Système de Suivi - Parc 1200 Réfrigérateurs")

# --- CHARGEMENT DE LA LISTE RÉFÉRENTIELLE (VOTRE EXCEL) ---
@st.cache_data
def charger_referentiel():
    if os.path.exists("liste_frigos.csv"):
        return pd.read_csv("liste_frigos.csv")
    else:
        # Si le fichier n'existe pas encore, on crée une liste vide pour éviter les erreurs
        return pd.DataFrame(columns=["ID_Frigo", "Responsable", "Zone"])

# --- FONCTION DE CHARGEMENT DE L'HISTORIQUE ---
def charger_donnees():
    if os.path.exists("suivi_activites.csv"):
        df = pd.read_csv("suivi_activites.csv")
        df = df.drop_duplicates(subset=["ID_Frigo", "Type", "Action_Detaillee", "Technicien"], keep='last')
        df["N°"] = range(1, len(df) + 1)
        return df
    else:
        return pd.DataFrame(columns=["N°", "Date", "ID_Frigo", "Type", "Action_Detaillee", "Technicien", "Responsable", "Zone"])

# Chargement des bases
df_referentiel = charger_referentiel()

# --- BARRE LATÉRALE : SAISIE ---
st.sidebar.header("📝 Nouvelle Intervention")

if not df_referentiel.empty:
    # Le technicien choisit l'ID dans votre liste Excel
    id_frigo = st.sidebar.selectbox("Sélectionner l'ID du Réfrigérateur", options=df_referentiel["ID_Frigo"].unique())
    
    # RÉCUPÉRATION AUTOMATIQUE des infos depuis votre fichier Excel
    infos_frigo = df_referentiel[df_referentiel["ID_Frigo"] == id_frigo].iloc[0]
    resp_auto = infos_frigo["Responsable"]
    zone_auto = infos_frigo["Zone"]
    
    # Affichage des infos pour confirmation (lecture seule)
    st.sidebar.info(f"📍 Responsable : {resp_auto}\n\n🌍 Zone : {zone_auto}")
else:
    st.sidebar.error("Fichier 'liste_frigos.csv' introuvable. Veuillez l'importer.")
    id_frigo = st.sidebar.text_input("ID du Réfrigérateur (Manuel)")
    resp_auto, zone_auto = "", ""

type_act = st.sidebar.selectbox("Type d'activité", ["Dépannage", "Entretien"])

if type_act == "Dépannage":
    action = st.sidebar.multiselect("Pièces remplacées", ["Compresseur", "Condensateur", "Ampoule", "Charge en gaz", "Thermostat", "Ventilateur", "Relais", "Déshydrateur"])
else:
    action = st.sidebar.multiselect("Actions effectuées", ["Débouchage", "Soufflage", "Lavage"])

tech = st.sidebar.text_input("Nom du Technicien")

if st.sidebar.button("Enregistrer l'intervention"):
    signature = f"{id_frigo}-{type_act}-{'-'.join(action)}-{tech}"
    
    if 'derniere_signature' in st.session_state and st.session_state.derniere_signature == signature:
        st.sidebar.warning("⚠️ Déjà enregistré !")
    elif not tech or not action:
        st.sidebar.error("❌ Veuillez remplir le nom du technicien et les actions.")
    else:
        df_actuel = charger_donnees()
        nouveau_suivi = {
            "N°": len(df_actuel) + 1,
            "Date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "ID_Frigo": id_frigo,
            "Type": type_act,
            "Action_Detaillee": ", ".join(action),
            "Technicien": tech,
            "Responsable": resp_auto, # Vient de l'Excel
            "Zone": zone_auto          # Vient de l'Excel
        }
        df_final = pd.concat([df_actuel, pd.DataFrame([nouveau_suivi])], ignore_index=True)
        df_final.to_csv("suivi_activites.csv", index=False)
        st.session_state.derniere_signature = signature
        st.sidebar.success("✅ Enregistré !")
        st.rerun()

# --- DASHBOARD ---
df_visu = charger_donnees()
st.subheader("📊 Suivi du Parc")
st.dataframe(df_visu, use_container_width=True, hide_index=True)