#ifndef GAMEWORLD_HPP
#define GAMEWORLD_HPP

#include <vector>
#include <string>

struct Resource {
    int food;
    int linemate;
    int deraumere;
    int sibur;
    int mendiane;
    int phiras;
    int thystame;
    
    Resource() : food(0), linemate(0), deraumere(0), sibur(0), 
                 mendiane(0), phiras(0), thystame(0) {}
};

struct Player {
    int id;
    int x;
    int y;
    int orientation;
    int level;
    std::string team;

    Player() : id(-1), x(0), y(0), orientation(1), level(1), team("") {}
    Player(int playerId, int posX, int posY, int orient, int playerLevel, const std::string &teamName)
        : id(playerId), x(posX), y(posY), orientation(orient), level(playerLevel), team(teamName) {}
};

struct Egg {
    int id;
    int x;
    int y;
    std::string team;
    
    Egg() : id(-1), x(0), y(0), team("") {}
    Egg(int eggId, int posX, int posY, const std::string &teamName)
        : id(eggId), x(posX), y(posY), team(teamName) {}
};

struct Tile {
    Resource resources;
    std::vector<int> playerIds;
    std::vector<int> eggIds;

    Tile() {}
};

class GameWorld {
private:
    int m_width;
    int m_height;
    std::vector<std::vector<Tile>> m_map;
    std::vector<Player> m_players;
    std::vector<Egg> m_eggs;
    std::vector<std::string> m_teams;

public:
    GameWorld();
    ~GameWorld();
    
    bool initialize(int width, int height);
    void clear();
    int getWidth() const;
    int getHeight() const;
    const Tile &getTile(int x, int y) const;
    const std::vector<Player> &getPlayers() const;
    const std::vector<Egg> &getEggs() const;
    const std::vector<std::string> &getTeams() const;
    void addTeam(const std::string &teamName);
    void updateTileResources(int x, int y, const Resource &resources);
    void addPlayer(const Player &player);
    void updatePlayerPosition(int playerId, int x, int y, int orientation);
    void updatePlayerLevel(int playerId, int level);
    void removePlayer(int playerId);
    Player *findPlayer(int playerId);
    void addEgg(const Egg &egg);
    void removeEgg(int eggId);
    Egg* findEgg(int eggId);
    bool isValidPosition(int x, int y) const;
    void movePlayerOnMap(int playerId, int oldX, int oldY, int newX, int newY);
    void moveEggOnMap(int eggId, int oldX, int oldY, int newX, int newY);
};

#endif
