import json
from data import *
from websocket import create_connection
import requests
import threading
import asyncio

serverAddr = "http://localhost:8080"
class Player:
    def __init__(self, color):
        self.__login(color)
        self.ws = create_connection("ws://localhost:8080/game")
        self.ws2 = create_connection("ws://localhost:8080/play")
        print(self.ws.connected)
        result = self.ws.recv()
        result = json.loads(self.ws.recv())
        self.__updateBoard(result)
        self.__updateCells(result)
        t = threading.Thread(target=self.update)
        t.start()
        #asyncio.run(self.update(self.ws))
        self.scores = None

    def logout(self):
        response = self.__sendRequest("", {"uuid": self.uuid})
        return response['success']

    def update(self):
        while True:
            result = self.ws.recv()
            result = json.loads(self.ws.recv())
            print("board: "+str(self.board))
            self.__updateScores(result)
            self.__updateBoard(result)
            self.__updateCells(result)

    def sendMove(self, moves):
        output_list = [{"X": x, "Y": y} for x, y in moves]
        self.ws2.send(json.dumps({"cells": output_list, "uuid": self.uuid}))
        print("send")
        print(json.dumps({"board": moves, "uuid": self.uuid}))
        response = self.__sendRequest("", {"board": moves, "uuid": self.color})
        return response['success']

    def __login(self, color):
        response = requests.get(serverAddr+"/register")
        print(response.json())
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

    def __sendRequest(self, url, data):
        #x = requests.post(url, json=data)
        file = open(data_path("data.json"))
        x = json.load(file)
        return x

