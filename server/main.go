package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"golang.org/x/net/websocket"
)

type CellSet struct {
	Cells []Cell `json:"cells"`
	Color Color  `json:"color"`
}

type Server struct {
	connection     map[*websocket.Conn]bool
	gameChannel    chan []byte
	cellSetChannel chan CellSet
	board          *Board
}

func newServer(b *Board) *Server {
	return &Server{
		connection:     make(map[*websocket.Conn]bool),
		gameChannel:    make(chan []byte),
		cellSetChannel: make(chan CellSet),
		board:          b,
	}
}

func (s *Server) handleRegister(w http.ResponseWriter, r *http.Request) {
	freeColor, err := s.board.getFreeColor()
	if err != nil {
		fmt.Println(err)
	}
	fmt.Fprint(w, freeColor)
}

func (s *Server) handleBoard(ws *websocket.Conn) {
	for {
		data, ok := <-s.gameChannel
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
	server := newServer(board)

	mux := http.NewServeMux()

	go board.play(server.gameChannel)
	go board.setCellsFromChannel(server.cellSetChannel)

	mux.Handle("/play", websocket.Handler(server.handlePlay))
	mux.Handle("/game", websocket.Handler(server.handleBoard))

	mux.HandleFunc("GET /register", server.handleRegister)

	http.ListenAndServe(":8080", mux)

}
