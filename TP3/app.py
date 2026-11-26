import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="BigData Commerce Analytics", layout="wide")


@st.cache_data
def charger():
    commandes = pd.read_parquet("data/commandes_pseudo.parquet")
    paiements = pd.read_parquet("data/paiements_pseudo.parquet")
    return commandes, paiements


commandes, paiements = charger()
payes = paiements[paiements["payment_status"] == "PAID"]

st.sidebar.title("BigData Commerce Analytics")
vue = st.sidebar.radio(
    "Vue",
    ["Vue d'ensemble", "Catégories", "Encaissements", "Clients", "Paiements et données"],
)
st.sidebar.caption("Données fictives DummyJSON, paiements simulés, clients pseudonymisés.")

if vue == "Vue d'ensemble":
    st.title("Vue d'ensemble")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Chiffre d'affaires des commandes", f"{commandes['discounted_line_total'].sum():,.0f} USD".replace(",", " "))
    c2.metric("Encaissements PAID", f"{payes['amount'].sum():,.0f} USD".replace(",", " "))
    c3.metric("Nombre de paniers", commandes["cart_id_pseudo"].nunique())
    c4.metric("Paiements acceptés", f"{100 * len(payes) / len(paiements):.1f} %")

    statuts = paiements["payment_status"].value_counts().reset_index()
    statuts.columns = ["Statut", "Nombre"]
    fig = px.pie(statuts, names="Statut", values="Nombre", title="Répartition des statuts de paiement", hole=0.4)
    st.plotly_chart(fig, width="stretch")

elif vue == "Catégories":
    st.title("Chiffre d'affaires par catégorie")
    ca = commandes.groupby("category")["discounted_line_total"].sum().sort_values().reset_index()
    ca.columns = ["Catégorie", "Chiffre d'affaires (USD)"]
    fig = px.bar(ca, x="Chiffre d'affaires (USD)", y="Catégorie", orientation="h", height=700)
    st.plotly_chart(fig, width="stretch")
    st.write("Les véhicules, les motos et les montres homme font plus de 80 % du chiffre d'affaires.")

elif vue == "Encaissements":
    st.title("Évolution mensuelle des encaissements")
    mensuel = payes.groupby(payes["payment_date"].dt.to_period("M").astype(str))["amount"].sum().reset_index()
    mensuel.columns = ["Mois", "Montant encaissé (USD)"]
    fig = px.line(mensuel, x="Mois", y="Montant encaissé (USD)", markers=True)
    st.plotly_chart(fig, width="stretch")
    st.write("Le pic de janvier vient des dates inventées par le script de collecte, ce n'est pas une vraie saison.")

elif vue == "Clients":
    st.title("Top clients pseudonymisés")
    nombre = st.slider("Nombre de clients", 5, 20, 10)
    top = payes.groupby("user_id_pseudo")["amount"].sum().sort_values(ascending=False).head(nombre)
    top = top.sort_values().reset_index()
    top.columns = ["Client (pseudonyme)", "Montant encaissé (USD)"]
    fig = px.bar(top, x="Montant encaissé (USD)", y="Client (pseudonyme)", orientation="h")
    st.plotly_chart(fig, width="stretch")
    part = 100 * top["Montant encaissé (USD)"].sum() / payes["amount"].sum()
    st.write(f"Ces {nombre} clients représentent {part:.1f} % de l'argent encaissé.")

else:
    st.title("Paiements et exploration des données")
    choix = st.multiselect("Statuts", ["PAID", "REFUSED", "PENDING"], default=["PAID", "REFUSED", "PENDING"])
    filtre = paiements[paiements["payment_status"].isin(choix)]
    montants = filtre.groupby("payment_status")["amount"].sum().reset_index()
    montants.columns = ["Statut", "Montant (USD)"]
    fig = px.bar(montants, x="Statut", y="Montant (USD)", color="Statut")
    st.plotly_chart(fig, width="stretch")

    categorie = st.selectbox("Catégorie", ["Toutes"] + sorted(commandes["category"].unique()))
    lignes = commandes if categorie == "Toutes" else commandes[commandes["category"] == categorie]
    st.write(f"{len(lignes)} lignes de commande")
    st.dataframe(lignes, width="stretch")
