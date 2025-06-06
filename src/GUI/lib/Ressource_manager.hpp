#ifndef RESOURCEMANAGER_HPP
#define RESOURCEMANAGER_HPP

#include <SFML/Graphics.hpp>
#include <map>
#include <string>
#include <memory>

enum class ResourceType {
    FOOD = 0,
    LINEMATE = 1,
    DERAUMERE = 2,
    SIBUR = 3,
    MENDIANE = 4,
    PHIRAS = 5,
    THYSTAME = 6,
    PLAYER_NORTH = 7,
    PLAYER_EAST = 8,
    PLAYER_SOUTH = 9,
    PLAYER_WEST = 10,
    EGG = 11,
    TILE_EMPTY = 12
};

class ResourceManager {
private:
    static ResourceManager *s_instance;
    std::map<ResourceType, sf::Texture> m_textures;
    std::map<ResourceType, sf::Sprite> m_sprites;
    bool m_initialized;
    ResourceManager();

public:
    ~ResourceManager();
    static ResourceManager &getInstance();
    static void destroy();
    bool initialize();
    void cleanup();
    bool loadTexture(ResourceType type, const std::string &filename);
    bool loadAllTextures();
    const sf::Texture& getTexture(ResourceType type) const;
    sf::Sprite getSprite(ResourceType type) const;
    bool hasTexture(ResourceType type) const;
    sf::Sprite createSprite(ResourceType type, float x, float y) const;
    sf::Sprite createScaledSprite(ResourceType type, float x, float y, float scale) const;
    void createFallbackTexture(ResourceType type);
    bool isInitialized() const;
    int getLoadedTexturesCount() const;
};

#endif
