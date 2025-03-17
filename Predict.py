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
def get_caracteristiques_section(soup):
    """
    Trouve la section des caractéristiques à partir du header "Caractéristiques".
    Retourne la balise <ul> contenant les données ou None si non trouvée.
    """
    header = soup.find(lambda tag: tag.name in ['h2', 'h3', 'div'] 
                       and "Caractéristiques" in tag.text)
    return header.find_next('ul') if header else None

def type(soup):
    section = get_caracteristiques_section(soup)
    if not section:
        raise NonValide("Section caractéristiques manquante")
    
    for li in section.find_all('li'):
        if 'type' in li.text.lower():
            valeur = li.get_text(strip=True).split(':', 1)[-1].strip()
            if valeur not in {"Maison", "Appartement"}:
                raise NonValide(f"Type invalide : {valeur}")
            return valeur
    raise NonValide("Type non trouvé")



print(get_caracteristiques_section(getsoup("https://www.immo-entre-particuliers.com/annonce-martinique-le-francois/409505-terrain-viabilise")))