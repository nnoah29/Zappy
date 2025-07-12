#ifndef GAMEWORLD_HPP
#define GAMEWORLD_HPP

#include <vector>
#include <string>
#include <memory>
#include <unordered_map> // NOUVEAU

#include "../Network/Network.hpp"
#include "../Animations/AnimationSystem.hpp"
#include "../RenderEngine/RenderingEngine.hpp"

class RenderingEngine;

// NOUVEAU : Enum pour des types de ressources explicites


struct Resource {
    int food, linemate, deraumere, sibur, mendiane, phiras, thystame;
    Resource() : food(0), linemate(0), deraumere(0), sibur(0),
                 mendiane(0), phiras(0), thystame(0) {}
};

struct PlayerInventory {
    int food, linemate, deraumere, sibur, mendiane, phiras, thystame;
    int lifeUnits;
    PlayerInventory() : food(0), linemate(0), deraumere(0), sibur(0),
                       mendiane(0), phiras(0), thystame(0), lifeUnits(1260) {}
};

struct Player {
    int id, x, y, orientation, level;
    std::string team;
    PlayerInventory inventory;
    float scale;
    Player() : id(-1), x(0), y(0), orientation(1), level(1), scale(1.0f) {}
};

struct Egg {
    int id, x, y, idn{};
    std::string team;
    Egg() : id(-1), x(0), y(0) {}
};

struct Tile {
    Resource resources;
    std::vector<int> playerIds;
    std::vector<int> eggIds;
};

class GameWorld {
private:
    int m_width = 0, m_height = 0;
    std::vector<std::vector<Tile>> m_map;

    std::unordered_map<int, Player> m_players;
    std::vector<Egg> m_eggs;
    std::shared_ptr<Network> m_network;
    AnimationSystem* m_animationSystem = nullptr;
    RenderingEngine* m_renderingEngine = nullptr;

public:
    std::vector<std::string> m_playerTeams;
    enum class ResourceType {
        Food = 0,
        Linemate,
        Deraumere,
        Sibur,
        Mendiane,
        Phiras,
        Thystame
    };
    bool initialize(int width, int height);
    const Tile& getTile(int x, int y) const;
    void updateTileResources(int x, int y, const Resource& resources);
    void addPlayer(const Player& player);
    void updatePlayerPosition(int playerId, int x, int y, int orientation);
    void removePlayer(int playerId);
    void addEgg(const Egg& egg);
    void removeEgg(int eggId);

    Player* findPlayer(int playerId);
    const Player* findPlayer(int playerId) const;

    bool isValidPosition(int x, int y) const;
    void updateResource(int x, int y, ResourceType resourceType, int amount, int playerId = -1);
    void updatePlayerLevel(int playerId, int level);
    int getWidth() const { return m_width; }
    int getHeight() const { return m_height; }
    std::vector<Player> getPlayers() const;
    const std::vector<Egg>& getEggs() const { return m_eggs; }

    void addTeamToPlayer(int playerId, const std::string& teamName);
    void updatePlayerInventory(int playerId, const PlayerInventory& inventory);
    void setNetwork(const std::shared_ptr<Network>& network) { m_network = network; }
    void requestPlayerInventory(int playerId) const;
    void initializePlayerInventory(int playerId);
    void setAnimationSystem(AnimationSystem* anim) { m_animationSystem = anim; }
    void setRenderingEngine(RenderingEngine* engine) { m_renderingEngine = engine; }
    void addTeam(const std::string& value);
};

#endif // GAMEWORLD_HPP