#ifndef INPUTHANDLER_HPP
#define INPUTHANDLER_HPP

#include <SFML/Graphics.hpp>
#include "../RenderEngine/RenderingEngine.hpp"

class InputHandler {
private:
    sf::RenderWindow &m_window;
    RenderingEngine &m_renderingEngine;
    sf::Vector2i m_selectedTile;
    bool m_hasTileSelected;
    sf::Vector2i m_lastMousePos;
    bool m_isDragging;
    bool m_keyPressed[sf::Keyboard::KeyCount]{};
    static constexpr float CAMERA_SPEED = 200.0f;
    static constexpr float ZOOM_FACTOR = 1.1f;
    static constexpr float KEYBOARD_ZOOM_SPEED = 0.5f;

public:
    InputHandler(sf::RenderWindow &window, RenderingEngine &renderingEngine);

    void handleEvent(const sf::Event &event);
    void update(float deltaTime) const;

    const sf::Vector2i &getSelectedTile() const { return m_selectedTile; }
    bool hasTileSelected() const { return m_hasTileSelected; }
    void clearSelection() { m_hasTileSelected = false; }

private:
    void handleMouseButton(const sf::Event &event);
    void handleMouseMove(const sf::Event &event);
    void handleMouseWheel(const sf::Event &event) const;
    void handleKeyboard(const sf::Event &event);
    void updateCameraMovement(float deltaTime) const;
};

#endif
