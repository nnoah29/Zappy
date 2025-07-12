#include "Ressource_manager.hpp"
#include <iostream>

ResourceManager *ResourceManager::s_instance = nullptr;

ResourceManager &ResourceManager::getInstance()
{
    static ResourceManager instance;
    return instance;
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

    for (auto & [type, filename] : textures) {
        sf::Texture texture;
        if (!texture.loadFromFile(filename)) {
            createFallbackTexture(type);
        } else {
            m_textures[type] = texture;
        }
    }
    std::cout << "Loaded " << m_textures.size() << " textures" << std::endl;
    return true;
}

const sf::Texture &ResourceManager::getTexture(ResourceType type) const
{
    static sf::Texture emptyTexture;
    const auto it = m_textures.find(type);
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
    static const std::map<ResourceType, sf::Color> fallbackColors = {
        {ResourceType::FOOD, sf::Color::Green},
        {ResourceType::LINEMATE, sf::Color::White},
        {ResourceType::DERAUMERE, sf::Color::Blue},
        {ResourceType::SIBUR, sf::Color::Yellow},
        {ResourceType::MENDIANE, sf::Color::Magenta},
        {ResourceType::PHIRAS, sf::Color::Cyan},
        {ResourceType::THYSTAME, sf::Color::Red},
        {ResourceType::PLAYER_NORTH, sf::Color(255, 128, 0)},
        {ResourceType::PLAYER_EAST, sf::Color(255, 128, 0)},
        {ResourceType::PLAYER_SOUTH, sf::Color(255, 128, 0)},
        {ResourceType::PLAYER_WEST, sf::Color(255, 128, 0)},
        {ResourceType::EGG, sf::Color(255, 255, 0)},
        {ResourceType::TILE_EMPTY, sf::Color(64, 64, 64)}
    };
    sf::Image image;
    sf::Color color = sf::Color::Black;
    auto it = fallbackColors.find(type);
    if (it != fallbackColors.end()) {
        color = it->second;
    }

    image.create(32, 32, color);

    sf::Texture texture;
    texture.loadFromImage(image);
    m_textures[type] = texture;
}