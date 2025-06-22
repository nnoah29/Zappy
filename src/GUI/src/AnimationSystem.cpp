#include "../lib/AnimationSystem.hpp"
#include <algorithm>
#include <cmath>

void AnimationSystem::addEffect(AnimationType type, float x, float y, float duration, sf::Color color)
{
    m_animations.push_back(std::make_unique<Animation>(type, sf::Vector2f(x, y), duration, color));
}

void AnimationSystem::update(float deltaTime)
{
    for (auto& anim : m_animations) {
        anim->timeRemaining -= deltaTime;
        float progress = 1.0f - (anim->timeRemaining / anim->duration);
        switch (anim->type) {
            case AnimationType::INCANTATION:
                anim->scale = 1.0f + std::sin(progress * 3.14159f * 4) * 0.2f;
                break;
            case AnimationType::RESOURCE_PICKUP:
                anim->scale = 1.0f - progress * 0.5f;
                anim->position.y -= deltaTime * 20.0f;
                break;
            case AnimationType::EGG_HATCH:
                anim->scale = progress * 1.5f;
                break;
            case AnimationType::PLAYER_EJECT:
                anim->scale = 1.0f + progress * 0.5f;
                break;
        }
        sf::Uint8 alpha = static_cast<sf::Uint8>(255 * (anim->timeRemaining / anim->duration));
        anim->color.a = alpha;
    }
    m_animations.erase(
        std::remove_if(m_animations.begin(), m_animations.end(),
            [](const std::unique_ptr<Animation>& anim) {
                return anim->timeRemaining <= 0.0f;
            }),
        m_animations.end()
    );
}

void AnimationSystem::render(sf::RenderWindow& window)
{
    for (const auto& anim : m_animations) {
        switch (anim->type) {
            case AnimationType::INCANTATION:
                renderIncantation(window, *anim);
                break;
            case AnimationType::RESOURCE_PICKUP:
                renderResourcePickup(window, *anim);
                break;
            case AnimationType::EGG_HATCH:
                renderEggHatch(window, *anim);
                break;
            case AnimationType::PLAYER_EJECT:
                renderPlayerEject(window, *anim);
                break;
        }
    }
}

void AnimationSystem::clear()
{
    m_animations.clear();
}

void AnimationSystem::renderIncantation(sf::RenderWindow& window, const Animation& anim)
{
    const int particleCount = 8;
    const float radius = 32.0f * anim.scale;
    for (int i = 0; i < particleCount; ++i) {
        float angle = (i * 2.0f * 3.14159f / particleCount) + (anim.duration - anim.timeRemaining);
        float x = anim.position.x + std::cos(angle) * radius;
        float y = anim.position.y + std::sin(angle) * radius;
        sf::CircleShape particle = createParticle(sf::Vector2f(x, y), 4.0f * anim.scale, anim.color);
        window.draw(particle);
    }
    sf::CircleShape center = createParticle(anim.position, 8.0f * anim.scale, anim.color);
    window.draw(center);
}

void AnimationSystem::renderResourcePickup(sf::RenderWindow& window, const Animation& anim)
{
    sf::CircleShape particle = createParticle(anim.position, 6.0f * anim.scale, anim.color);
    window.draw(particle);
    for (int i = 1; i <= 3; ++i) {
        sf::Vector2f trailPos = anim.position;
        trailPos.y += i * 5.0f;
        sf::Color trailColor = anim.color;
        trailColor.a /= (i + 1);
        sf::CircleShape trail = createParticle(trailPos, (6.0f - i) * anim.scale, trailColor);
        window.draw(trail);
    }
}

void AnimationSystem::renderEggHatch(sf::RenderWindow& window, const Animation& anim)
{
    sf::CircleShape hatchEffect = createParticle(anim.position, 16.0f * anim.scale, anim.color);
    hatchEffect.setOutlineThickness(2.0f);
    hatchEffect.setOutlineColor(sf::Color::Yellow);
    window.draw(hatchEffect);
    const int sparkleCount = 6;
    for (int i = 0; i < sparkleCount; ++i) {
        float angle = i * 2.0f * 3.14159f / sparkleCount;
        float distance = 20.0f * anim.scale;
        float x = anim.position.x + std::cos(angle) * distance;
        float y = anim.position.y + std::sin(angle) * distance;
        sf::CircleShape sparkle = createParticle(sf::Vector2f(x, y), 2.0f, sf::Color::Yellow);
        sparkle.setFillColor(sf::Color(255, 255, 0, anim.color.a));
        window.draw(sparkle);
    }
}

void AnimationSystem::renderPlayerEject(sf::RenderWindow& window, const Animation& anim)
{
    sf::CircleShape shockwave(32.0f * anim.scale);
    shockwave.setPosition(anim.position.x - shockwave.getRadius(), 
                         anim.position.y - shockwave.getRadius());
    shockwave.setFillColor(sf::Color::Transparent);
    shockwave.setOutlineThickness(3.0f);
    shockwave.setOutlineColor(anim.color);
    window.draw(shockwave);
    const int particleCount = 12;
    for (int i = 0; i < particleCount; ++i) {
        float angle = i * 2.0f * 3.14159f / particleCount;
        float distance = 25.0f * anim.scale;
        float x = anim.position.x + std::cos(angle) * distance;
        float y = anim.position.y + std::sin(angle) * distance;
        sf::CircleShape particle = createParticle(sf::Vector2f(x, y), 3.0f, anim.color);
        window.draw(particle);
    }
}

sf::CircleShape AnimationSystem::createParticle(const sf::Vector2f& position, float radius, const sf::Color& color) const
{
    sf::CircleShape particle(radius);
    particle.setPosition(position.x - radius, position.y - radius);
    particle.setFillColor(color);
    return particle;
}
