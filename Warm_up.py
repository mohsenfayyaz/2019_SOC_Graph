import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString

URL = 'http://www.livescores.com/soccer/iran/persian-gulf-league/results/all/'
GAMES_LIMIT = 120


class NetworkHandler:
    def __init__(self):
        pass

    @staticmethod
    def get_games():
        markup = requests.get(URL).text
        soup = BeautifulSoup(markup, 'html.parser')
        games = soup.find_all("div", class_="row-gray")
        counter = 0
        games_list = list()
        for game in games:
            try:
                lhs_name = game.find("div", class_="ply tright name").contents[0]
                rhs_name = game.find("div", class_="ply name").contents[0]
                score_tag = game.find("div", class_="sco")
                if score_tag.find("a", class_="scorelink") is not None:
                    score_tag = score_tag.find("a", class_="scorelink")
                score = score_tag.contents[0]

                if "?" not in score:
                    if counter < GAMES_LIMIT:
                        games_list.append([lhs_name.strip(), score.strip(), rhs_name.strip()])
                    counter += 1
                else:
                    pass

            except NavigableString:
                pass

        return games_list


class Graph:
    def __init__(self):
        self.games_graph = dict()

    def add_edge(self, from_name, to_name):
        if from_name not in self.games_graph:
            self.games_graph[from_name] = list()
        if to_name not in self.games_graph:
            self.games_graph[to_name] = list()
        if to_name not in self.games_graph[from_name]:
            self.games_graph[from_name].append(to_name)

    def make_games_graph(self, games_list):
        for game in games_list:
            lhs_name = game[0]
            rhs_name = game[2]
            lscore = game[1].split()[0]
            rscore = game[1].split()[0]
            if lscore >= rscore:
                self.add_edge(rhs_name, lhs_name)  # From LOSER to WINNER
            else:
                self.add_edge(lhs_name, rhs_name)
        return self.games_graph

    @staticmethod
    def inc_games_played(games_played, team_name):
        if team_name not in games_played:
            games_played[team_name] = 0
        games_played[team_name] += 1
        return games_played

    def has_every_pair_played(self):
        games_played = dict()
        for team_name, winner_teams in self.games_graph.items():
            for winner_name in winner_teams:
                games_played = self.inc_games_played(games_played, team_name)
                games_played = self.inc_games_played(games_played, winner_name)

        for team_name, games_played_count in games_played.items():
            if games_played_count != (len(games_graph) - 1):
                return False
        return True


my_network_handler = NetworkHandler()
games_list = my_network_handler.get_games()
graph = Graph()
games_graph = graph.make_games_graph(games_list)
print("Rules are followed" if graph.has_every_pair_played() else "Rules are broken")
