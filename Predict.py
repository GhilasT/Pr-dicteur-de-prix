import requests
from bs4 import BeautifulSoup

def getsoup(url):
    """
    Prend en entrée l'URL d'une annonce et renvoie la soupe correspondant à cette page HTML.
    
    Parameters:
    url (str): L'URL de l'annonce immobilière
    
    Returns:
    BeautifulSoup: L'objet BeautifulSoup correspondant à la page HTML
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

class NonValide(Exception):
    """
    Exception levée lorsqu'une annonce ne correspond pas aux critères requis.
    Cette exception sera utilisée pour signaler les annonces à éliminer, comme 
    les parkings, fonds de commerce, ou annonces trop peu chères.
    """
    pass

def prix(soup):
    """
    Extrait le prix d'une annonce immobilière à partir de sa soupe.
    
    Parameters:
    soup (BeautifulSoup): La soupe de la page HTML de l'annonce
    
    Returns:
    str: Le prix de l'annonce, sans le symbole "€"
    
    Raises:
    NonValide: Si le prix est inférieur à 10 000€ ou non trouvé
    """
    # Recherche du prix dans la balise <p> avec la classe "product-price"
    prix_element = soup.find("p", class_="product-price")
    
    if prix_element:
        # Extraction du texte du prix
        prix_texte = prix_element.text.strip()
        
        # Suppression du symbole "€" et des espaces
        prix_texte = prix_texte.replace("€", "").replace(" ", "")
        
        try:
            # Conversion en entier pour vérification
            prix_valeur = int(prix_texte)
        except ValueError:
            raise NonValide("Format de prix invalide")
        
        # Vérification du prix minimum
        if prix_valeur < 10000:
            raise NonValide("Prix inférieur à 10 000€")
        
        return prix_texte
    else:
        raise NonValide("Prix non trouvé")

def ville(soup):
    """
    Extrait la ville d'une annonce immobilière à partir de sa soupe.
    
    Parameters:
    soup (BeautifulSoup): La soupe de la page HTML de l'annonce
    
    Returns:
    str: La ville où se trouve le bien immobilier
    """
    # Recherche de l'icône de localisation puis remontée au parent h2
    span_element = soup.find("span", class_="fa-location-dot")
    if span_element:
        h2_element = span_element.find_parent("h2")
        if h2_element:
            # Extraction du texte complet et nettoyage
            localisation_texte = h2_element.get_text(strip=True)
            
            # Découpage pour obtenir la dernière partie après la dernière virgule
            parties = localisation_texte.split(", ")
            if len(parties) > 0:
                return parties[-1]
    
    # Fallback alternatif si la méthode précédente échoue
    balise_ville = soup.find("h2")  # Recherche directe dans le premier h2
    if balise_ville:
        texte = balise_ville.get_text(strip=True)
        if ", " in texte:
            return texte.split(", ")[-1]
    
    return "Ville inconnue"
class NonValide(Exception):
    pass

def get_caracteristiques_section(soup):
    """Récupère la section des caractéristiques"""
    section = soup.find('div', class_='product-features')
    if section:
        return section.find('ul', class_='list-inline')
    return None

def type(soup):
    ul = get_caracteristiques_section(soup)
    if not ul:
        raise NonValide("Section caractéristiques manquante")
    
    for li in ul.find_all('li'):
        label = li.find('span', class_='text-muted')
        if label and 'Type' in label.text:
            valeur = li.find('span', class_='fw-bold').text.strip()
            if valeur not in {"Maison", "Appartement"}:
                raise NonValide(f"Type de bien non valide : {valeur}")
            return valeur
    raise NonValide("Type de bien non trouvé")

def surface(soup):
    ul = get_caracteristiques_section(soup)
    if not ul:
        return "-"
    
    for li in ul.find_all('li'):
        label = li.find('span', class_='text-muted')
        if label and 'Surface' in label.text:
            valeur = li.find('span', class_='fw-bold').text.strip()
            return valeur.replace('m²', '').strip()
    return "-"

def nbrpieces(soup):
    ul = get_caracteristiques_section(soup)
    if not ul:
        return "-"
    
    for li in ul.find_all('li'):
        label = li.find('span', class_='text-muted')
        if label and 'pièces' in label.text:
            valeur = li.find('span', class_='fw-bold').text.strip()
            return valeur
    return "-"

def nbrchambres(soup):
    ul = get_caracteristiques_section(soup)
    if not ul:
        return "-"
    
    for li in ul.find_all('li'):
        label = li.find('span', class_='text-muted')
        if label and 'chambres' in label.text:
            valeur = li.find('span', class_='fw-bold').text.strip()
            return valeur
    return "-"

def nbrsdb(soup):
    ul = get_caracteristiques_section(soup)
    if not ul:
        return "-"
    
    for li in ul.find_all('li'):
        label = li.find('span', class_='text-muted')
        if label:
            label_text = label.text.lower()
            # Gestion de la faute d'orthographe ET des variantes
            if any(keyword in label_text for keyword in ['salle de bain', 'sdb', 'sales de bain']):
                valeur = li.find('span', class_='fw-bold').text.strip()
                return valeur or "-"  # Garde-fou supplémentaire
    
    return "-"

def dpe(soup):
    ul = get_caracteristiques_section(soup)
    if not ul:
        return "-"
    
    for li in ul.find_all('li'):
        label = li.find('span', class_='text-muted')
        if label and ('DPE' in label.text.upper() or 'énergie' in label.text.lower()):
            valeur = li.find('span', class_='fw-bold').text.strip()
            return valeur.split('(')[0].strip()
    return "-"

def informations(soup):
    """
    Agrège toutes les informations d'une annonce immobilière dans un format CSV.
    
    Parameters:
        soup (BeautifulSoup): Objet BeautifulSoup de la page HTML
        
    Returns:
        str: Chaîne formatée "Ville,Type,Surface,NbrPieces,NbrChambres,NbrSdb,DPE,Prix"
        
    Raises:
        NonValide: Si l'annonce est non conforme (type/prix invalides ou manquants)
        
    Exemple:
        "Le Vauclin,Maison,140,5,3,1,-,370000"
        
    Processus:
        1. Extraction séquentielle de chaque caractéristique
        2. Validation automatique via les appels de fonctions existants
        3. Formatage des valeurs manquantes avec '-'
        4. Concaténation finale avec contrôle des exceptions
    """
    try:
        # 1. Extraction de la ville (nécessite une localisation valide)
        ville_val = ville(soup)  # Peut retourner "Ville inconnue" mais ne lève pas d'exception
        
        # 2. Validation du type (lève NonValide si absent/invalide)
        type_val = type(soup)    # Maison/Appartement uniquement
        
        # 3. Extraction des données optionnelles (retournent "-" si manquantes)
        surface_val = surface(soup)          # "140" ou "-"
        nbrpieces_val = nbrpieces(soup)      # "5" ou "-"
        nbrchambres_val = nbrchambres(soup)  # "3" ou "-"
        nbrsdb_val = nbrsdb(soup)            # "1" ou "-"
        dpe_val = dpe(soup)                  # "D" ou "-"
        
        # 4. Validation du prix (lève NonValide si <10k€ ou absent)
        prix_val = prix(soup)    # Format numérique sans "€"
        
    except NonValide as e:
        # Propagation de l'exception avec contexte enrichi
        raise NonValide(f"Annonce non conforme - {str(e)}") from e
    
    # 5. Assemblage des valeurs dans l'ordre requis
    donnees = [
        ville_val,       # Peut être "Ville inconnue"
        type_val,        # Validé
        surface_val,     # "-" si absent
        nbrpieces_val,   # "-" si absent
        nbrchambres_val, # "-" si absent
        nbrsdb_val,      # "-" si absent
        dpe_val,         # "-" si absent
        prix_val         # Validé
    ]
    
    # 6. Conversion en chaîne CSV
    return ",".join(donnees)

print(informations(getsoup("https://www.immo-entre-particuliers.com/annonce-val-de-marne-nogent-sur-marne/409496-magnifique-studio")))