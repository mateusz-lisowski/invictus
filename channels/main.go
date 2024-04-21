package main

import (
	"fmt"
	"time"
)

type CellSet struct {
	cells []Cell
	color Color
}

func pushChangeToChannel(ch chan CellSet) {
	for {
		time.Sleep(time.Second * 1)
		cellSet := CellSet{[]Cell{{1, 1}, {1, 2}, {2, 1}, {2, 2}}, Red}
		ch <- cellSet
	}
}

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

	outputChannel := make(chan []byte)
	cellSetChannel := make(chan CellSet)

	go board.play(outputChannel)
	go printFromChannel(outputChannel)
	go board.setCellsFromChannel(cellSetChannel)
	go pushChangeToChannel(cellSetChannel)

	for {
	}

}
