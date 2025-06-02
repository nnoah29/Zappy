# === CONFIGURATION ===
NAME_SERVER := zappy_server
NAME_GUI    := zappy_gui
NAME_AI     := zappy_ai
LIB_DIR     := lib

CC          := gcc
CXX         := g++
CFLAGS      := -Wall -Wextra -Iincludes
CXXFLAGS    := -std=c++20 -Iincludes -fPIC -fno-gnu-unique
LDFLAGS     := -ldl

SFML_LIBS   := -lsfml-graphics -lsfml-window -lsfml-system

DEBUG ?= 0
ifeq ($(DEBUG),1)
	CFLAGS   += -g -DDEBUG
	CXXFLAGS += -g -DDEBUG
endif

# === VERBOSE SWITCH ===
ifndef V
	SILENT = @
else
	SILENT =
endif

# === PATHS ===
SRC_DIR      := src
INC_DIR      := includes
OBJ_DIR      := obj

SERVER_DIR   := $(SRC_DIR)/SERVER
GUI_DIR      := $(SRC_DIR)/GUI
AI_DIR       := $(SRC_DIR)/AI

# === FILES ===
SERVER_SRCS := $(shell find $(SERVER_DIR) -maxdepth 1 -name '*.c')
SERVER_OBJS := $(SERVER_SRCS:$(SERVER_DIR)/%.c=$(OBJ_DIR)/%.o)

GUI_SRCS    := $(shell find $(GUI_DIR) -name '*.cpp')
GUI_OBJS    := $(GUI_SRCS:$(GUI_DIR)/%.cpp=$(OBJ_DIR)/%.o)

# === COLORS ===
GREEN   := $(shell echo -e "\033[0;32m")
RED     := $(shell echo -e "\033[0;31m")
VIOLET  := $(shell echo -e "\033[0;35m")
BLUE    := $(shell echo -e "\033[0;34m")
NC      := $(shell echo -e "\033[0m")

# === RULES ===
all: $(NAME_SERVER) $(NAME_GUI)
	@echo "$(GREEN)[OK] Full build complete.$(NC)"

$(OBJ_DIR)/%.o: $(SERVER_DIR)/%.c | $(OBJ_DIR)
	$(SILENT)$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR)/%.o: $(GUI_DIR)/%.cpp | $(OBJ_DIR)
	$(SILENT)$(CXX) $(CXXFLAGS) -c $< -o $@

$(NAME_SERVER): $(SERVER_OBJS)
	$(SILENT)$(CC) $(CFLAGS) $^ -o $@
	@echo "$(GREEN)[OK] Server built.$(NC)"

$(NAME_GUI): $(GUI_OBJS)
	$(SILENT)$(CXX) $(CXXFLAGS) $^ -o $@ $(SFML_LIBS)
	@echo "$(GREEN)[OK] GUI built.$(NC)"

$(OBJ_DIR):
	$(SILENT)mkdir -p $(OBJ_DIR)

clean:
	$(SILENT)$(RM) -r $(OBJ_DIR)
	@echo "$(VIOLET)[CLEAN] Object files removed.$(NC)"

fclean: clean
	$(SILENT)$(RM) $(NAME_SERVER) $(NAME_GUI)
	@echo "$(VIOLET)[FCLEAN] Binaries removed.$(NC)"

re: fclean all

.PHONY: all clean fclean re run_ai
