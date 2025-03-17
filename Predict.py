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

print(getsoup("https://www.seloger.com/annonces/achat/appartement/paris-17eme-75/monceau-wagram/157073189.htm"))