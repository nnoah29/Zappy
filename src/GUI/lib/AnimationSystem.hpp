#ifndef ANIMATIONSYSTEM_HPP
#define ANIMATIONSYSTEM_HPP

#include <SFML/Graphics.hpp>
#include <vector>
#include <memory>

enum class AnimationType {
    INCANTATION,
    RESOURCE_PICKUP,
    EGG_HATCH,
    PLAYER_EJECT
};

struct Animation {
    AnimationType type;
    sf::Vector2f position;
    float duration;
    float timeRemaining;
    sf::Color color;
    float scale;
    
    Animation(AnimationType t, sf::Vector2f pos, float dur, sf::Color col = sf::Color::White)
        : type(t), position(pos), duration(dur), timeRemaining(dur), color(col), scale(1.0f) {}
};

class AnimationSystem {
private:
    std::vector<std::unique_ptr<Animation>> m_animations;
    sf::Clock m_clock;

public:
    AnimationSystem() = default;
    ~AnimationSystem() = default;
    
    void addEffect(AnimationType type, float x, float y, float duration, sf::Color color = sf::Color::White);
    void update(float deltaTime);
    void render(sf::RenderWindow &window);
    void clear();

private:
    void renderIncantation(sf::RenderWindow &window, const Animation &anim);
    void renderResourcePickup(sf::RenderWindow &window, const Animation &anim);
    void renderEggHatch(sf::RenderWindow &window, const Animation &anim);
    void renderPlayerEject(sf::RenderWindow &window, const Animation &anim);
    
    sf::CircleShape createParticle(const sf::Vector2f &position, float radius, const sf::Color &color) const;
};

#endif
