# RepCRec
Advanced Database topics NYU fall 2022 final project

## Usage
``` bash
> python3 repcrec.py -h
usage: repcrec [-h] [-i] [filename]

Distributed replicated concurrency control and recovery

positional arguments:
  filename           input filename

options:
  -h, --help         show this help message and exit
  -i, --interactive  enter interactive mode(enter exit to quit)
```

## Example

Run `repcrec` as a Python script
``` bash
> python3 repcrec.py tests/test7.txt
x1: 10
x2: 20
x3: 30
```

Run `repcrec` within interactive mode
```
> python3 repcrec.py -i

  _ __ ___ _ __   ___ _ __ ___  ___ 
 | '__/ _ \ '_ \ / __| '__/ _ \/ __|
 | | |  __/ |_) | (__| | |  __/ (__ 
 |_|  \___| .__/ \___|_|  \___|\___|
          |_|                 
    
  Advanced Database Systems, CSCI-GA.2434-001, NYU, Fall 2022
  professor: Dennis Shasha   
  author: Xiaohan Wu, Yulin Hu

> begin(t1)
> R(t1, x2)
x2: 20
> end(t1)
> exit
Bye~
```
