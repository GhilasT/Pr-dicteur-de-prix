import pandas as pd
import unicodedata
import re

# Question 8 : Importer le CSV dans un DataFrame
annonces = pd.read_csv('annonces.csv')  # Remplacez par le nom de votre fichier CSV

# Vérification de la conformité des données

# 1. Aperçu des premières lignes
print("=== Aperçu des données ===")
print(annonces.head())

# 2. Vérification des colonnes et types de données
print("\n=== Structure du DataFrame ===")
print(annonces.info())

# 3. Vérification des valeurs manquantes ou "-"
print("\n=== Valeurs manquantes ou '-' ===")
for colonne in annonces.columns:
    count_dash = (annonces[colonne] == '-').sum()
    print(f"{colonne}: {count_dash} occurrence(s) de '-'")

# 4. Vérification des critères de conformité
print("\n=== Critères de conformité ===")

# Prix >= 10 000 €
prix_non_conforme = annonces[annonces['Prix'].astype(int) < 10000]
print(f"Annonces avec prix < 10 000 € : {len(prix_non_conforme)}")

# Type valide (Maison/Appartement)
type_non_valide = annonces[~annonces['Type'].isin(['Maison', 'Appartement'])]
print(f"Annonces avec type non valide : {len(type_non_valide)}")

# Surface, NbrPieces, etc. (vérification des formats numériques)
try:
    annonces['Surface'] = annonces['Surface'].astype(float)
except ValueError as e:
    print(f"Erreur de conversion pour la Surface : {e}")

# Vérification de la présence des colonnes attendues
colonnes_attendues = ['Ville', 'Type', 'Surface', 'NbrPieces', 'NbrChambres', 'NbrSdb', 'DPE', 'Prix']
assert all(col in annonces.columns for col in colonnes_attendues), "Colonnes manquantes !"

annonces["DPE"] = annonces["DPE"].replace("-", "Vierge")

# Vérification
print("=== Vérification après remplacement ===")
print("Valeurs uniques dans DPE :", annonces["DPE"].unique())
print("Nombre de 'Vierge' dans DPE :", (annonces["DPE"] == "Vierge").sum())
# Question 10 : Remplacer les valeurs manquantes par la moyenne
colonnes_a_nettoyer = ["Surface", "NbrPieces", "NbrChambres", "NbrSdb"]

# Conversion des colonnes en numérique (remplacement des '-' par NaN)
for colonne in colonnes_a_nettoyer:
    annonces[colonne] = pd.to_numeric(annonces[colonne], errors="coerce")

# Calcul des moyennes et remplacement des NaN
for colonne in colonnes_a_nettoyer:
    moyenne_colonne = annonces[colonne].mean()
    annonces[colonne].fillna(moyenne_colonne, inplace=True)

# Suppression des lignes avec des valeurs manquantes résiduelles (si besoin)
annonces.dropna(inplace=True)

# Vérification finale
print("=== Vérification après nettoyage ===")
print(annonces.info())
print("\nMoyennes utilisées :")
for colonne in colonnes_a_nettoyer:
    print(f"{colonne} : {annonces[colonne].mean():.2f}")
    
# Question 11 : Création de variables indicatrices (compatible avec pandas < 1.5.0)

# Définir manuellement toutes les catégories possibles pour "DPE"
categories_dpe = ["A", "B", "C", "D", "E", "F", "G", "Vierge"]

# Forcer les catégories manquantes avec pd.Categorical
annonces["DPE"] = pd.Categorical(annonces["DPE"], categories=categories_dpe)

# Appliquer get_dummies() normalement
annonces = pd.get_dummies(
    annonces,
    columns=["Type", "DPE"],
    prefix=["Type", "DPE"],
    dtype=int  # Convertir en 0/1 au lieu de True/False
)

# Vérifier les colonnes générées
print("=== Colonnes après get_dummies() ===")
print(annonces.columns.tolist())

print("\n=== Aperçu des variables indicatrices ===")
print(annonces[["Type_Maison", "Type_Appartement", "DPE_A", "DPE_B", "DPE_C", "DPE_D", "DPE_E", "DPE_F", "DPE_G", "DPE_Vierge"]].head(3))

# Charger le fichier cities.csv avec les colonnes fournies
villes = pd.read_csv("cities.csv")

# Vérification de l'importation
print("=== Colonnes du fichier cities.csv ===")
print(villes.columns.tolist())

print("\n=== Aperçu des données (3 premières lignes) ===")
print(villes[["label", "latitude", "longitude", "department_name", "region_name"]].head(3))

print("\n=== Structure du DataFrame villes ===")
print(villes.info())

# Question 13 : Harmoniser les formats des noms de villes

# Fonction pour nettoyer les noms de villes
def nettoyer_nom_ville(nom):
    # Convertir en minuscules
    nom = nom.lower()
    # Supprimer les accents
    nom = unicodedata.normalize('NFKD', nom).encode('ASCII', 'ignore').decode('utf-8')
    # Remplacer les caractères spéciaux, espaces, tirets et apostrophes
    nom = re.sub(r"[-'’ ,]", "", nom)
    # Cas particulier pour Paris (ex: "Paris 12e" → "paris12")
    if "paris" in nom:
        # Extraire le numéro d'arrondissement (ex: "paris12e" → "paris12")
        nom = re.sub(r"paris(\d+).*", r"paris\1", nom)
    return nom

# Appliquer le nettoyage aux colonnes "Ville" (annonces) et "label" (villes)
annonces["Ville"] = annonces["Ville"].apply(nettoyer_nom_ville)
villes["label"] = villes["label"].apply(nettoyer_nom_ville)

# Vérification des cas particuliers
print("=== Exemples de nettoyage ===")
print("Avant : 'Saint-Étienne' → Après :", nettoyer_nom_ville("Saint-Étienne"))  # → "saintetienne"
print("Avant : 'Nogent-sur-Marne' → Après :", nettoyer_nom_ville("Nogent-sur-Marne"))  # → "nogentsurmarne"
print("Avant : 'Paris 12e' → Après :", nettoyer_nom_ville("Paris 12e"))  # → "paris12"