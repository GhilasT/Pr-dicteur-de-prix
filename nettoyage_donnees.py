import pandas as pd

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