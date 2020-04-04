# Technologie Sieciowe

Aplikacja klienta oraz serwera przetwarzającego działania matematyczne, działająca przez sieć.
Projekt ma na celu zapoznanie się z programowaniem sieciowym, zagrożeniami i problemami wynikającymi z tworzenia systemów rozproszonych oraz aplikacji korzystających z rozległych sieci, takich jak Internet.

```
usage: client.py [-h] [-a N N] [-m N N] [-r N N] [-M N N] [-x | -X]
                 ip_address port

Connect to a remote host and perform calculations.

positional arguments:
  ip_address            IP Address of the server.
  port                  Port through which the data will be sent.

optional arguments:
  -h, --help            show this help message and exit
  -a N N, --add N N     Calculate the sum of two numbers
  -m N N, --multiply N N
                        Multiply two numbers
  -r N N, --random N N  Get a random number from range (inclusive)
  -M N N, --modulo N N  Get modulo operation result
  -x, --sortA           Sort given numbers in ascending order
  -X, --sortD           Sort given numbers in descending order
```

> semestr 3, projekt 1

> 2019 Bartosz Kosmala & Jordan Kondracki
