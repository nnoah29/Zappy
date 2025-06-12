## EPITECH PROJECT, 2024
## B-OOP-400-COT-4-1-tekspice-christian.abiala
## File description:
## Makefile

NAME = zappy_gui

SRC = $(wildcard src/*.cpp)
OBJ = $(SRC:.cpp=.o)

CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++17 -Iinclude
LDFLAGS = -lsfml-graphics -lsfml-window -lsfml-system -lpthread

$(NAME): $(OBJ)
	$(CXX) $(OBJ) -o $(NAME) $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ)

fclean: clean
	rm -f $(NAME)

re: fclean all

all: $(NAME)