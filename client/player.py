import json
from data import *

class Player:
    def __init__(self, color):
        self.__login(color)
        self.scores = None

    def logout(self):
        response = self.__sendRequest("", {"uuid": self.uuid})
        return response['success']

    def sendMove(self, moves):
        response = self.__sendRequest("", {"board": moves, "uuid": self.uuid})
        return response['success']

    def updateScores(self):
        response = self.__sendRequest("", {"uuid": self.uuid})
        self.scores = response['scores']

    def __login(self, color):
        response = self.__sendRequest("", {"color": color})
        self.uuid = response['uuid']
        self.color = response['color']
        self.__updateBoard()
        self.__updateCells()

    def __updateBoard(self):
        response = self.__sendRequest("", {"uuid": self.uuid})
        self.board = response['board']
        self.board_width = response['width']
        self.board_height = response['height']

    def __updateCells(self):
        response = self.__sendRequest("", {"uuid": self.uuid})
        self.cells = response['cells']

    def __sendRequest(self, url, data):
        #x = requests.post(url, json=data)
        file = open(data_path("data.json"))
        x = json.load(file)
        return x

