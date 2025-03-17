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



print(nbrpieces(getsoup("https://www.immo-entre-particuliers.com/annonce-martinique-le-vauclin/409025-vends-maison-sur-la-plage-de-pointe-faula-martinique")))