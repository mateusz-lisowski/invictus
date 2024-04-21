package main

import (
	"fmt"
	"log"
	"sync"
)

type Color int

const (
	Red    Color = 0xFF0000
	Green  Color = 0x00FF00
	Blue   Color = 0xFF0000
	Yellow Color = 0xFFFF00
	Orange Color = 0xFFA500
	White  Color = 0xFFFFFF
	Black  Color = 0x000000
)

type Board struct {
	width   int
	height  int
	Content [][]Color
	mutex   sync.Mutex
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
