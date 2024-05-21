GOOS=windows GOARCH=386 go build -o server_x86.exe
GOOS=windows GOARCH=amd64 go build -o server_amd.exe
GOOS=linux GOARCH=386 go build -o server_x86.bin
GOOS=linux GOARCH=amd64 go build -o server_amd.bin

