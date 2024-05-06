import json
from websocket import create_connection
import requests
import threading

serverAddr = "localhost:8080"

class Player:
    def __init__(self):
        self.__login()
        self.ws = create_connection(f"ws://{serverAddr}/game")
        self.ws2 = create_connection(f"ws://{serverAddr}/play")
        result = json.loads(self.ws.recv())
        self.__updateBoard(result)
        self.__updateCells(result)

    def start(self):
        t = threading.Thread(target=self.__update)
        t.start()

    def sendMove(self, moves):
        output_list = [{"X": x, "Y": y} for x, y in moves]
        self.ws2.send(json.dumps({"cells": output_list, "uuid": self.uuid}))

    def __update(self):
        while True:
            result = self.ws.recv()
            result = json.loads(self.ws.recv())
            self.__updateScores(result)
            self.__updateBoard(result)
            self.__updateCells(result)

    def __login(self):
        response = requests.get(f"http://{serverAddr}/register")
        self.color = response.json()["color"]
        self.uuid = response.json()["uuid"]

    def __updateBoard(self, response):
        self.board = response['board']
        self.board_width = len(self.board)
        self.board_height = len(self.board[0])

    def __updateCells(self, response):
        self.cells = response['players'][0]['cells']

    def __updateScores(self, response):
        self.scores = response['players'][0]['score']
