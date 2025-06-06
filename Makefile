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

# Python configuration
PYTHON          := python3
PIP             := pip3
PYINSTALLER     := $(PYTHON) -m PyInstaller
AI_REQUIREMENTS := src/ai/requirements.txt

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
AI_DIR       := $(SRC_DIR)/ai

# === FILES ===
SERVER_SRCS := $(shell find $(SERVER_DIR) -maxdepth 1 -name '*.c')
SERVER_OBJS := $(SERVER_SRCS:$(SERVER_DIR)/%.c=$(OBJ_DIR)/%.o)

GUI_SRCS    := $(shell find $(GUI_DIR) -name '*.cpp')
GUI_OBJS    := $(GUI_SRCS:$(GUI_DIR)/%.cpp=$(OBJ_DIR)/%.o)

# === COLORS ===
GREEN  := $(shell echo -e "\033[0;32m")
RED    := $(shell echo -e "\033[0;31m")
VIOLET := $(shell echo -e "\033[0;35m")
BLUE   := $(shell echo -e "\033[0;34m")
NC     := $(shell echo -e "\033[0m")

# === RULES ===
all: $(NAME_SERVER) setup_ai
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

# === Python AI Rules ===
setup_ai: build_ai
	@echo "$(BLUE)[SETUP] Installing Python dependencies...$(NC)"
	$(SILENT)$(PIP) install -r $(AI_REQUIREMENTS)
	@echo "$(GREEN)[OK] Python dependencies installed.$(NC)"

build_ai: setup_ai
	@echo "$(BLUE)[BUILD] Building AI binary...$(NC)"
	$(SILENT)cd $(AI_DIR) && $(PYINSTALLER) --onefile --name $(NAME_AI) main.py
	$(SILENT)mv $(AI_DIR)/dist/$(NAME_AI) .
	$(SILENT)rm -rf $(AI_DIR)/build $(AI_DIR)/dist $(AI_DIR)/$(NAME_AI).spec
	@echo "$(GREEN)[OK] AI binary built.$(NC)"

test_ai:
	@echo "$(BLUE)[TEST] Running AI tests...$(NC)"
	$(SILENT)$(PYTHON) -m pytest $(AI_DIR)/tests -v

clean_ai:
	@echo "$(VIOLET)[CLEAN] Cleaning Python cache files...$(NC)"
	$(SILENT)find $(AI_DIR) -type f -name "*.pyc" -delete
	$(SILENT)find $(AI_DIR) -type d -name "__pycache__" -delete
	$(SILENT)rm -rf ".pytest_cache"
	$(SILENT)find $(AI_DIR) -type d -name "*.egg-info" -delete
	$(SILENT)find $(AI_DIR) -type d -name ".pytest_cache" -delete
	$(SILENT)find $(AI_DIR) -type d -name ".coverage" -delete
	$(SILENT)rm -f $(NAME_AI)

clean: clean_ai
	$(SILENT)$(RM) -r $(OBJ_DIR)
	@echo "$(VIOLET)[CLEAN] Object files removed.$(NC)"

fclean: clean
	$(SILENT)$(RM) $(NAME_SERVER) $(NAME_GUI) $(NAME_AI)
	@echo "$(VIOLET)[FCLEAN] Binaries removed.$(NC)"

re: fclean all

.PHONY: all clean fclean re setup_ai test_ai clean_ai build_ai
