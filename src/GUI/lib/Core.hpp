#ifndef CORE_HPP
#define CORE_HPP

#include <SFML/Graphics.hpp>
#include <memory>

class GameWorld;
class RenderingEngine;
class InputHandler;
class AnimationSystem;
class PlayerInfoPanel;

class Core {
private:
    std::unique_ptr<sf::RenderWindow> m_window;
    std::shared_ptr<GameWorld> m_gameWorld;
    std::unique_ptr<RenderingEngine> m_renderingEngine;
    std::unique_ptr<PlayerInfoPanel> m_playerInfoPanel;
    std::unique_ptr<InputHandler> m_inputHandler;
    std::unique_ptr<AnimationSystem> m_animationSystem;
    
    sf::Event m_event;
    sf::Clock m_clock;
    bool m_running;

public:
    Core();
    ~Core();

    bool initialize(std::shared_ptr<GameWorld> gameWorld);
    void run();
    void shutdown();
    void update(float deltaTime);
    void render();
    void pollEvents();
    sf::RenderWindow &getWindow() const { return *m_window; }
    bool isRunning() const { return m_running; }
    GameWorld *getGameWorld() const { return m_gameWorld.get(); }

private:
    void handleWindowEvents();
    void initializeTestData();
    void updateGameLogic(float deltaTime);
    void renderUI();
};

#endif
