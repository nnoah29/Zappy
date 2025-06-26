## EPITECH PROJECT, 2024
## B-OOP-400-COT-4-1-tekspice-christian.abiala
## File description:
## Makefile

NAME = zappy_gui

SRC = src/main.cpp \
	  src/Gui_client.cpp \
	  src/Network.cpp \
	  src/Parser.cpp \
	  src/Game_world.cpp \
	  src/AnimationSystem.cpp \
	  src/Core.cpp \
	  src/Input_handler.cpp \
	  src/RenderingEngine.cpp \
	  src/PlayerInfoPanel.cpp \
	  src/Ressource_manager.cpp

OBJ = $(SRC:.cpp=.o)

CXX = g++
CXXFLAGS = -Wall -Wextra -std=c++20 -Iinclude -g3
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