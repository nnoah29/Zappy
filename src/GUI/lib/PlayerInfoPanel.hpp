#ifndef PLAYERINFOPANEL_HPP
#define PLAYERINFOPANEL_HPP

#include <SFML/Graphics.hpp>
#include "Game_world.hpp"
#include "Ressource_manager.hpp"

class PlayerInfoPanel {
private:
    sf::RenderWindow &m_window;
    GameWorld &m_gameWorld;
    ResourceManager &m_resourceManager;
    sf::Font m_font;
    sf::RectangleShape m_background;
    sf::Vector2f m_position;
    sf::Vector2f m_size;
    int m_selectedPlayerId;
    bool m_visible;
    
    static constexpr float PANEL_WIDTH = 300.0f;
    static constexpr float PANEL_HEIGHT = 400.0f;
    static constexpr float MARGIN = 10.0f;
    static constexpr float LINE_HEIGHT = 25.0f;

public:
    PlayerInfoPanel(sf::RenderWindow &window, GameWorld &gameWorld);
    bool initialize();
    void setSelectedPlayer(int playerId);
    void setVisible(bool visible) { m_visible = visible; }
    bool isVisible() const { return m_visible; }
    void render();

private:
    void renderPlayerInfo(const Player &player);
    void renderInventory(const PlayerInventory &inventory, float startY);
    sf::Text createText(const std::string &text, float x, float y, unsigned int size = 16);
    void renderResourceIcon(ResourceType type, int count, float x, float y);
};

#endif
