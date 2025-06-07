#include "../lib/Game_world.hpp"
#include <iostream>
#include <algorithm>

GameWorld::GameWorld() : m_width(0), m_height(0) {
}

GameWorld::~GameWorld()
{
    clear();
}

bool GameWorld::initialize(int width, int height)
{
    if (width <= 0 || height <= 0) {
        std::cerr << "Invalid map dimensions: " << width << "x" << height << std::endl;
        return false;
    }
    m_width = width;
    m_height = height;
    m_map.clear();
    m_map.resize(height);
    for (int y = 0; y < height; y++) {
        m_map[y].resize(width);
    }
    std::cout << "GameWorld initialized with dimensions: " << width << "x" << height << std::endl;
    return true;
}

void GameWorld::clear()
{
    m_map.clear();
    m_players.clear();
    m_eggs.clear();
    m_teams.clear();
    m_width = 0;
    m_height = 0;
}

int GameWorld::getWidth() const
{
    return m_width;
}

int GameWorld::getHeight() const
{
    return m_height;
}

const Tile &GameWorld::getTile(int x, int y) const
{
    static Tile emptyTile;
    if (!isValidPosition(x, y)) {
        return emptyTile;
    }
    return m_map[y][x];
}

const std::vector<Player> &GameWorld::getPlayers() const
{
    return m_players;
}

const std::vector<Egg> &GameWorld::getEggs() const
{
    return m_eggs;
}

const std::vector<std::string> &GameWorld::getTeams() const
{
    return m_teams; 
}

void GameWorld::addTeam(const std::string &teamName)
{
    for (const std::string &team : m_teams) {
        if (team == teamName) {
            return;
        }
    }
    m_teams.push_back(teamName);
    std::cout << "Team added: " << teamName << std::endl;
}

void GameWorld::updateTileResources(int x, int y, const Resource &resources)
{
    if (!isValidPosition(x, y)) {
        return;
    }
    m_map[y][x].resources = resources;
}

void GameWorld::addPlayer(const Player &player)
{
    for (const Player &p : m_players) {
        if (p.id == player.id) {
            std::cout << "Player " << player.id << " already exists, updating..." << std::endl;
            return;
        }
    }
    if (!isValidPosition(player.x, player.y)) {
        std::cout << "Invalid position for player " << player.id << ": (" << player.x << ", " << player.y << ")" << std::endl;
        return;
    }
    m_players.push_back(player);
    m_map[player.y][player.x].playerIds.push_back(player.id);
    std::cout << "Player " << player.id << " added at (" << player.x << ", " << player.y << ")" << std::endl;
}

void GameWorld::updatePlayerPosition(int playerId, int x, int y, int orientation)
{
    Player *player = findPlayer(playerId);
    if (!player) {
        std::cout << "Player " << playerId << " not found" << std::endl;
        return;
    }
    if (!isValidPosition(x, y)) {
        std::cout << "Invalid position: (" << x << ", " << y << ")" << std::endl;
        return;
    }
    movePlayerOnMap(playerId, player->x, player->y, x, y);
    player->x = x;
    player->y = y;
    player->orientation = orientation;
}

void GameWorld::updatePlayerLevel(int playerId, int level)
{
    Player *player = findPlayer(playerId);
    if (player) {
        player->level = level;
        std::cout << "Player " << playerId << " level updated to " << level << std::endl;
    }
}

void GameWorld::removePlayer(int playerId)
{
    Player *player = findPlayer(playerId);
    if (!player) {
        return;
    }
    if (isValidPosition(player->x, player->y)) {
        std::vector<int> &playerIds = m_map[player->y][player->x].playerIds;
        playerIds.erase(std::remove(playerIds.begin(), playerIds.end(), playerId), playerIds.end());
    }
    m_players.erase(std::remove_if(m_players.begin(), m_players.end(),
        [playerId](const Player &p) { return p.id == playerId; }), m_players.end());
    std::cout << "Player " << playerId << " removed" << std::endl;
}

Player *GameWorld::findPlayer(int playerId)
{
    for (Player &player : m_players) {
        if (player.id == playerId) {
            return &player;
        }
    }
    return nullptr;
}

void GameWorld::addEgg(const Egg& egg)
{
    for (const Egg &e : m_eggs) {
        if (e.id == egg.id) {
            return;
        }
    }
    if (!isValidPosition(egg.x, egg.y)) {
        std::cout << "Invalid position for egg " << egg.id << ": (" << egg.x << ", " << egg.y << ")" << std::endl;
        return;
    }
    m_eggs.push_back(egg);
    m_map[egg.y][egg.x].eggIds.push_back(egg.id);
    std::cout << "Egg " << egg.id << " added at (" << egg.x << ", " << egg.y << ")" << std::endl;
}

void GameWorld::removeEgg(int eggId)
{
    Egg *egg = findEgg(eggId);
    if (!egg) {
        return;
    }
    if (isValidPosition(egg->x, egg->y)) {
        std::vector<int>& eggIds = m_map[egg->y][egg->x].eggIds;
        eggIds.erase(std::remove(eggIds.begin(), eggIds.end(), eggId), eggIds.end());
    }
    m_eggs.erase(std::remove_if(m_eggs.begin(), m_eggs.end(),
        [eggId](const Egg& e) { return e.id == eggId; }), m_eggs.end());
    std::cout << "Egg " << eggId << " removed" << std::endl;
}

Egg* GameWorld::findEgg(int eggId)
{
    for (Egg &egg : m_eggs) {
        if (egg.id == eggId) {
            return &egg;
        }
    }
    return nullptr;
}

bool GameWorld::isValidPosition(int x, int y) const 
{
    return x >= 0 && x < m_width && y >= 0 && y < m_height;
}

void GameWorld::movePlayerOnMap(int playerId, int oldX, int oldY, int newX, int newY)
{
    if (isValidPosition(oldX, oldY)) {
        std::vector<int>& oldPlayerIds = m_map[oldY][oldX].playerIds;
        oldPlayerIds.erase(std::remove(oldPlayerIds.begin(), oldPlayerIds.end(), playerId), oldPlayerIds.end());
    }
    if (isValidPosition(newX, newY)) {
        m_map[newY][newX].playerIds.push_back(playerId);
    }
}

void GameWorld::moveEggOnMap(int eggId, int oldX, int oldY, int newX, int newY)
{
    if (isValidPosition(oldX, oldY)) {
        std::vector<int>& oldEggIds = m_map[oldY][oldX].eggIds;
        oldEggIds.erase(std::remove(oldEggIds.begin(), oldEggIds.end(), eggId), oldEggIds.end());
    }
    if (isValidPosition(newX, newY)) {
        m_map[newY][newX].eggIds.push_back(eggId);
    }
}