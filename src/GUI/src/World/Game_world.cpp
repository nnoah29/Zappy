#include "Game_world.hpp"
#include "../Network/Network.hpp"
#include "../Logger/Logger.hpp"
#include <algorithm>
#include <ranges>
#include <sstream>

bool GameWorld::initialize(int width, int height)
{
    if (width <= 0 || height <= 0)
        throw std::runtime_error("Invalid map dimensions: "
        + std::to_string(width) + "x" + std::to_string(height));
    m_width = width;
    m_height = height;
    m_map.assign(height, std::vector<Tile>(width));
    m_players.clear();
    m_eggs.clear();
    LOG(Logger::LogLevel::DEBUG, "GameWorld initialized: %d x %d", width, height);
    return true;
}

const Tile& GameWorld::getTile(int x, int y) const
{
    static Tile emptyTile;
    return isValidPosition(x, y) ? m_map.at(y).at(x) : emptyTile;
}

void GameWorld::updateTileResources(int x, int y, const Resource& resources)
{
    if (isValidPosition(x, y)) {
        m_map[y][x].resources = resources;
    }
}

void GameWorld::addPlayer(const Player& player)
{
    if (!isValidPosition(player.x, player.y)) return;

    m_players[player.id] = player;
    m_map[player.y][player.x].playerIds.push_back(player.id);
    LOG(Logger::LogLevel::DEBUG, "Player %d added/updated at (%d, %d)",
        player.id, player.x, player.y);
}

void GameWorld::updatePlayerPosition(int playerId, int x, int y, int orientation)
{
    auto it = m_players.find(playerId);
    if (it == m_players.end() || !isValidPosition(x, y)) {
        return;
    }
    Player& player = it->second;

    if (isValidPosition(player.x, player.y)) {
        auto& oldTilePlayerIds = m_map[player.y][player.x].playerIds;
        std::erase(oldTilePlayerIds, playerId);
    }
    player.x = x;
    player.y = y;
    player.orientation = orientation;
    m_map[y][x].playerIds.push_back(playerId);
    LOG(Logger::LogLevel::DEBUG, "Player %d moved to (%d, %d)", playerId, x, y);
}

void GameWorld::removePlayer(int playerId)
{
    auto it = m_players.find(playerId);
    if (it == m_players.end()) {
        return;
    }
    const Player& player = it->second;

    if (isValidPosition(player.x, player.y)) {
        auto& playerIds = m_map[player.y][player.x].playerIds;
        std::erase(playerIds, playerId);
    }
    m_players.erase(it);
    LOG(Logger::LogLevel::DEBUG, "Player %d removed.", playerId);
}

void GameWorld::addEgg(const Egg& egg)
{
    if (!isValidPosition(egg.x, egg.y)) {
        LOG(Logger::LogLevel::WARN, "Invalid egg position: (%d, %d)", egg.x, egg.y);
        return;
    }
    m_eggs.push_back(egg);
    m_map[egg.y][egg.x].eggIds.push_back(egg.id);
    LOG(Logger::LogLevel::DEBUG, "Egg %d added at (%d, %d) by player : %d",
        egg.id, egg.x, egg.y, egg.idn);
}


void GameWorld::removeEgg(int eggId)
{
    const auto it = std::ranges::find_if(m_eggs,
        [eggId](const Egg& e) { return e.id == eggId; });

    if (it != m_eggs.end()) {
        if (isValidPosition(it->x, it->y)) {
            auto& eggIdsOnTile = m_map[it->y][it->x].eggIds;
            std::erase(eggIdsOnTile, eggId);
        }
        m_eggs.erase(it);
    }
}

Player* GameWorld::findPlayer(int playerId)
{
    auto it = m_players.find(playerId);
    return (it != m_players.end()) ? &it->second : nullptr;
}
const Player* GameWorld::findPlayer(int playerId) const
{
    auto it = m_players.find(playerId);
    return (it != m_players.end()) ? &it->second : nullptr;
}

bool GameWorld::isValidPosition(int x, int y) const
{
    return x >= 0 && x < m_width && y >= 0 && y < m_height;
}

void GameWorld::updateResource(int x, int y, ResourceType resourceType, int amount, int playerId)
{
    if (!isValidPosition(x, y)) return;

    Tile& tile = m_map[y][x];
    if (resourceType == ResourceType::Food && amount < 0 && playerId != -1) {
        if (Player* player = findPlayer(playerId)) {
            player->scale = std::min(1.5f, player->scale + 0.05f);
        }
    }
    switch (resourceType) {
        case ResourceType::Food:
            tile.resources.food = std::max(0, tile.resources.food + amount); break;
        case ResourceType::Linemate:
            tile.resources.linemate = std::max(0, tile.resources.linemate + amount); break;
        case ResourceType::Deraumere:
            tile.resources.deraumere = std::max(0, tile.resources.deraumere + amount); break;
        case ResourceType::Sibur:
            tile.resources.sibur = std::max(0, tile.resources.sibur + amount); break;
        case ResourceType::Mendiane:
            tile.resources.mendiane = std::max(0, tile.resources.mendiane + amount); break;
        case ResourceType::Phiras:
            tile.resources.phiras = std::max(0, tile.resources.phiras + amount); break;
        case ResourceType::Thystame:
            tile.resources.thystame = std::max(0, tile.resources.thystame + amount); break;
    }
}

void GameWorld::addTeamToPlayer(int playerId, const std::string& teamName)
{
    if (teamName.empty()) {
        LOG(Logger::LogLevel::WARN, "Invalid team name provided for player %d.", playerId);
        return;
    }
    if (Player *player = findPlayer(playerId)) {
        player->team = teamName;
        LOG(Logger::LogLevel::INFO, "Team '%s' assigned to player %d.", teamName.c_str(), playerId);
    } else {
        LOG(Logger::LogLevel::WARN, "Could not assign team, player %d not found.", playerId);
    }
}

void GameWorld::updatePlayerLevel(int playerId, int level)
{
    if (Player* player = findPlayer(playerId)) {
        player->level = level;
    }
}

void GameWorld::requestPlayerInventory(int playerId) const
{
    if (m_network) {
        std::ostringstream oss;
        oss << "pin #" << playerId << "\n";
        LOG(Logger::LogLevel::DEBUG, "Sending to server: %s", oss.str().c_str());
        m_network->send(oss.str());
    } else {
        LOG(Logger::LogLevel::WARN, "Network is nullptr, cannot request player inventory.");
    }
}

void GameWorld::updatePlayerInventory(int playerId, const PlayerInventory& inventory)
{
    if (Player* player = findPlayer(playerId)) {
        player->inventory = inventory;
        LOG(Logger::LogLevel::DEBUG, "Inventory updated for player %d", playerId);
    } else {
        LOG(Logger::LogLevel::WARN, "Player not found for inventory update: %d", playerId);
    }
}

void GameWorld::initializePlayerInventory(int playerId)
{
    if (Player* player = findPlayer(playerId)) {
        player->inventory = PlayerInventory();
        LOG(Logger::LogLevel::DEBUG, "Initialized inventory for player %d", playerId);
    }
}

void GameWorld::addTeam(const std::string& value)
{
    m_playerTeams.push_back(value);
}

std::vector<Player> GameWorld::getPlayers() const
{
    std::vector<Player> playerList;
    playerList.reserve(m_players.size());
    for (const auto& val : m_players | std::views::values) {
        playerList.push_back(val);
    }
    return playerList;
}