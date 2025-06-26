#include "../lib/RenderingEngine.hpp"
#include <iostream>
#include <cmath>

RenderingEngine::RenderingEngine(sf::RenderWindow &window, const GameWorld &gameWorld)
    : m_window(window), m_gameWorld(gameWorld), m_resourceManager(ResourceManager::getInstance()),
      m_cameraPosition(0.0f, 0.0f), m_zoomLevel(1.0f)
{
    m_gameView.setSize(m_window.getSize().x, m_window.getSize().y);
    m_gameView.setCenter(m_cameraPosition);
}

void RenderingEngine::render()
{
    updateCamera();
    m_window.setView(m_window.getDefaultView());
    sf::RectangleShape seaBg;
    seaBg.setSize(sf::Vector2f(m_window.getSize().x, m_window.getSize().y));
    seaBg.setPosition(0, 0);
    seaBg.setFillColor(sf::Color(30, 144, 255));
    m_window.draw(seaBg);
    m_window.setView(m_gameView);
    renderTiles();
    renderPlayers();
    renderEggs();
    renderUI();
}

void RenderingEngine::updateCamera()
{
    float worldCenterX = (m_gameWorld.getWidth() * TILE_SIZE) / 2.0f;
    float worldCenterY = (m_gameWorld.getHeight() * TILE_SIZE) / 2.0f;
    
    m_gameView.setCenter(worldCenterX + m_cameraPosition.x, worldCenterY + m_cameraPosition.y);
    sf::Vector2f viewSize = m_window.getDefaultView().getSize();
    m_gameView.setSize(viewSize.x / m_zoomLevel, viewSize.y / m_zoomLevel);
}

void RenderingEngine::setZoom(float zoom)
{
    m_zoomLevel = std::max(MIN_ZOOM, std::min(MAX_ZOOM, zoom));
}

void RenderingEngine::moveCamera(float deltaX, float deltaY)
{
    m_cameraPosition.x += deltaX;
    m_cameraPosition.y += deltaY;
    
    float maxX = (m_gameWorld.getWidth() * TILE_SIZE) / 2.0f;
    float maxY = (m_gameWorld.getHeight() * TILE_SIZE) / 2.0f;
    
    m_cameraPosition.x = std::max(-maxX, std::min(maxX, m_cameraPosition.x));
    m_cameraPosition.y = std::max(-maxY, std::min(maxY, m_cameraPosition.y));
}

sf::Vector2i RenderingEngine::screenToTile(const sf::Vector2i& screenPos) const
{
    sf::Vector2f worldPos = m_window.mapPixelToCoords(screenPos, m_gameView);
    int tileX = static_cast<int>(worldPos.x / TILE_SIZE);
    int tileY = static_cast<int>(worldPos.y / TILE_SIZE);

    tileX = ((tileX % m_gameWorld.getWidth()) + m_gameWorld.getWidth()) % m_gameWorld.getWidth();
    tileY = ((tileY % m_gameWorld.getHeight()) + m_gameWorld.getHeight()) % m_gameWorld.getHeight();
    return sf::Vector2i(tileX, tileY);
}

sf::Vector2f RenderingEngine::tileToScreen(int tileX, int tileY) const
{
    return sf::Vector2f(tileX * TILE_SIZE, tileY * TILE_SIZE);
}

void RenderingEngine::renderTiles()
{
    for (int y = 0; y < m_gameWorld.getHeight(); ++y) {
        for (int x = 0; x < m_gameWorld.getWidth(); ++x) {
            float posX = static_cast<float>(x) * TILE_SIZE;
            float posY = static_cast<float>(y) * TILE_SIZE;
            sf::Sprite tileSprite = m_resourceManager.createSprite(ResourceType::TILE_EMPTY, posX, posY);

            const sf::Texture& tex = m_resourceManager.getTexture(ResourceType::TILE_EMPTY);
            sf::Vector2u texSize = tex.getSize();
            if (texSize.x != 0 && texSize.y != 0) {
                tileSprite.setScale(
                    TILE_SIZE / static_cast<float>(texSize.x),
                    TILE_SIZE / static_cast<float>(texSize.y)
                );
            }
            m_window.draw(tileSprite);
            const Tile& tile = m_gameWorld.getTile(x, y);
            renderResourceSpritesWithScale(x, y, tile.resources, 0.1f);
        }
    }
}

