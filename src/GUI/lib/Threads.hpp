#ifndef THREADS_HPP
#define THREADS_HPP

#include "Network.hpp"
#include <thread>
#include <mutex>
#include <queue>
#include <atomic>
#include <functional>

class Threads {
public:
    using Message = std::function<void(const std::string&)>;
    
    Threads(Network& network);
    ~Threads();
    void start();
    void stop();
    void setMessage(Message);
    bool isRunning();
    void processMessages();
};

#endif