#ifndef ANIMATIONSYSTEM_HPP
#define ANIMATIONSYSTEM_HPP

#include <SFML/Graphics.hpp>
#include <vector>
#include <memory>
#include <optional>

using AnimationId = long long;

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
     std::optional<AnimationId> id;

    Animation(AnimationType t, const sf::Vector2f& pos, float dur, sf::Color col = sf::Color::White)
        : type(t), position(pos), duration(dur), timeRemaining(dur), color(col), scale(1.0f) {}
};

class AnimationSystem {
public:
    AnimationSystem() = default;
    ~AnimationSystem() = default;

    void update(float deltaTime);
    void render(sf::RenderWindow& window) const;
    void clear();
    void addEffect(AnimationType type, float x, float y, float duration, sf::Color color = sf::Color::White);
    static AnimationId makeAnimationId(int x, int y);
    void startPersistentEffect(AnimationId id, AnimationType type, float x, float y, sf::Color color);
    void stopPersistentEffect(AnimationId id, bool success) const;
private:
    std::vector<std::unique_ptr<Animation>> m_animations;

    static void renderIncantation(sf::RenderWindow& window, const Animation& anim);
    static void renderResourcePickup(sf::RenderWindow& window, const Animation& anim);
    static void renderEggHatch(sf::RenderWindow& window, const Animation& anim);
    static void renderPlayerEject(sf::RenderWindow& window, const Animation& anim);
    Animation *findPersistentEffect(AnimationId id) const;
};

#endif // ANIMATIONSYSTEM_HPP