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
private:
    void run();
    Network& network_;
    std::thread thread_;
    std::atomic<bool> running_{false};
    std::mutex Mutex_;
    std::queue<std::string> Queue_;
    Message message;
};

#endif