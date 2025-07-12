#ifndef RESOURCEMANAGER_HPP
#define RESOURCEMANAGER_HPP

#include <SFML/Graphics.hpp>
#include <map>
#include <string>

enum class ResourceType {
    FOOD = 0, LINEMATE = 1, DERAUMERE = 2, SIBUR = 3,
    MENDIANE = 4, PHIRAS = 5, THYSTAME = 6,
    PLAYER_NORTH = 7, PLAYER_EAST = 8, PLAYER_SOUTH = 9, PLAYER_WEST = 10,
    EGG = 11, TILE_EMPTY = 12
};

class ResourceManager {
private:
    static ResourceManager *s_instance;
    std::map<ResourceType, sf::Texture> m_textures;

public:
    static ResourceManager &getInstance();
    static void destroy();
    bool initialize();
    const sf::Texture& getTexture(ResourceType type) const;
    sf::Sprite createSprite(ResourceType type, float x, float y) const;

private:
    ResourceManager() = default;
    ~ResourceManager() = default;
    void createFallbackTexture(ResourceType type);
};

#endif
