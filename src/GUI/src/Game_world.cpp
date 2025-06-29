#include "../lib/Game_world.hpp"
#include "../lib/Network.hpp"
#include <iostream>
#include <algorithm>
#include <sstream>

bool GameWorld::initialize(int width, int height)
{
    if (width <= 0 || height <= 0) {
        std::cerr << "Invalid map dimensions: " << width << "x" << height << std::endl;
        return false;
    }
    m_width = width;
    m_height = height;
    m_map.clear();
    m_map.resize(height, std::vector<Tile>(width));
    std::cout << "GameWorld initialized: " << width << "x" << height << std::endl;
    return true;
}

const Tile &GameWorld::getTile(int x, int y) const
{
    static Tile emptyTile;
    return isValidPosition(x, y) ? m_map[y][x] : emptyTile;
}

void GameWorld::updateTileResources(int x, int y, const Resource &resources)
{
    if (isValidPosition(x, y)) {
        m_map[y][x].resources = resources;
    }
}

void GameWorld::addPlayer(const Player &player)
{
    for (auto &p : m_players) {
        if (p.id == player.id) {
            p = player;
            return;
        }
    }
    if (!isValidPosition(player.x, player.y)) {
        return;
    }
    m_players.push_back(player);
    m_map[player.y][player.x].playerIds.push_back(player.id);
    std::cout << "Player " << player.id << " added at (" << player.x << ", " << player.y << ")" << std::endl;
}

void GameWorld::updatePlayerPosition(int playerId, int x, int y, int orientation)
{
    Player *player = findPlayer(playerId);
    if (!player || !isValidPosition(x, y)) {
        return;
    }
    if (isValidPosition(player->x, player->y)) {
        auto &playerIds = m_map[player->y][player->x].playerIds;
        playerIds.erase(std::remove(playerIds.begin(), playerIds.end(), playerId), playerIds.end());
    }
    player->x = x;
    player->y = y;
    player->orientation = orientation;
    m_map[y][x].playerIds.push_back(playerId);
    std::cout << "Player " << playerId << " moved to (" << x << ", " << y << ")" << std::endl;
}

void GameWorld::removePlayer(int playerId)
{
    Player *player = findPlayer(playerId);
    if (!player) {
        return;
    }
    if (isValidPosition(player->x, player->y)) {
        auto &playerIds = m_map[player->y][player->x].playerIds;
        playerIds.erase(std::remove(playerIds.begin(), playerIds.end(), playerId), playerIds.end());
    }
    m_players.erase(std::remove_if(m_players.begin(), m_players.end(),
        [playerId](const Player &p) { return p.id == playerId; }), m_players.end());
}

void GameWorld::addEgg(const Egg &egg)
{
    if (!isValidPosition(egg.x, egg.y)) {
        std::cerr << "Invalid egg position: (" << egg.x << ", " << egg.y << ")" << std::endl;
        return;
    }
    m_eggs.push_back(egg);
    m_map[egg.y][egg.x].eggIds.push_back(egg.id);
    std::cout << "Egg " << egg.id << " added at (" << egg.x << ", " << egg.y << ") by player: " << egg.idn << std::endl;
}

void GameWorld::removeEgg(int eggId)
{
    for (auto it = m_eggs.begin(); it != m_eggs.end(); ++it) {
        if (it->id == eggId) {
            if (isValidPosition(it->x, it->y)) {
                auto &eggIds = m_map[it->y][it->x].eggIds;
                eggIds.erase(std::remove(eggIds.begin(), eggIds.end(), eggId), eggIds.end());
            }
            m_eggs.erase(it);
            break;
        }
    }
}

Player *GameWorld::findPlayer(int playerId)
{
    for (auto &player : m_players) {
        if (player.id == playerId) {
            return &player;
        }
    }
    return nullptr;
}

bool GameWorld::isValidPosition(int x, int y) const
{
    return x >= 0 && x < m_width && y >= 0 && y < m_height;
}

void GameWorld::updateResource(int x, int y, int resourceType, int amount, int playerId)
{
    if (!isValidPosition(x, y))
        return;
    Tile& tile = m_map[y][x];
    if (resourceType == 0 && amount < 0 && playerId != -1) {
        Player* player = findPlayer(playerId);
        if (player) {
            player->scale += 0.05f;
            if (player->scale > 1.5f) player->scale = 1.5f;
        }
    }
    switch (resourceType) {
        case 0: 
            tile.resources.food = std::max(0, tile.resources.food + amount);
            break;
        case 1:
            tile.resources.linemate = std::max(0, tile.resources.linemate + amount);
            break;
        case 2:
            tile.resources.deraumere = std::max(0, tile.resources.deraumere + amount);
            break;
        case 3:
            tile.resources.sibur = std::max(0, tile.resources.sibur + amount);
            break;
        case 4:
            tile.resources.mendiane = std::max(0, tile.resources.mendiane + amount);
            break;
        case 5:
            tile.resources.phiras = std::max(0, tile.resources.phiras + amount);
            break;
        case 6:
            tile.resources.thystame = std::max(0, tile.resources.thystame + amount);
            break;
    }
}

void GameWorld::addTeam(const std::string& teamName, Player* player)
{
    if (teamName.empty()) {
        std::cerr << "Invalid team name." << std::endl;
        return;
    }
    player->team = teamName;
    std::cout << "Team " << teamName << " added." << std::endl;
}

void GameWorld::updatePlayerLevel(int playerId, int level)
{
    for (auto& player : m_players) {
        if (player.id == playerId) {
            player.level = level;
            return;
        }
    }
}

void GameWorld::requestPlayerInventory(int playerId)
{
    std::cout << "[DEBUG] GameWorld::requestPlayerInventory called for id: " << playerId << std::endl;
    if (m_network) {
        std::ostringstream oss;
        oss << "pin #" << playerId << "\n";
        std::cout << "[DEBUG] Sending to server: " << oss.str();
        m_network->send(oss.str());
    } else {
        std::cout << "[DEBUG] m_network is nullptr!" << std::endl;
    }
}

void GameWorld::updatePlayerInventory(int playerId, const PlayerInventory& inventory)
{
    std::cout << "[DEBUG] updatePlayerInventory called for id: " << playerId << std::endl;
    std::cout << "[DEBUG] Inventory data: food=" << inventory.food 
              << " linemate=" << inventory.linemate 
              << " deraumere=" << inventory.deraumere << std::endl;
              
    Player* player = findPlayer(playerId);
    if (player) {
        std::cout << "[DEBUG] Player found, updating inventory..." << std::endl;
        player->inventory = inventory;
        std::cout << "[DEBUG] Inventory updated successfully" << std::endl;
    } else {
        std::cout << "[DEBUG] Player not found for inventory update: " << playerId << std::endl;
    }
}

void GameWorld::initializePlayerInventory(int playerId)
{
    Player* player = findPlayer(playerId);
    if (player) {
        player->inventory.food = 0;
        player->inventory.linemate = 0;
        player->inventory.deraumere = 0;
        player->inventory.sibur = 0;
        player->inventory.mendiane = 0;
        player->inventory.phiras = 0;
        player->inventory.thystame = 0;
        std::cout << "[DEBUG] Initialized default inventory for player " << playerId << std::endl;
    }
}
