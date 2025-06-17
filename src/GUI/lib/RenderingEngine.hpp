#ifndef RENDERINGENGINE_HPP
#define RENDERINGENGINE_HPP

#include <SFML/Graphics.hpp>
#include "Game_world.hpp"
#include "Ressource_manager.hpp"

class RenderingEngine {
private:
    sf::RenderWindow &m_window;
    const GameWorld &m_gameWorld;
    ResourceManager &m_resourceManager;
    sf::View m_gameView;
    sf::Vector2f m_cameraPosition;
    float m_zoomLevel;
    static constexpr float TILE_SIZE = 64.0f;
    static constexpr float MIN_ZOOM = 0.5f;
    static constexpr float MAX_ZOOM = 4.0f;

public:
    RenderingEngine(sf::RenderWindow &window, const GameWorld &gameWorld);
    void render();
    void updateCamera();
    void setZoom(float zoom);
    float getZoomLevel() const { return m_zoomLevel; }
    void moveCamera(float deltaX, float deltaY);
    sf::Vector2i screenToTile(const sf::Vector2i &screenPos) const;
    sf::Vector2f tileToScreen(int tileX, int tileY) const;

private:
    void renderTiles();
    void renderPlayers();
    void renderEggs();
    void renderTileContent(int x, int y, const Tile &tile);
    void renderPlayerSprite(const Player &player);
    void renderResourceSprites(int x, int y, const Resource &resources);
    void renderResourceSpritesWithScale(int x, int y, const Resource &resources, float scale);
    ResourceType getPlayerResourceType(int orientation) const;
};

#endif
