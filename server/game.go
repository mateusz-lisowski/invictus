package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"sync"
	"time"
	"github.com/google/uuid"
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

type ClientUpdate struct {
	Color		Color 		`json:"color"`
	CellsCount 	int 		`json:"cells"`
	Score		int			`json:"score"`
	Width 		int			`json:"width"`
	Height 		int			`json:"height"`
	Content		[][]Color 	`json:"board"`
}

type Player struct {
	Color      Color `json:"color"`
	CellsCount int   `json:"cells"`
	Score      int   `json:"score"`
	UUID 	   uuid.UUID
}

type Board struct {
	Width   int
	Height  int
	Content [][]Color `json:"board"`
	mutex   sync.Mutex
	Players []Player `json:"players"`
}

func newBoard(h int, w int) *Board {
	board := new(Board)
	board.Width = w
	board.Height = h

	board.Content = make([][]Color, h)

	for i := range board.Content {
		board.Content[i] = make([]Color, w)
		for j := range board.Content[i] {
			board.Content[i][j] = Black
		}
	}

	return board
}


func (b *Board) playerWithUUID(uuid uuid.UUID) *Player {
	var player *Player = nil
	for index := range b.Players {
		if b.Players[index].UUID == uuid {
			player = &b.Players[index]
		}
	}
	return player
}


func newClientUpdate(b *Board, uuid uuid.UUID) *ClientUpdate {
	update := new(ClientUpdate)
	update.Width = b.Width
	update.Height = b.Height
	update.Content = b.Content

	var player = b.playerWithUUID(uuid);
	if (player == nil) {
		return nil
	}

	update.Score = player.Score
	update.CellsCount = player.CellsCount
	update.Color = player.Color
	return update
}

type Cell struct {
	X int `json:"X"` 
	Y int `json:"Y"`
}

func (b *Board) assertIfOutofBounds(cell Cell) error {
	if !b.cellIsInBounds(cell) {
		log.Fatalf("Error: Program stopped: (Cell out of bounds %d %d)", cell.X, cell.Y)
		return errors.New("Cell out of bounds")
	}
	return nil
}

func (b *Board) setCellsToColor(cells []Cell, uuid uuid.UUID) error {

	// TODO: 1) Add cells validation (now you can overwrite other player's cells)
	// TODO: 2) assertOutOfBounds should return an error and stop function before setting anything

	currentPlayer := b.playerWithUUID(uuid)
	if (currentPlayer == nil) {
		return errors.New("Player not found");
	}

	color := currentPlayer.Color

	if len(cells) > currentPlayer.CellsCount {
		log.Printf("Error: Too little cells for player: %s", uuid.String())
		return errors.New("Too little cells")
	}

	b.mutex.Lock()
	defer b.mutex.Unlock()

	for _, cell := range cells {
		err := b.assertIfOutofBounds(cell)
		if (err != nil) {
			return err
		}
		if (b.Content[cell.Y][cell.X] != Black) {
			log.Fatalf("Error: Cell to set is occupied: X:%d Y:%d", cell.X, cell.Y)
			return errors.New("Cell to set is occupied")
		}
	}

	for _, cell := range cells {
		b.Content[cell.Y][cell.X] = color
	}
	currentPlayer.CellsCount -= len(cells)
	return nil
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
	if cell.X < 0 || cell.X >= b.Width || cell.Y < 0 || cell.Y >= b.Height {
		return false
	}
	return true
}

func (b *Board) colorOfCell(cell Cell) Color {
	err := b.assertIfOutofBounds(cell)
	if (err != nil) {
		return 0
	}
	return b.Content[cell.Y][cell.X]
}

func (b *Board) futureColorOfCell(cell Cell) Color {
	err := b.assertIfOutofBounds(cell)
	if (err != nil) {
		return 0
	}
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

	newContent := make([][]Color, b.Height)

	for i := range newContent {
		newContent[i] = make([]Color, b.Width)
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
		b.nextPlayersData()
		time.Sleep(time.Millisecond * 125)

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
		b.setCellsToColor(data.Cells, data.UUID)
	}
}

func (b *Board) getFreeColor(uuid uuid.UUID) (Color, error) {

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
		b.Players = append(b.Players, Player{Color: choosenColor, CellsCount: 0, Score: 0, UUID: uuid})
		return choosenColor, nil
	}

	return 0, errors.New("no free colors aviable")
}

func (b *Board) nextPlayersData() {
	for index := range b.Players {
		b.Players[index].CellsCount += 1
		b.Players[index].Score = 0
		for _, row := range b.Content {
			for _, cell := range row {
				if b.Players[index].Color == cell {
					b.Players[index].Score++
					
				}
			}
		}
	}
}
