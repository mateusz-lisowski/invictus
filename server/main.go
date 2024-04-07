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
  board []int
  possibleColors []int
  usedColors []int
} 

func main() {
	const port int = 8080

	server := newServer()

	http.Handle("/board", websocket.Handler(server.handleBoard))

	fmt.Printf("Listening on port %d\n", port)
	http.ListenAndServe(fmt.Sprintf(":%d", port), nil)
}
