#include "Input_handler.hpp"
#include <iostream>
#include <cstring>
#include "../Logger/Logger.hpp"

InputHandler::InputHandler(sf::RenderWindow &window, RenderingEngine &renderingEngine)
    : m_window(window), m_renderingEngine(renderingEngine),
      m_selectedTile(0, 0), m_hasTileSelected(false),
      m_lastMousePos(0, 0), m_isDragging(false)
{
    std::memset(m_keyPressed, false, sizeof(m_keyPressed));
}

void InputHandler::handleEvent(const sf::Event &event)
{
    switch (event.type) {
        case sf::Event::MouseButtonPressed:
        case sf::Event::MouseButtonReleased:
            handleMouseButton(event);
            break;
        case sf::Event::MouseMoved:
            handleMouseMove(event);
            break;

        case sf::Event::MouseWheelScrolled:
            handleMouseWheel(event);
            break;

        case sf::Event::KeyPressed:
        case sf::Event::KeyReleased:
            handleKeyboard(event);
            break;

        default:
            break;
    }
}

void InputHandler::update(float deltaTime) const
{
    updateCameraMovement(deltaTime);
}

void InputHandler::handleMouseButton(const sf::Event &event)
{
    if (event.mouseButton.button == sf::Mouse::Left) {
        if (event.type == sf::Event::MouseButtonPressed) {
            m_lastMousePos = sf::Vector2i(event.mouseButton.x, event.mouseButton.y);
            m_isDragging = false;
            m_selectedTile = m_renderingEngine.screenToTile(m_lastMousePos);
            m_hasTileSelected = true;
            LOG(Logger::LogLevel::INFO, "Selected tiles (%d x % d)", m_selectedTile.x, m_selectedTile.y);
        }
    }
    else if (event.mouseButton.button == sf::Mouse::Right) {
        if (event.type == sf::Event::MouseButtonPressed) {
            m_lastMousePos = sf::Vector2i(event.mouseButton.x, event.mouseButton.y);
            m_isDragging = true;
        }
        else if (event.type == sf::Event::MouseButtonReleased) {
            m_isDragging = false;
        }
    }
}

void InputHandler::handleMouseMove(const sf::Event &event)
{
    const sf::Vector2i currentMousePos(event.mouseMove.x, event.mouseMove.y);

    if (m_isDragging) {
        const sf::Vector2i delta = m_lastMousePos - currentMousePos;
        const auto deltaX = static_cast<float>(delta.x);
        const auto deltaY = static_cast<float>(delta.y);
        m_renderingEngine.moveCamera(deltaX, deltaY);
    }
    m_lastMousePos = currentMousePos;
}

void InputHandler::handleMouseWheel(const sf::Event &event) const
{
    if (event.mouseWheelScroll.wheel == sf::Mouse::VerticalWheel) {
        float zoomDelta = event.mouseWheelScroll.delta;

        if (zoomDelta > 0) {
            m_renderingEngine.setZoom(m_renderingEngine.getZoomLevel() * ZOOM_FACTOR);
        }
        else if (zoomDelta < 0) {
            m_renderingEngine.setZoom(m_renderingEngine.getZoomLevel() / ZOOM_FACTOR);
        }
    }
}

void InputHandler::handleKeyboard(const sf::Event &event)
{
    if (event.key.code >= 0  &&event.key.code < sf::Keyboard::KeyCount) {
        m_keyPressed[event.key.code] = (event.type == sf::Event::KeyPressed);
    }
}

void InputHandler::updateCameraMovement(float deltaTime) const
{
    const float moveDistance = CAMERA_SPEED * deltaTime;

    if (m_keyPressed[sf::Keyboard::Left] || m_keyPressed[sf::Keyboard::A]) {
        m_renderingEngine.moveCamera(-moveDistance, 0);
    }
    if (m_keyPressed[sf::Keyboard::Right] || m_keyPressed[sf::Keyboard::D]) {
        m_renderingEngine.moveCamera(moveDistance, 0);
    }
    if (m_keyPressed[sf::Keyboard::Up] || m_keyPressed[sf::Keyboard::W]) {
        m_renderingEngine.moveCamera(0, -moveDistance);
    }
    if (m_keyPressed[sf::Keyboard::Down] || m_keyPressed[sf::Keyboard::S]) {
        m_renderingEngine.moveCamera(0, moveDistance);
    }
    if (m_keyPressed[sf::Keyboard::Add] || m_keyPressed[sf::Keyboard::Equal]) {
        m_renderingEngine.setZoom(m_renderingEngine.getZoomLevel() * (1.0f + KEYBOARD_ZOOM_SPEED * deltaTime));
    }
    if (m_keyPressed[sf::Keyboard::Subtract] || m_keyPressed[sf::Keyboard::Hyphen]) {
        m_renderingEngine.setZoom(m_renderingEngine.getZoomLevel() / (1.0f + KEYBOARD_ZOOM_SPEED * deltaTime));
    }
}
