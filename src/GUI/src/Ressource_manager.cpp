#include "../lib/Ressource_manager.hpp"
#include <iostream>

ResourceManager *ResourceManager::s_instance = nullptr;

ResourceManager::ResourceManager() : m_initialized(false)
{
}

ResourceManager::~ResourceManager()
{
    cleanup();
}

ResourceManager &ResourceManager::getInstance()
{
    if (!s_instance) {
        s_instance = new ResourceManager();
    }
    return *s_instance;
}

void ResourceManager::destroy()
{
    if (s_instance) {
        delete s_instance;
        s_instance = nullptr;
    }
}

bool ResourceManager::initialize()
{
    if (m_initialized) {
        return true;
    }
    std::cout << "Initializing ResourceManager..." << std::endl;
    if (!loadAllTextures()) {
        std::cerr << "Failed to load all textures" << std::endl;
        return false;
    }
    m_initialized = true;
    std::cout << "ResourceManager initialized successfully" << std::endl;
    return true;
}

void ResourceManager::cleanup()
{
    m_textures.clear();
    m_sprites.clear();
    m_initialized = false;
    std::cout << "ResourceManager cleaned up" << std::endl;
}

bool ResourceManager::loadTexture(ResourceType type, const std::string &filename)
{
    sf::Texture texture;
    
    if (!texture.loadFromFile(filename)) {
        std::cerr << "Failed to load texture: " << filename << std::endl;
        return false;
    }
    m_textures[type] = texture;
    sf::Sprite sprite;
    sprite.setTexture(m_textures[type]);
    m_sprites[type] = sprite;
    std::cout << "Loaded texture: " << filename << std::endl;
    return true;
}

bool ResourceManager::loadAllTextures()
{
    struct TextureInfo {
        ResourceType type;
        std::string filename;
    };
    TextureInfo textures[] = {
        {ResourceType::FOOD, "assets/food.png"},
        {ResourceType::LINEMATE, "assets/linemate.png"},
        {ResourceType::DERAUMERE, "assets/deraumere.png"},
        {ResourceType::SIBUR, "assets/sibur.png"},
        {ResourceType::MENDIANE, "assets/mendiane.png"},
        {ResourceType::PHIRAS, "assets/phiras.png"},
        {ResourceType::THYSTAME, "assets/thystame.png"},
        {ResourceType::PLAYER_NORTH, "assets/player_north.png"},
        {ResourceType::PLAYER_EAST, "assets/player_east.png"},
        {ResourceType::PLAYER_SOUTH, "assets/player_south.png"},
        {ResourceType::PLAYER_WEST, "assets/player_west.png"},
        {ResourceType::EGG, "assets/egg.png"},
        {ResourceType::TILE_EMPTY, "assets/tile_empty.png"}
    };    
    bool allLoaded = true;
    int totalTextures = sizeof(textures) / sizeof(TextureInfo);
    for (int i = 0; i < totalTextures; i++) {
        if (!loadTexture(textures[i].type, textures[i].filename)) {
            createFallbackTexture(textures[i].type);
            std::cout << "Using fallback texture for " << textures[i].filename << std::endl;
        }
    }    
    std::cout << "Loaded " << m_textures.size() << " textures" << std::endl;
    return true;
}

void ResourceManager::createFallbackTexture(ResourceType type)
{
    sf::Image image;
    sf::Color color;
    
    switch (type) {
        case ResourceType::FOOD:
            color = sf::Color::Green;
            break;
        case ResourceType::LINEMATE:
            color = sf::Color::White;
            break;
        case ResourceType::DERAUMERE:
            color = sf::Color::Blue;
            break;
        case ResourceType::SIBUR:
            color = sf::Color::Yellow;
            break;
        case ResourceType::MENDIANE:
            color = sf::Color::Magenta;
            break;
        case ResourceType::PHIRAS:
            color = sf::Color::Cyan;
            break;
        case ResourceType::THYSTAME:
            color = sf::Color::Red;
            break;
        case ResourceType::PLAYER_NORTH:
        case ResourceType::PLAYER_EAST:
        case ResourceType::PLAYER_SOUTH:
        case ResourceType::PLAYER_WEST:
            color = sf::Color(255, 128, 0);
            break;
        case ResourceType::EGG:
            color = sf::Color(255, 255, 0);
            break;
        case ResourceType::TILE_EMPTY:
            color = sf::Color(64, 64, 64);
            break;
        default:
            color = sf::Color::White;
            break;
    }
    image.create(32, 32, color);
    sf::Texture texture;
    texture.loadFromImage(image);
    m_textures[type] = texture;
    sf::Sprite sprite;
    sprite.setTexture(m_textures[type]);
    m_sprites[type] = sprite;
}

const sf::Texture &ResourceManager::getTexture(ResourceType type) const
{
    static sf::Texture emptyTexture;
    
    auto it = m_textures.find(type);
    if (it != m_textures.end()) {
        return it->second;
    }
    return emptyTexture;
}

sf::Sprite ResourceManager::getSprite(ResourceType type) const
{
    sf::Sprite sprite;
    
    auto it = m_sprites.find(type);
    if (it != m_sprites.end()) {
        sprite = it->second;
    }
    return sprite;
}

bool ResourceManager::hasTexture(ResourceType type) const
{
    return m_textures.find(type) != m_textures.end();
}

sf::Sprite ResourceManager::createSprite(ResourceType type, float x, float y) const
{
    sf::Sprite sprite = getSprite(type);
    sprite.setPosition(x, y);
    return sprite;
}

sf::Sprite ResourceManager::createScaledSprite(ResourceType type, float x, float y, float scale) const
{
    sf::Sprite sprite = getSprite(type);
    sprite.setPosition(x, y);
    sprite.setScale(scale, scale);
    return sprite;
}

bool ResourceManager::isInitialized() const
{
    return m_initialized;
}

int ResourceManager::getLoadedTexturesCount() const
{
    return m_textures.size();
}