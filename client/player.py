import json
from websocket import create_connection
import requests
import threading

from config import *

class Player:
    def __init__(self):
        self.__login()
        if self.id == 0:
            return
        self.ws = create_connection(f"ws://{serverIp()}:{serverPort()}/game{self.id}")
        self.ws2 = create_connection(f"ws://{serverIp()}:{serverPort()}/play")
        result = self.ws.recv()
        result = json.loads(self.ws.recv())
        self.__updateBoard(result)
        self.__updateCells(result)
        self.disconnected = False

    def start(self):
        self.update_thread = threading.Thread(target=self.__update)
        self.update_thread.start()

    def sendMove(self, moves):
        output_list = [{"X": x, "Y": y} for x, y in moves]
        try:
            self.ws2.send(json.dumps({"cells": output_list, "uuid": self.uuid}))
        except:
            self.disconnected = True

    def __update(self):
        try:
            while True:
                result = json.loads(self.ws.recv())
                self.__updateScores(result)
                self.__updateBoard(result)
                self.__updateCells(result)
        except:
            self.disconnected = True

    def __login(self):
        response = requests.get(f"http://{serverIp()}:{serverPort()}/register")
        self.color = response.json()["color"]
        self.uuid = response.json()["uuid"]
        self.id = response.json()["id"]

    def __updateBoard(self, response):
        self.board = response['board']
        self.board_width = len(self.board[0])
        self.board_height = len(self.board)

    def __updateCells(self, response):
        self.cells = response['players'][0]['cells']

    def __updateScores(self, response):
        self.scores = response['players'][0]['score']