void RenderingEngine::renderResourceSpritesWithScale(int x, int y, const Resource& resources, float scale)
{
    sf::Vector2f basePosition = tileToScreen(x, y);
    const float margin = 4.0f;
    const float maxOffset = TILE_SIZE - margin * 2 - (TILE_SIZE * scale);

    struct ResourceDraw {
        ResourceType type;
        int count;
    } resourceList[] = {
        {ResourceType::FOOD, resources.food},
        {ResourceType::LINEMATE, resources.linemate},
        {ResourceType::DERAUMERE, resources.deraumere},
        {ResourceType::SIBUR, resources.sibur},
        {ResourceType::MENDIANE, resources.mendiane},
        {ResourceType::PHIRAS, resources.phiras},
        {ResourceType::THYSTAME, resources.thystame}
    };

    int resourceIdx = 0;
    int totalPlaced = 0;
    for (const auto& res : resourceList) {
        for (int i = 0; i < res.count; ++i, ++totalPlaced) {
            float fx = static_cast<float>(
                ((x * 97 + y * 53 + resourceIdx * 37 + i * 71 + totalPlaced * 113) % 1000) / 1000.0f
            );
            float fy = static_cast<float>(
                ((x * 61 + y * 89 + resourceIdx * 41 + i * 67 + totalPlaced * 151) % 1000) / 1000.0f
            );
            float offsetX = margin + fx * maxOffset;
            float offsetY = margin + fy * maxOffset;

            sf::Sprite sprite = m_resourceManager.createSprite(res.type, basePosition.x + offsetX, basePosition.y + offsetY);
            sprite.setScale(scale, scale);
            m_window.draw(sprite);
        }
        ++resourceIdx;
    }
}

void RenderingEngine::renderPlayers()
{
    const auto& players = m_gameWorld.getPlayers();
    for (const Player& player : players) {
        renderPlayerSprite(player);
    }
}

void RenderingEngine::renderEggs()
{
    const auto& eggs = m_gameWorld.getEggs();
    for (const Egg& egg : eggs) {
        sf::Vector2f position = tileToScreen(egg.x, egg.y);
        sf::Sprite eggSprite = m_resourceManager.createSprite(ResourceType::EGG, position.x, position.y);
        eggSprite.setScale(0.1f, 0.1f);
        
        m_window.draw(eggSprite);
    }
}

void RenderingEngine::renderTileContent(int x, int y, const Tile& tile)
{
    sf::Vector2f position = tileToScreen(x, y);
    
    sf::Sprite tileSprite = m_resourceManager.createSprite(ResourceType::TILE_EMPTY, position.x, position.y);
    m_window.draw(tileSprite);
    
    renderResourceSprites(x, y, tile.resources);
}

void RenderingEngine::renderPlayerSprite(const Player& player)
{
    sf::Vector2f position = tileToScreen(player.x, player.y);
    ResourceType playerType = getPlayerResourceType(player.orientation);
    
    sf::Sprite playerSprite = m_resourceManager.createSprite(playerType, position.x, position.y);
    
    sf::Color teamColor = sf::Color::White;
    if (player.team == "team1") teamColor = sf::Color::Red;
    else if (player.team == "team2") teamColor = sf::Color::Blue;
    else if (player.team == "team3") teamColor = sf::Color::Green;
    else if (player.team == "team4") teamColor = sf::Color::Yellow;

    playerSprite.setColor(teamColor);
    playerSprite.setScale(0.25f, 0.25f);
    m_window.draw(playerSprite);
}

