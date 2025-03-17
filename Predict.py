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
    
print(prix(getsoup("https://www.immo-entre-particuliers.com/annonce-martinique-le-francois/409505-terrain-viabilise")))