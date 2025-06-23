#ifndef GAMEWORLD_HPP
#define GAMEWORLD_HPP

#include <vector>
#include <string>

struct Resource {
    int food, linemate, deraumere, sibur, mendiane, phiras, thystame;
    Resource() : food(0), linemate(0), deraumere(0), sibur(0), 
                 mendiane(0), phiras(0), thystame(0) {}
};

struct Player {
    int id, x, y, orientation, level;
    std::string team;
    Player() : id(-1), x(0), y(0), orientation(1), level(1) {}
};

struct Egg {
    int id, x, y, idn;
    Egg() : id(-1), x(0), y(0) {}
};

struct Tile {
    Resource resources;
    std::vector<int> playerIds;
    std::vector<int> eggIds;
};

class GameWorld {
private:
    int m_width, m_height;
    std::vector<std::vector<Tile>> m_map;
    std::vector<Player> m_players;
    std::vector<Egg> m_eggs;

public:
    bool initialize(int width, int height);
    const Tile &getTile(int x, int y) const;
    void updateTileResources(int x, int y, const Resource &resources);
    void addPlayer(const Player &player);
    void updatePlayerPosition(int playerId, int x, int y, int orientation);
    void removePlayer(int playerId);
    void addEgg(const Egg &egg);
    void removeEgg(int eggId);
    Player *findPlayer(int playerId);
    bool isValidPosition(int x, int y) const;
    void updateResource(int, int, int, int);
    void updatePlayerLevel(int, int);
    int getWidth() const { return m_width; }
    int getHeight() const { return m_height; }
    const std::vector<Player> &getPlayers() const { return m_players; }
    const std::vector<Egg> &getEggs() const { return m_eggs; }
    void addTeam(const std::string &teamName, Player *player = nullptr);
};

#endif
