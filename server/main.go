package main

import (
	"encoding/json"
	"fmt"
	"time"
)

// import (
// 	"flag"
// 	"log"
// 	"net/http"
// )

// var addr = flag.String("addr", ":8080", "http service address")

// func serveHome(w http.ResponseWriter, r *http.Request) {
// 	log.Println(r.URL)
// 	if r.URL.Path != "/" {
// 		http.Error(w, "Not found", http.StatusNotFound)
// 		return
// 	}
// 	if r.Method != http.MethodGet {
// 		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
// 		return
// 	}
// 	http.ServeFile(w, r, "home.html")
// }

func main() {

	// flag.Parse()
	// hub := newHub()

	// go hub.run()

	// http.HandleFunc("/", serveHome)
	// http.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
	// 	serveWs(hub, w, r)
	// })

	// server := &http.Server{
	// 	Addr:              *addr,
	// 	ReadHeaderTimeout: 3 * time.Second,
	// }

	// err := server.ListenAndServe()
	// if err != nil {
	// 	log.Fatal("ListenAndServe: ", err)
	// }

	board := newBoard(4, 4)
	board.setCellsToColor([]Cell{{1, 1}, {2, 1}, {1, 2}, {2, 2}}, Red)
	for {
		board.print()
		board.nextTick()
		time.Sleep(time.Second)
		jsonData, err := json.Marshal(board)
		if err != nil {
			fmt.Println("Error:", err)
			return
		}
		fmt.Println(string(jsonData))
	}

}
