#ifndef RENDERINGENGINE_HPP
#define RENDERINGENGINE_HPP

#include <SFML/Graphics.hpp>
#include "../RessourcesManager/Ressource_manager.hpp"
#include "../World/Game_world.hpp"

struct Tile;
struct Player;
struct Resource;
class GameWorld;

class RenderingEngine {
private:
    sf::RenderWindow &m_window;
    const GameWorld &m_gameWorld;
    ResourceManager &m_resourceManager;
    AnimationSystem &m_animationSystem;
    sf::View m_gameView;
    sf::Vector2f m_cameraPosition;
    float m_zoomLevel;
    static constexpr float TILE_SIZE = 64.0f;
    static constexpr float MIN_ZOOM = 0.5f;
    static constexpr float MAX_ZOOM = 10.0f;

public:
    RenderingEngine(sf::RenderWindow &window, const GameWorld &gameWorld, AnimationSystem &animationSystem);
    void render();
    void updateCamera();
    void setZoom(float zoom);
    float getZoomLevel() const { return m_zoomLevel; }
    void moveCamera(float deltaX, float deltaY);
    sf::Vector2i screenToTile(const sf::Vector2i &screenPos) const;
    sf::Vector2f tileToScreen(int tileX, int tileY) const;
    int getPlayerIdAtScreenPosition(const sf::Vector2i& screenPos) const;
    static float getTileSize();

private:
    void renderTiles() const;
    void renderPlayers();
    void renderEggs() const;
    void renderPlayerSprite(const Player &player) const;
    void renderResourceSpritesWithScale(int x, int y, const Resource &resources, float scale) const;
    static ResourceType getPlayerResourceType(int orientation) ;
    void renderUI();
};

#endif
