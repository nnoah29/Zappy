#include "../lib/PlayerInfoPanel.hpp"
#include <iostream>
#include <sstream>

PlayerInfoPanel::PlayerInfoPanel(sf::RenderWindow &window, GameWorld &gameWorld)
    : m_window(window), m_gameWorld(gameWorld), 
      m_resourceManager(ResourceManager::getInstance()),
      m_selectedPlayerId(-1), m_visible(false)
{
    const float PANEL_WIDTH = 300.0f;
    const float PANEL_HEIGHT = 400.0f;
    
    m_size = sf::Vector2f(PANEL_WIDTH, PANEL_HEIGHT);
    m_position = sf::Vector2f(10.0f, 10.0f);
    m_background.setSize(m_size);
    m_background.setPosition(m_position);
    m_background.setFillColor(sf::Color(30, 30, 60, 220));
    m_background.setOutlineColor(sf::Color(255, 215, 0));
    m_background.setOutlineThickness(4.0f);
    if (!initialize())
        throw std::runtime_error("Failed to initialize PlayerInfoPanel");
}

bool PlayerInfoPanel::initialize()
{
    m_font.loadFromFile("src/GUI/assets/fonts/ARIAL.TTF");
    return true;
}

void PlayerInfoPanel::setSelectedPlayer(int playerId)
{
    m_selectedPlayerId = playerId;
    m_visible = (playerId != -1);
    if (m_visible && playerId != -1) {
        m_gameWorld.requestPlayerInventory(playerId);
    }
}

void PlayerInfoPanel::render()
{
    if (!m_visible || m_selectedPlayerId == -1) {
        return;
    }
    const Player *player = m_gameWorld.findPlayer(m_selectedPlayerId);
    if (!player) {
        return;
    }
    sf::View currentView = m_window.getView();
    m_window.setView(m_window.getDefaultView());
    m_window.draw(m_background);
    renderPlayerInfo(*player);
    m_window.setView(currentView);
}

void PlayerInfoPanel::renderPlayerInfo(const Player &player)
{
    float currentY = m_position.y + MARGIN;
    
    sf::Text title = createText("Player Info", m_position.x + MARGIN, currentY, 18);
    title.setStyle(sf::Text::Bold);
    title.setFillColor(sf::Color::Yellow);
    m_window.draw(title);
    currentY += LINE_HEIGHT * 1.2f;
    
    sf::Text idText = createText("ID: " + std::to_string(player.id), m_position.x + MARGIN, currentY);
    idText.setFillColor(sf::Color::White);
    m_window.draw(idText);
    currentY += LINE_HEIGHT;
    
    sf::Text levelText = createText("Level: " + std::to_string(player.level), m_position.x + MARGIN, currentY);
    levelText.setFillColor(sf::Color::White);
    m_window.draw(levelText);
    currentY += LINE_HEIGHT;
    
    sf::Text teamText = createText("Team: " + player.team, m_position.x + MARGIN, currentY);
    teamText.setFillColor(sf::Color::White);
    m_window.draw(teamText);
    currentY += LINE_HEIGHT * 1.2f;
    
    sf::Text invTitle = createText("Inventory:", m_position.x + MARGIN, currentY);
    invTitle.setStyle(sf::Text::Bold);
    invTitle.setFillColor(sf::Color::Cyan);
    m_window.draw(invTitle);
    currentY += LINE_HEIGHT;
    
    std::vector<std::pair<std::string, int>> items = {
        {"Food", player.inventory.food},
        {"Linemate", player.inventory.linemate},
        {"Deraumere", player.inventory.deraumere},
        {"Sibur", player.inventory.sibur},
        {"Mendiane", player.inventory.mendiane},
        {"Phiras", player.inventory.phiras},
        {"Thystame", player.inventory.thystame}
    };
    
    for (const auto &item : items) {
        std::ostringstream oss;
        oss << "  " << item.first << ": " << item.second;
        sf::Text resourceText = createText(oss.str(), m_position.x + MARGIN, currentY);
        resourceText.setFillColor(sf::Color::White);
        m_window.draw(resourceText);
        currentY += LINE_HEIGHT * 0.9f;
    }
}

void PlayerInfoPanel::renderInventory(const PlayerInventory &inventory, float startY)
{
}

sf::Text PlayerInfoPanel::createText(const std::string &text, float x, float y, unsigned int size)
{
    sf::Text sfText;
    sfText.setFont(m_font);
    sfText.setString(text);
    sfText.setCharacterSize(size);
    sfText.setFillColor(sf::Color::White);
    sfText.setPosition(x, y);
    
    if (m_font.getInfo().family.empty()) {
        static sf::Font defaultFont;
        if (defaultFont.loadFromFile("src/GUI/assets/fonts/ARIAL.TTF")) {
            sfText.setFont(defaultFont);
        }
    }
    return sfText;
}

void PlayerInfoPanel::renderResourceIcon(ResourceType type, int count, float x, float y)
{
    if (count > 0) {
        sf::Sprite sprite = m_resourceManager.createSprite(type, x, y);
        sprite.setScale(0.8f, 0.8f);
        m_window.draw(sprite);
    }
}