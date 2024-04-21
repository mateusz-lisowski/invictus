package main

import (
	"fmt"
	"math/rand"
	"time"
)

func pushRandomValueToChannel(ch chan int) {
	for {
		time.Sleep(time.Second)
		ch <- rand.Intn(100)
	}
}

func printFromChannel(ch chan int) {
	for {
		data, ok := <-ch
		if !ok {
			fmt.Println("Something went wrong while reading from the channel")
		}
		fmt.Println(data)
	}
}

func main() {

	numbersChannel := make(chan int)
	go pushRandomValueToChannel(numbersChannel)
	go printFromChannel(numbersChannel)

	for {
	}

}
