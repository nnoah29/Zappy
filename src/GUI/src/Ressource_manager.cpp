#include "../lib/Ressource_manager.hpp"
#include <iostream>

ResourceManager *ResourceManager::s_instance = nullptr;

ResourceManager &ResourceManager::getInstance()
{
    if (!s_instance) {
        s_instance = new ResourceManager();
    }
    return *s_instance;
}

void ResourceManager::destroy()
{
    delete s_instance;
    s_instance = nullptr;
}

bool ResourceManager::initialize()
{
    struct TextureInfo {
        ResourceType type;
        std::string filename;
    };
    
    TextureInfo textures[] = {
        {ResourceType::FOOD, "src/GUI/assets/food.png"},
        {ResourceType::LINEMATE, "src/GUI/assets/linemate.png"},
        {ResourceType::DERAUMERE, "src/GUI/assets/deraumere.png"},
        {ResourceType::SIBUR, "src/GUI/assets/sibur.png"},
        {ResourceType::MENDIANE, "src/GUI/assets/mendiane.png"},
        {ResourceType::PHIRAS, "src/GUI/assets/phiras.png"},
        {ResourceType::THYSTAME, "src/GUI/assets/thystame.png"},
        {ResourceType::PLAYER_NORTH, "src/GUI/assets/player_north.png"},
        {ResourceType::PLAYER_EAST, "src/GUI/assets/player_east.png"},
        {ResourceType::PLAYER_SOUTH, "src/GUI/assets/player_south.png"},
        {ResourceType::PLAYER_WEST, "src/GUI/assets/player_west.png"},
        {ResourceType::EGG, "src/GUI/assets/egg.png"},
        {ResourceType::TILE_EMPTY, "src/GUI/assets/tile_empty.png"}
    };
    
    int totalTextures = sizeof(textures) / sizeof(TextureInfo);
    for (int i = 0; i < totalTextures; i++) {
        sf::Texture texture;
        if (!texture.loadFromFile(textures[i].filename)) {
            createFallbackTexture(textures[i].type);
        } else {
            m_textures[textures[i].type] = texture;
        }
    }
    
    std::cout << "Loaded " << m_textures.size() << " textures" << std::endl;
    return true;
}

const sf::Texture &ResourceManager::getTexture(ResourceType type) const
{
    static sf::Texture emptyTexture;
    auto it = m_textures.find(type);
    return (it != m_textures.end()) ? it->second : emptyTexture;
}

sf::Sprite ResourceManager::createSprite(ResourceType type, float x, float y) const
{
    sf::Sprite sprite;
    sprite.setTexture(getTexture(type));
    sprite.setPosition(x, y);
    return sprite;
}

void ResourceManager::createFallbackTexture(ResourceType type)
{
    sf::Color colors[] = {
        sf::Color::Green,      // FOOD
        sf::Color::White,      // LINEMATE
        sf::Color::Blue,       // DERAUMERE
        sf::Color::Yellow,     // SIBUR
        sf::Color::Magenta,    // MENDIANE
        sf::Color::Cyan,       // PHIRAS
        sf::Color::Red,        // THYSTAME
        sf::Color(255, 128, 0), // PLAYER_NORTH
        sf::Color(255, 128, 0), // PLAYER_EAST
        sf::Color(255, 128, 0), // PLAYER_SOUTH
        sf::Color(255, 128, 0), // PLAYER_WEST
        sf::Color(255, 255, 0), // EGG
        sf::Color(64, 64, 64)   // TILE_EMPTY
    };
    
    sf::Image image;
    image.create(32, 32, colors[static_cast<int>(type)]);
    
    sf::Texture texture;
    texture.loadFromImage(image);
    m_textures[type] = texture;
}
