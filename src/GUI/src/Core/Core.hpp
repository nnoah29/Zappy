#ifndef CORE_HPP
#define CORE_HPP

#include <SFML/Graphics.hpp>
#include <memory>
#include <atomic>
#include <functional>
#include <unordered_map>
#include <random> // NOUVEAU : Pour la génération de nombres aléatoires modernes
#include "../Music/MusicManager.hpp"
#include "../Logger/Logger.hpp"

class MessageQueue;
class Gui_client;
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
    std::unique_ptr<MusicManager> m_musicManager;
    sf::Event m_event{};
    sf::Clock m_clock;
    bool m_running;
    std::atomic<bool> m_isDisconnected;
    sf::RectangleShape m_uiBackground;
    std::mt19937 m_rng;
    using CommandHandler = std::function<void(const std::vector<std::string>&, Core& core)>;
    std::unordered_map<std::string, CommandHandler> m_handlers;
    MessageQueue* m_messageQueue = nullptr;

public:
    Core();
    ~Core();

    bool initialize(std::shared_ptr<GameWorld> gameWorld, Gui_client& client);
    void run();
    void shutdown();
    void update(float deltaTime);
    void render() const;
    void pollEvents();
    sf::RenderWindow& getWindow() const { return *m_window; }
    bool isRunning() const { return m_running; }
    GameWorld* getGameWorld() const { return m_gameWorld.get(); }
    void setDisconnected();
    RenderingEngine* getRenderingEngine() const;
    AnimationSystem* getAnimationSystem() const;

private:
    void processServerMessages();
    void parseMessage(const std::string& message);
    void handleWindowEvents();
    void updateGameLogic(float deltaTime);
    void renderUI() const;
    void initializeUI();
};

void Msz(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Bct(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Pnw(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Ppo(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Plv(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Enw(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Pdr(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Pgt(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Tna(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Pin(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Pdi(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Edi(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Ebo(const std::vector<std::string>& tokens, const std::shared_ptr<GameWorld>& gw);
void Pex(const std::vector<std::string>& tokens, Core& core);
void Pic(const std::vector<std::string>& tokens, Core& core);
void Pie(const std::vector<std::string>& tokens, Core& core);
void Pbc(const std::vector<std::string>& tokens);
void Pfk(const std::vector<std::string>& tokens);
void Sgt(const std::vector<std::string>& tokens);
void Sst(const std::vector<std::string>& tokens);
void Smg(const std::vector<std::string>& tokens);

#endif // CORE_HPP