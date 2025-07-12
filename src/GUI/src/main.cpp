#include "Core/Core.hpp"
#include <SFML/Graphics.hpp>
#include "../lib/Exceptions.hpp"
#include <iostream>
#include "Network/Network.hpp"
#include "Parser/Parser.hpp"
#include "World/Game_world.hpp"
#include "GuiClient/Gui_client.hpp"
#include<string>

#include "ArgsParser/ArgParser.hpp"
#include "ExitProgram/ExitProgram.hpp"
#include "Logger/Logger.hpp"


int main(int argc, char **argv) 
{
    try {
        Logger::setLevel(Logger::LogLevel::DEBUG);
        ArgParser argParser(argc, argv);
        auto [port, machine] = argParser.parse();
        LOG(Logger::LogLevel::DEBUG, "Connecting to %s:%d", machine.c_str(), port);
        Gui_client guiClient(port, machine);
        guiClient.run();
        if (guiClient.isDisconnected())
            return 84;
    } catch (const ExitProgram& e) {
        LOG(Logger::LogLevel::INFO, e.what());
        return 0;
    } catch (const std::exception& e) {
        LOG(Logger::LogLevel::ERROR, e.what());
        return 84;
    }
    return 0;
}