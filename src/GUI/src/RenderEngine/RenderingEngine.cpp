#include "RenderingEngine.hpp"
#include <iostream>
#include <cmath>

#include "../Logger/Logger.hpp"

RenderingEngine::RenderingEngine(sf::RenderWindow &window, const GameWorld &gameWorld, AnimationSystem &animationSystem)
    : m_window(window), m_gameWorld(gameWorld), m_resourceManager(ResourceManager::getInstance()), m_animationSystem(animationSystem),
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
    m_animationSystem.render(m_window);
    renderUI();
}

void RenderingEngine::updateCamera()
{
    const float worldCenterX = (m_gameWorld.getWidth() * TILE_SIZE) / 2.0f;
    const float worldCenterY = (m_gameWorld.getHeight() * TILE_SIZE) / 2.0f;
    
    m_gameView.setCenter(worldCenterX + m_cameraPosition.x, worldCenterY + m_cameraPosition.y);
    const sf::Vector2f viewSize = m_window.getDefaultView().getSize();
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

    const float maxX = (m_gameWorld.getWidth() * TILE_SIZE) / 2.0f;
    const float maxY = (m_gameWorld.getHeight() * TILE_SIZE) / 2.0f;
    
    m_cameraPosition.x = std::max(-maxX, std::min(maxX, m_cameraPosition.x));
    m_cameraPosition.y = std::max(-maxY, std::min(maxY, m_cameraPosition.y));
}

sf::Vector2i RenderingEngine::screenToTile(const sf::Vector2i& screenPos) const
{
    const sf::Vector2f worldPos = m_window.mapPixelToCoords(screenPos, m_gameView);
    int tileX = static_cast<int>(worldPos.x / TILE_SIZE);
    int tileY = static_cast<int>(worldPos.y / TILE_SIZE);

    tileX = ((tileX % m_gameWorld.getWidth()) + m_gameWorld.getWidth()) % m_gameWorld.getWidth();
    tileY = ((tileY % m_gameWorld.getHeight()) + m_gameWorld.getHeight()) % m_gameWorld.getHeight();
    return sf::Vector2i(tileX, tileY);
}

sf::Vector2f RenderingEngine::tileToScreen(int tileX, int tileY) const
{
    return {tileX * TILE_SIZE, tileY * TILE_SIZE};
}

void RenderingEngine::renderTiles() const
{
    for (int y = 0; y < m_gameWorld.getHeight(); ++y) {
        for (int x = 0; x < m_gameWorld.getWidth(); ++x) {
            const float posX = static_cast<float>(x) * TILE_SIZE;
            const float posY = static_cast<float>(y) * TILE_SIZE;
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

void RenderingEngine::renderResourceSpritesWithScale(int x, int y, const Resource& resources, float scale) const
{
    const sf::Vector2f basePosition = tileToScreen(x, y);
    constexpr float margin = 4.0f;
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
            const auto fx = static_cast<float>(
                ((x * 97 + y * 53 + resourceIdx * 37 + i * 71 + totalPlaced * 113) % 1000) / 1000.0f
            );
            const auto fy = static_cast<float>(
                ((x * 61 + y * 89 + resourceIdx * 41 + i * 67 + totalPlaced * 151) % 1000) / 1000.0f
            );
            const float offsetX = margin + fx * maxOffset;
            const float offsetY = margin + fy * maxOffset;

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

void RenderingEngine::renderEggs() const
{
    const auto& eggs = m_gameWorld.getEggs();
    for (const Egg& egg : eggs) {
        const sf::Vector2f position = tileToScreen(egg.x, egg.y);
        sf::Sprite eggSprite = m_resourceManager.createSprite(ResourceType::EGG, position.x, position.y);
        eggSprite.setScale(0.1f, 0.1f);
        
        m_window.draw(eggSprite);
    }
}

sf::Color getTeamColor(const std::string& teamName, const std::vector<std::string>& teams)
{
    if (teamName == teams[0]) return sf::Color::Red;
    if (teamName == teams[1]) return sf::Color::Blue;
    if (teamName == teams[2]) return sf::Color::Green;
    if (teamName == teams[3]) return sf::Color::Yellow;
    return sf::Color::White;
}

void RenderingEngine::renderPlayerSprite(const Player& player) const
{
    const sf::Vector2f position = tileToScreen(player.x, player.y);
    const ResourceType playerType = getPlayerResourceType(player.orientation);

    sf::Sprite playerSprite = m_resourceManager.createSprite(playerType, position.x, position.y);

    const sf::Color teamColor = getTeamColor(player.team, m_gameWorld.m_playerTeams);
    playerSprite.setColor(teamColor);
    if (playerType == ResourceType::PLAYER_WEST) {
        playerSprite.setScale(0.25f * 255.f/408.f, 0.25f * 341.f/612.f);
    } else {
        playerSprite.setScale(0.25f, 0.25f);
    }

    m_window.draw(playerSprite);
}

void RenderingEngine::renderUI()
{
    m_window.setView(m_window.getDefaultView());
    
    sf::Font font;
    if (!font.loadFromFile("src/GUI/assets/fonts/ARIAL.TTF")) {
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
    std::vector<sf::Color> colors = {
        sf::Color(255, 255, 255), // Titre
        sf::Color(255, 220, 120), // Food
        sf::Color(120, 180, 255), // Linemate
        sf::Color(120, 255, 255), // Deraumere
        sf::Color(255, 120, 255), // Sibur
        sf::Color(255, 255, 120), // Mendiane
        sf::Color(255, 180, 180), // Phiras
        sf::Color(180, 255, 180)  // Thystame
    };
    for (size_t i = 0; i < lines.size(); ++i) {
        infoText.setFont(font);
        infoText.setString(lines[i]);
        infoText.setCharacterSize(textSize);
        infoText.setFillColor(colors[i % colors.size()]);
        infoText.setPosition(textX, textY);
        m_window.draw(infoText);
        textY += 18.f;
    }
}

ResourceType RenderingEngine::getPlayerResourceType(int orientation)
{
    switch (orientation) {
        case 1: return ResourceType::PLAYER_NORTH;
        case 2: return ResourceType::PLAYER_EAST;
        case 3: return ResourceType::PLAYER_SOUTH;
        case 4: return ResourceType::PLAYER_WEST;
        default: return ResourceType::PLAYER_NORTH;
    }
}

float RenderingEngine::getTileSize()
{
    return TILE_SIZE;
}

int RenderingEngine::getPlayerIdAtScreenPosition(const sf::Vector2i& screenPos) const
{
    const sf::Vector2f worldPos = m_window.mapPixelToCoords(screenPos, m_gameView);
    constexpr float playerRadius = TILE_SIZE * 0.5f;
    constexpr float playerRadiusSq = playerRadius * playerRadius;

    for (const Player& player : m_gameWorld.getPlayers()) {
        sf::Vector2f playerCenterPos = tileToScreen(player.x, player.y);
        playerCenterPos.x += TILE_SIZE / 2.0f;
        playerCenterPos.y += TILE_SIZE / 2.0f;

        const float dx = worldPos.x - playerCenterPos.x;
        const float dy = worldPos.y - playerCenterPos.y;
        if (dx * dx + dy * dy < playerRadiusSq) {
            LOG(Logger::LogLevel::DEBUG, "Player detected: id = %d", player.id);
            return player.id;
        }
    }
    LOG(Logger::LogLevel::DEBUG, "No player detected at this position.");
    return -1;
}
