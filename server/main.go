package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"golang.org/x/net/websocket"
	"github.com/google/uuid"
)

type CellSet struct {
	Cells []Cell 	 `json:"cells"`
	UUID  uuid.UUID  `json:"uuid"`
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
	uuid := uuid.New()
	freeColor, index, err := s.board.getFreeColor(uuid)
	if err != nil {
		fmt.Println(err)
	}
	
	data := map[string]interface{}{
		"color":    freeColor,
		"id": 		index,
		"uuid":   	uuid.String(),
	}

	jsonData, err := json.Marshal(data)
	fmt.Fprintf(w, "%s", jsonData)
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
			// fmt.Println("Error while reading from ws: ", err)
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

	board := newBoard(256, 144)
	server := newServer(board)

	mux := http.NewServeMux()

	go board.play(server.gameChannel)
	go board.setCellsFromChannel(server.cellSetChannel)

	
	mux.Handle("/play", websocket.Handler(server.handlePlay))
	
	mux.Handle("/game1", websocket.Handler(server.handleBoard))
	mux.Handle("/game2", websocket.Handler(server.handleBoard))
	mux.Handle("/game3", websocket.Handler(server.handleBoard))
	mux.Handle("/game4", websocket.Handler(server.handleBoard))
	mux.Handle("/game5", websocket.Handler(server.handleBoard))
	mux.Handle("/game6", websocket.Handler(server.handleBoard))

	mux.HandleFunc("GET /register", server.handleRegister)

	http.ListenAndServe(":8080", mux)

}
