package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"golang.org/x/net/websocket"
)

type CellSet struct {
	Cells []Cell
	Color Color
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
			continue
		}

		data := buffer[:length]
		var cellSetData CellSet

		err = json.Unmarshal(data, &cellSetData)
		if err != nil {
			fmt.Println("Error unmarshalling data:", err)
		} else {
			s.cellSetChannel <- cellSetData
		}

	}
}

func main() {

	board := newBoard(4, 4)
	server := newServer()

	go board.play(server.outputChannel)
	go board.setCellsFromChannel(server.cellSetChannel)

	http.Handle("/play", websocket.Handler(server.handlePlay))
	http.Handle("/board", websocket.Handler(server.handleBoard))
	http.ListenAndServe(":8080", nil)

}
