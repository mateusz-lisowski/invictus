package main

import (
	"fmt"
	"io"
	"net/http"
	"time"

	"golang.org/x/net/websocket"
)

type CellSet struct {
	cells []Cell
	color Color
}

type Server struct {
	connection     map[*websocket.Conn]bool
	outputChannel  chan []byte
	cellSetChannel chan CellSet
}

func newServer() *Server {
	return &Server{
		connection:     make(map[*websocket.Conn]bool),
		outputChannel:  make(chan []byte),
		cellSetChannel: make(chan CellSet),
	}
}

func (s *Server) handleBoard(ws *websocket.Conn) {
	for {
		data, ok := <-s.outputChannel
		if !ok {
			fmt.Println("Something went wrong while reading from the channel")
		}
		ws.Write(data)
	}
}

func (s *Server) handlePlay(ws *websocket.Conn) {
	s.connection[ws] = true
	s.readPump(ws)
}

func (s *Server) readPump(ws *websocket.Conn) {
	buffer := make([]byte, 1024)
	for {
		length, err := ws.Read(buffer)
		if err != nil {
			if err == io.EOF {
				break
			}
			fmt.Println("Error while reading from ws: ", err)
		}
		data := buffer[:length]
		fmt.Println(string(data))
	}
}

func pushChangeToChannel(ch chan CellSet) {
	for {
		time.Sleep(time.Second * 1)
		cellSet := CellSet{[]Cell{{1, 1}, {1, 2}, {2, 1}, {2, 2}}, Red}
		ch <- cellSet
	}
}

func main() {

	board := newBoard(4, 4)
	server := newServer()

	go board.play(server.outputChannel)
	go board.setCellsFromChannel(server.cellSetChannel)
	go pushChangeToChannel(server.cellSetChannel)

	http.Handle("/play", websocket.Handler(server.handlePlay))
	http.Handle("/board", websocket.Handler(server.handleBoard))
	http.ListenAndServe(":8080", nil)

}
