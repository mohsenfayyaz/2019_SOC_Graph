import requests
from bs4 import BeautifulSoup
from bs4 import NavigableString

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

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
        self.hamilton_path_team_names = list()

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

    def find_hamilton_path(self):
        hamilton_path_team_names = [next(iter(self.games_graph))]
        for new_team_name, to_teams in self.games_graph.items():
            v1 = hamilton_path_team_names[0]
            vn = hamilton_path_team_names[-1]
            if v1 in to_teams:  # Edge From new node to v1 -> add new v in the beginning of path
                hamilton_path_team_names.insert(0, new_team_name)
                continue
            if new_team_name in self.games_graph[vn]:  # Edge From vn to new node -> add new v in the end of path
                hamilton_path_team_names.append(new_team_name)
                continue

            path_index = dict()
            i = 0
            for team in hamilton_path_team_names:
                path_index[team] = i
                i += 1

            min_index_team = len(hamilton_path_team_names)
            for v in to_teams:
                if v in path_index and path_index[v] < min_index_team:
                    min_index_team = path_index[v]  # First team in path that new v has edge to it
            hamilton_path_team_names.insert(min_index_team, new_team_name)

        self.hamilton_path_team_names = hamilton_path_team_names
        print(hamilton_path_team_names)

    def draw_graph(self):
        # ------- DIRECTED

        # Build a dataframe with your connections
        # This time a pair can appear 2 times, in one side or in the other!
        edges = list()
        for team_name, to_teams in self.games_graph.items():
            for to_team_name in to_teams:

                edges.append((team_name, to_team_name))

        red_edges = list()
        old_team_name = None
        for team_name in self.hamilton_path_team_names:
            if old_team_name is not None:
                red_edges.append((old_team_name, team_name))
            old_team_name = team_name


        G = nx.DiGraph()
        G.add_edges_from(edges)
        black_edges = [edge for edge in G.edges()]

        # Need to create a layout when doing
        # separate calls to draw nodes and edges
        pos = nx.circular_layout(G)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_color='#73F4EA', node_size=5000, node_shape="s")
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color="r", arrows=True, width=4, alpha=0.5)
        nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=True)
        plt.show()


my_network_handler = NetworkHandler()
games_list = my_network_handler.get_games()
graph = Graph()
games_graph = graph.make_games_graph(games_list)
print("Rules are followed" if graph.has_every_pair_played() else "Rules are broken")
graph.find_hamilton_path()
graph.draw_graph()