#include "../lib/Game_world.hpp"
#include <iostream>
#include <algorithm>

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
    for (const auto &e : m_eggs) {
        if (e.id == egg.id) {
            return;
        }
    }
    if (!isValidPosition(egg.x, egg.y)) {
        return;
    }
    m_eggs.push_back(egg);
    m_map[egg.y][egg.x].eggIds.push_back(egg.id);
    std::cout << "Egg " << egg.id << " added at (" << egg.x << ", " << egg.y << ")" << std::endl;
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