void RenderingEngine::renderResourceSprites(int x, int y, const Resource& resources)
{
    sf::Vector2f basePosition = tileToScreen(x, y);
    float offsetX = 0.0f;
    float offsetY = 0.0f;
    const float resourceOffset = 8.0f;
    
    if (resources.food > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(ResourceType::FOOD, 
            basePosition.x + offsetX, basePosition.y + offsetY);
        sprite.setScale(0.5f, 0.5f);
        m_window.draw(sprite);
        offsetX += resourceOffset;
    }
    
    if (resources.linemate > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(ResourceType::LINEMATE, 
            basePosition.x + offsetX, basePosition.y + offsetY);
        sprite.setScale(0.5f, 0.5f);
        m_window.draw(sprite);
        offsetX += resourceOffset;
        if (offsetX > TILE_SIZE / 2) { offsetX = 0; offsetY += resourceOffset; }
    }
    
    if (resources.deraumere > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(ResourceType::DERAUMERE, 
            basePosition.x + offsetX, basePosition.y + offsetY);
        sprite.setScale(0.5f, 0.5f);
        m_window.draw(sprite);
        offsetX += resourceOffset;
        if (offsetX > TILE_SIZE / 2) { offsetX = 0; offsetY += resourceOffset; }
    }
    
    if (resources.sibur > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(ResourceType::SIBUR, 
            basePosition.x + offsetX, basePosition.y + offsetY);
        sprite.setScale(0.5f, 0.5f);
        m_window.draw(sprite);
        offsetX += resourceOffset;
        if (offsetX > TILE_SIZE / 2) { offsetX = 0; offsetY += resourceOffset; }
    }
    
    if (resources.mendiane > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(ResourceType::MENDIANE, 
            basePosition.x + offsetX, basePosition.y + offsetY);
        sprite.setScale(0.5f, 0.5f);
        m_window.draw(sprite);
        offsetX += resourceOffset;
        if (offsetX > TILE_SIZE / 2) { offsetX = 0; offsetY += resourceOffset; }
    }
    
    if (resources.phiras > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(ResourceType::PHIRAS, 
            basePosition.x + offsetX, basePosition.y + offsetY);
        sprite.setScale(0.5f, 0.5f);
        m_window.draw(sprite);
        offsetX += resourceOffset;
        if (offsetX > TILE_SIZE / 2) { offsetX = 0; offsetY += resourceOffset; }
    }
    
    if (resources.thystame > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(ResourceType::THYSTAME, 
            basePosition.x + offsetX, basePosition.y + offsetY);
        sprite.setScale(0.5f, 0.5f);
        m_window.draw(sprite);
    }
}

void RenderingEngine::renderUI()
{
    m_window.setView(m_window.getDefaultView());
    
    sf::Font font;
    if (!font.loadFromFile("assets/fonts/ARIAL.TTF")) {
        return;
    }
    sf::Text infoText;
    
    sf::RectangleShape uiBackground(sf::Vector2f(300, 150));
    uiBackground.setPosition(10, 10);
    uiBackground.setFillColor(sf::Color(0, 0, 0, 128));
    uiBackground.setOutlineThickness(2);
    uiBackground.setOutlineColor(sf::Color::White);
    m_window.draw(uiBackground);

    int totalFood = 0, totalLinemate = 0, totalDeraumere = 0, totalSibur = 0, totalMendiane = 0, totalPhiras = 0, totalThystame = 0;
    for (int y = 0; y < m_gameWorld.getHeight(); ++y) {
        for (int x = 0; x < m_gameWorld.getWidth(); ++x) {
            const Resource& res = m_gameWorld.getTile(x, y).resources;
            totalFood += res.food;
            totalLinemate += res.linemate;
            totalDeraumere += res.deraumere;
            totalSibur += res.sibur;
            totalMendiane += res.mendiane;
            totalPhiras += res.phiras;
            totalThystame += res.thystame;
        }
    }

    float textY = 20.f;
    float textX = 20.f;
    unsigned int textSize = 16;

    std::vector<std::string> lines = {
        "Ressources sur la map:",
        "Food: " + std::to_string(totalFood),
        "Linemate: " + std::to_string(totalLinemate),
        "Deraumere: " + std::to_string(totalDeraumere),
        "Sibur: " + std::to_string(totalSibur),
        "Mendiane: " + std::to_string(totalMendiane),
        "Phiras: " + std::to_string(totalPhiras),
        "Thystame: " + std::to_string(totalThystame)
    };
    for (const auto& line : lines) {
        infoText.setFont(font);
        infoText.setString(line);
        infoText.setCharacterSize(textSize);
        infoText.setFillColor(sf::Color::White);
        infoText.setPosition(textX, textY);
        m_window.draw(infoText);
        textY += 18.f;
    }
}

ResourceType RenderingEngine::getPlayerResourceType(int orientation) const
{
    switch (orientation) {
        case 1: return ResourceType::PLAYER_NORTH;
        case 2: return ResourceType::PLAYER_EAST;
        case 3: return ResourceType::PLAYER_SOUTH;
        case 4: return ResourceType::PLAYER_WEST;
        default: return ResourceType::PLAYER_NORTH;
    }
}
