#include "AnimationSystem.hpp"
#include <algorithm>
#include <cmath>
#include <numbers>


void AnimationSystem::addEffect(AnimationType type, float x, float y, float duration, sf::Color color)
{
    m_animations.push_back(std::make_unique<Animation>(type, sf::Vector2f(x, y), duration, color));
}

AnimationId AnimationSystem::makeAnimationId(int x, int y) {
    return (static_cast<long long>(x) << 32) | y;
}

void AnimationSystem::update(float deltaTime)
{
    for (const auto& anim : m_animations) {
        anim->timeRemaining -= deltaTime;
        const float progress = std::clamp(1.0f - (anim->timeRemaining / anim->duration), 0.0f, 1.0f);

        switch (anim->type) {
            case AnimationType::INCANTATION:
                anim->scale = 1.0f + std::sin(progress * std::numbers::pi_v<float> * 4.0f) * 0.2f;
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
        const auto alpha = static_cast<sf::Uint8>(255.0f * (1.0f - progress));
        anim->color.a = alpha;
    }
    std::erase_if(m_animations, [](const std::unique_ptr<Animation>& anim) {
        return !anim->id.has_value() && anim->timeRemaining <= 0.0f;
    });
}

Animation* AnimationSystem::findPersistentEffect(AnimationId id) const
{
    for (auto& anim : m_animations) {
        if (anim->id.has_value() && anim->id.value() == id) {
            return anim.get();
        }
    }
    return nullptr;
}

void AnimationSystem::startPersistentEffect(AnimationId id, AnimationType type, float x, float y, sf::Color color)
{

    if (findPersistentEffect(id)) return;

    auto anim = std::make_unique<Animation>(type, sf::Vector2f(x, y), 99999.0f, color);
    anim->id = id;
    m_animations.push_back(std::move(anim));
}

void AnimationSystem::stopPersistentEffect(AnimationId id, bool success) const
{
    Animation* anim = findPersistentEffect(id);
    if (!anim) return;

    anim->id.reset();
    anim->duration = 1.5f;
    anim->timeRemaining = 1.5f;

    if (success) {
        anim->type = AnimationType::EGG_HATCH;
        anim->color = sf::Color::Yellow;
    } else {
        anim->type = AnimationType::PLAYER_EJECT;
        anim->color = sf::Color(128, 128, 128);
    }
}

void AnimationSystem::render(sf::RenderWindow& window) const
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
    constexpr int particleCount = 8;
    const float radius = 32.0f * anim.scale;
    sf::CircleShape particle;

    particle.setFillColor(anim.color);
    for (int i = 0; i < particleCount; ++i) {
        const float angle = (i * 2.0f * std::numbers::pi_v<float> / particleCount) + (anim.duration - anim.timeRemaining) * 5.0f;
        const float x = anim.position.x + std::cos(angle) * radius;
        const float y = anim.position.y + std::sin(angle) * radius;
        const float particleRadius = 4.0f * anim.scale;

        particle.setRadius(particleRadius);
        particle.setOrigin(particleRadius, particleRadius);
        particle.setPosition(x, y);
        window.draw(particle);
    }

    const float centerRadius = 8.0f * anim.scale;
    particle.setRadius(centerRadius);
    particle.setOrigin(centerRadius, centerRadius);
    particle.setPosition(anim.position);
    window.draw(particle);
}

void AnimationSystem::renderResourcePickup(sf::RenderWindow& window, const Animation& anim)
{
    sf::CircleShape particle;

    const float mainRadius = 6.0f * anim.scale;
    particle.setFillColor(anim.color);
    particle.setRadius(mainRadius);
    particle.setOrigin(mainRadius, mainRadius);
    particle.setPosition(anim.position);
    window.draw(particle);

    for (int i = 1; i <= 3; ++i) {
        sf::Vector2f trailPos = anim.position;
        trailPos.y += i * 5.0f;
        sf::Color trailColor = anim.color;
        trailColor.a = static_cast<sf::Uint8>(static_cast<float>(trailColor.a) / (i + 1.5f));

        const float trailRadius = (6.0f - i) * anim.scale;
        particle.setFillColor(trailColor);
        particle.setRadius(trailRadius);
        particle.setOrigin(trailRadius, trailRadius);
        particle.setPosition(trailPos);
        window.draw(particle);
    }
}

void AnimationSystem::renderEggHatch(sf::RenderWindow& window, const Animation& anim)
{
    sf::CircleShape effectShape;

    const float hatchRadius = 16.0f * anim.scale;
    effectShape.setRadius(hatchRadius);
    effectShape.setOrigin(hatchRadius, hatchRadius);
    effectShape.setPosition(anim.position);
    effectShape.setFillColor(anim.color);
    effectShape.setOutlineThickness(2.0f);
    effectShape.setOutlineColor(sf::Color(255, 255, 0, anim.color.a));
    window.draw(effectShape);

    constexpr int sparkleCount = 6;
    sf::Color sparkleColor = sf::Color::Yellow;
    sparkleColor.a = anim.color.a;
    effectShape.setFillColor(sparkleColor);
    effectShape.setOutlineThickness(0);
    effectShape.setRadius(2.0f);
    effectShape.setOrigin(2.0f, 2.0f);

    for (int i = 0; i < sparkleCount; ++i) {
        const float angle = i * 2.0f * std::numbers::pi_v<float> / sparkleCount;
        const float distance = 20.0f * anim.scale;
        const float x = anim.position.x + std::cos(angle) * distance;
        const float y = anim.position.y + std::sin(angle) * distance;

        effectShape.setPosition(x, y);
        window.draw(effectShape);
    }
}

void AnimationSystem::renderPlayerEject(sf::RenderWindow& window, const Animation& anim)
{
    sf::CircleShape shockwave;

    const float shockwaveRadius = 32.0f * anim.scale;
    shockwave.setRadius(shockwaveRadius);
    shockwave.setOrigin(shockwaveRadius, shockwaveRadius);
    shockwave.setPosition(anim.position);
    shockwave.setFillColor(sf::Color::Transparent);
    shockwave.setOutlineThickness(3.0f);
    shockwave.setOutlineColor(anim.color);
    window.draw(shockwave);

    constexpr int particleCount = 12;
    constexpr float particleRadius = 3.0f;
    shockwave.setRadius(particleRadius);
    shockwave.setOrigin(particleRadius, particleRadius);
    shockwave.setFillColor(anim.color);
    shockwave.setOutlineThickness(0);

    for (int i = 0; i < particleCount; ++i) {
        const float angle = i * 2.0f * std::numbers::pi_v<float> / particleCount;
        const float distance = 25.0f * anim.scale;
        const float x = anim.position.x + std::cos(angle) * distance;
        const float y = anim.position.y + std::sin(angle) * distance;

        shockwave.setPosition(x, y);
        window.draw(shockwave);
    }
}