from websocket import create_connection
import requests
import asyncio
import json
import uuid

serverAddr = "http://localhost:8080"
response = requests.get(serverAddr+"/register")
print("response: "+str(response.json()))
id =  response.json()['uuid']
print("uuid: "+str(id))

serverAddr = "127.0.0.1:8080"
ws = create_connection("ws://localhost:8080/game")
print("/game connection: "+str(ws.connected))
ws2 = create_connection("ws://localhost:8080/play")
print("/play connection: "+str(ws.connected))
result = ws.recv()
print(result)
result = ws.recv()
print(result)
result = json.loads(ws.recv())
cells = result["players"][0]["cells"]
print(cells)
while cells<1:
    result = ws.recv()
    result = json.loads(ws.recv())
    print("available cells: "+str(result["players"][0]["cells"]))
    cells = result["players"][0]["cells"]

ws2.send(json.dumps({"cells": [{"X":1,"Y":1}], "uuid": id}))
print("sent: "+str(json.dumps({"cells": [{"X":2,"Y":2}], "uuid": id})))
#ws2.send(json.dumps({"cells": [[0,1]], "color": 1}))

