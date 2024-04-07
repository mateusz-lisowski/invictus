package main

import (
	"fmt"
	"net/http"
	"time"

	"golang.org/x/net/websocket"
)

type server struct {
	connections map[*websocket.Conn]bool
}

func newServer() *server {
	return &server{
		connections: make(map[*websocket.Conn]bool),
	}
}

func (s *server) handleBoard(conn *websocket.Conn) {
	fmt.Println("New incoming connection to board handler from client: ", conn.RemoteAddr())
	for {
		payload := fmt.Sprint("board state: ", time.Now())
		conn.Write([]byte(payload))
		time.Sleep(time.Second * 3)
	}
}

type game struct {
  board []string
  possibleColors []string
  usedColors []string
} 

func newGame(boardSize int, possibleColors []string) *game {
  return &game{
    board: make([]string, boardSize),
    possibleColors: possibleColors,
    usedColors: make([]string, len(possibleColors)),
  }
}



func main() {
	const port int = 8080
  const size int = 64
  possibleColors := []string{"red", "green", "blue"}

  game := newGame(size, possibleColors)
  fmt.Println(game)

	server := newServer()

	http.Handle("/board", websocket.Handler(server.handleBoard))

	fmt.Printf("Listening on port %d\n", port)
	http.ListenAndServe(fmt.Sprintf(":%d", port), nil)
}
