package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"sync"
	"time"
)

type Color int

const (
	Blue    Color = 1
	Green   Color = 2
	Cyan    Color = 3
	Red     Color = 4
	Magenta Color = 5
	Yellow  Color = 6
	Black   Color = 0
)

type Player struct {
	Color      Color `json:"color"`
	CellsCount int   `json:"cells"`
	Score      int   `json:"score"`
}

type Board struct {
	width   int
	height  int
	Content [][]Color `json:"board"`
	mutex   sync.Mutex
	Players []Player `json:"players"`
}

func newBoard(h int, w int) *Board {
	board := new(Board)
	board.width = w
	board.height = h

	board.Content = make([][]Color, h)

	for i := range board.Content {
		board.Content[i] = make([]Color, w)
		for j := range board.Content[i] {
			board.Content[i][j] = Black
		}
	}

	return board
}

type Cell struct {
	X, Y int
}

func (b *Board) assertIfOutofBounds(cell Cell) {
	if !b.cellIsInBounds(cell) {
		log.Fatalf("Error: Program stopped: (Cell out of bounds %d %d)", cell.X, cell.Y)
	}
}

func (b *Board) setCellsToColor(cells []Cell, color Color) {
	b.mutex.Lock()
	defer b.mutex.Unlock()

	for _, cell := range cells {
		b.assertIfOutofBounds(cell)
		b.Content[cell.Y][cell.X] = color
	}
}

func (b *Board) print() {
	for _, row := range b.Content {
		for _, cell := range row {
			fmt.Print(cell, " ")
		}
		fmt.Println()
	}
}

func (b *Board) cellIsInBounds(cell Cell) bool {
	if cell.X < 0 || cell.X >= b.width || cell.Y < 0 || cell.Y >= b.height {
		return false
	}
	return true
}

func (b *Board) colorOfCell(cell Cell) Color {
	b.assertIfOutofBounds(cell)
	return b.Content[cell.Y][cell.X]
}

func (b *Board) futureColorOfCell(cell Cell) Color {
	b.assertIfOutofBounds(cell)

	neighborCells := []Cell{
		{cell.X + 1, cell.Y + 1},
		{cell.X + 1, cell.Y + 0},
		{cell.X + 1, cell.Y - 1},

		{cell.X - 1, cell.Y + 1},
		{cell.X - 1, cell.Y + 0},
		{cell.X - 1, cell.Y - 1},

		{cell.X + 0, cell.Y + 1},
		{cell.X + 0, cell.Y - 1},
	}

	var ownColor = b.colorOfCell(cell)
	var neighboarColors []Color

	for _, neighboar := range neighborCells {
		if !b.cellIsInBounds(neighboar) {
			continue
		}
		if b.colorOfCell(neighboar) == Black {
			continue
		}
		neighboarColors = append(neighboarColors, b.colorOfCell(neighboar))
	}

	if len(neighboarColors) < 2 {
		return Black
	}

	if len(neighboarColors) > 3 {
		return Black
	}

	potentialColor := neighboarColors[0]

	for _, neighboarColor := range neighboarColors {
		if neighboarColor != potentialColor {
			return Black
		}
	}

	if len(neighboarColors) == 2 {
		return ownColor
	}
	if ownColor == Black && len(neighboarColors) == 3 {
		return potentialColor
	}
	return ownColor
}

func (b *Board) nextTick() {
	b.mutex.Lock()
	defer b.mutex.Unlock()

	newContent := make([][]Color, b.height)

	for i := range newContent {
		newContent[i] = make([]Color, b.width)
		for j := range newContent[i] {
			newContent[i][j] = b.futureColorOfCell(Cell{X: j, Y: i})
		}
	}

	b.Content = newContent
}

func (b *Board) play(boardChannel chan []byte) {
	for {

		b.print()
		b.nextTick()
		time.Sleep(time.Second)

		jsonBoard, err := json.Marshal(b)
		if err != nil {
			fmt.Println("Error:", err)
		}
		boardChannel <- jsonBoard

	}
}

func (b *Board) setCellsFromChannel(cellSet chan CellSet) {
	for {
		data, ok := <-cellSet
		if !ok {
			fmt.Println("Something went wrong while reading from the channel")
		}
		b.setCellsToColor(data.Cells, data.Color)
	}
}

func (b *Board) getFreeColor() (Color, error) {

	possibleColors := []Color{Blue, Green, Cyan, Red, Magenta, Yellow}

	for _, player := range b.Players {
		newColors := []Color{}
		for _, c := range possibleColors {
			if c != player.Color {
				newColors = append(newColors, c)
			}
		}
		possibleColors = newColors
	}

	if len(possibleColors) >= 1 {
		choosenColor := possibleColors[0]
		b.Players = append(b.Players, Player{Color: choosenColor, CellsCount: 0, Score: 0})
		return choosenColor, nil
	}

	return 0, errors.New("no free colors aviable")
}

func (b *Board) getPlayerScore() int {
	return 0
}

func (b *Board) getPlayerCellsNumber() int {
	return 0
}
