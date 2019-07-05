import requests
from bs4 import BeautifulSoup

r = requests.get('http://www.livescores.com/soccer/iran/persian-gulf-league/results/all/')
markup = r.text
soup = BeautifulSoup(markup, 'html.parser')
games = soup.find_all("div", class_="row-gray")

for game in games:
    lhs_name = game.find("div", class_="ply tright name").contents[0]
    rhs_name = game.find("div", class_="ply name").contents[0]
    score_tag = game.find("div", class_="sco")
    if score_tag.find("a", class_="scorelink") is not None:
        score_tag = score_tag.find("a", class_="scorelink")
    score = score_tag.contents[0]

    print(lhs_name, score, rhs_name)







