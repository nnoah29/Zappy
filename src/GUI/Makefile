## EPITECH PROJECT, 2024
## B-OOP-400-COT-4-1-tekspice-christian.abiala
## File description:
## Makefile

NAME = zappy_gui

SRC = $(wildcard src/*.cpp)

CXX = g++

CXXFLAGS = -Wall -Wextra -std=c++17 -Iinclude -lsfml-graphics -lsfml-window -lsfml-system

$(NAME):

	$(CXX) $(CXXFLAGS) -o $(NAME) $(SRC)

clean:
	rm -f $(OBJ)

fclean: clean
	rm -f $(NAME)

re: fclean all

all: $(NAME)
