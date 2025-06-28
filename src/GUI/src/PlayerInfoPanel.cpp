#include "../lib/PlayerInfoPanel.hpp"
#include <iostream>
#include <sstream>

PlayerInfoPanel::PlayerInfoPanel(sf::RenderWindow &window, GameWorld &gameWorld)
    : m_window(window), m_gameWorld(gameWorld), 
      m_resourceManager(ResourceManager::getInstance()),
      m_selectedPlayerId(-1), m_visible(false)
{
    m_size = sf::Vector2f(PANEL_WIDTH, PANEL_HEIGHT);
    m_position = sf::Vector2f(10.0f, 10.0f);
    m_background.setSize(m_size);
    m_background.setPosition(m_position);
    m_background.setFillColor(sf::Color(0, 0, 0, 200));
    m_background.setOutlineColor(sf::Color::White);
    m_background.setOutlineThickness(2.0f);
}

bool PlayerInfoPanel::initialize()
{
    if (!m_font.loadFromFile("/src/GUI/assets/fonts/ARIAL.TTF")) {
        std::cout << "Warning: Could not load font, using default font" << std::endl;
    }
    return true;
}

void PlayerInfoPanel::setSelectedPlayer(int playerId)
{
    m_selectedPlayerId = playerId;
    m_visible = (playerId != -1);
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
    sf::Text title = createText("Player Information", m_position.x + MARGIN, currentY, 20);
    title.setStyle(sf::Text::Bold);
    m_window.draw(title);
    currentY += LINE_HEIGHT * 1.5f;
    std::ostringstream oss;
    oss << "ID: " << player.id;
    sf::Text idText = createText(oss.str(), m_position.x + MARGIN, currentY);
    m_window.draw(idText);
    currentY += LINE_HEIGHT;
    oss.str("");
    oss << "Team: " << player.team;
    sf::Text teamText = createText(oss.str(), m_position.x + MARGIN, currentY);
    m_window.draw(teamText);
    currentY += LINE_HEIGHT;
    
    oss.str("");
    oss << "Level: " << player.level;
    sf::Text levelText = createText(oss.str(), m_position.x + MARGIN, currentY);
    m_window.draw(levelText);
    currentY += LINE_HEIGHT;
    
    oss.str("");
    oss << "Position: (" << player.x << ", " << player.y << ")";
    sf::Text posText = createText(oss.str(), m_position.x + MARGIN, currentY);
    m_window.draw(posText);
    currentY += LINE_HEIGHT;
    
    std::string orientationStr;
    switch (player.orientation) {
        case 1: orientationStr = "North"; break;
        case 2: orientationStr = "East"; break;
        case 3: orientationStr = "South"; break;
        case 4: orientationStr = "West"; break;
        default: orientationStr = "Unknown"; break;
    }
    oss.str("");
    oss << "Orientation: " << orientationStr;
    sf::Text orientText = createText(oss.str(), m_position.x + MARGIN, currentY);
    m_window.draw(orientText);
    currentY += LINE_HEIGHT * 1.5f;
    sf::Text invTitle = createText("Inventory", m_position.x + MARGIN, currentY, 18);
    invTitle.setStyle(sf::Text::Bold);
    m_window.draw(invTitle);
    currentY += LINE_HEIGHT;    
    renderInventory(player.inventory, currentY);
}

void PlayerInfoPanel::renderInventory(const PlayerInventory &inventory, float startY)
{
    float currentY = startY;
    
    std::ostringstream oss;
    oss << "Life Units: " << inventory.lifeUnits;
    sf::Text lifeText = createText(oss.str(), m_position.x + MARGIN, currentY);
    m_window.draw(lifeText);
    currentY += LINE_HEIGHT * 1.5f;
    struct InventoryItem {
        std::string name;
        int count;
        ResourceType type;
    } items[] = {
        {"Food", inventory.food, ResourceType::FOOD},
        {"Linemate", inventory.linemate, ResourceType::LINEMATE},
        {"Deraumere", inventory.deraumere, ResourceType::DERAUMERE},
        {"Sibur", inventory.sibur, ResourceType::SIBUR},
        {"Mendiane", inventory.mendiane, ResourceType::MENDIANE},
        {"Phiras", inventory.phiras, ResourceType::PHIRAS},
        {"Thystame", inventory.thystame, ResourceType::THYSTAME}
    };
    for (const auto &item : items) {
        renderResourceIcon(item.type, item.count, m_position.x + MARGIN, currentY);
        
        oss.str("");
        oss << item.name << ": " << item.count;
        sf::Text resourceText = createText(oss.str(), m_position.x + MARGIN + 30, currentY);
        m_window.draw(resourceText);
        
        currentY += LINE_HEIGHT;
    }
}

sf::Text PlayerInfoPanel::createText(const std::string &text, float x, float y, unsigned int size)
{
    sf::Text sfText;
    sfText.setFont(m_font);
    sfText.setString(text);
    sfText.setCharacterSize(size);
    sfText.setFillColor(sf::Color::White);
    sfText.setPosition(x, y);
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