package main

import (
	"fmt"
)

func printFromChannel(ch chan []byte) {
	for {
		data, ok := <-ch
		if !ok {
			fmt.Println("Something went wrong while reading from the channel")
		}
		fmt.Println(string(data))
	}
}

func main() {

	board := newBoard(4, 4)
	jsonChannel := make(chan []byte)

	go board.play(jsonChannel)
	go printFromChannel(jsonChannel)

	for {
	}

}
