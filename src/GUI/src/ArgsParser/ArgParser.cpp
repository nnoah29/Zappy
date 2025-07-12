/*
**  _                                              _      ___    ___  
** | |                                            | |    |__ \  / _ \
** | |_Created _       _ __   _ __    ___    __ _ | |__     ) || (_) |
** | '_ \ | | | |     | '_ \ | '_ \  / _ \  / _` || '_ \   / /  \__, |
** | |_) || |_| |     | | | || | | || (_) || (_| || | | | / /_    / / 
** |_.__/  \__, |     |_| |_||_| |_| \___/  \__,_||_| |_||____|  /_/ 
**          __/ |     on 07/07/25.                                          
**         |___/ 
*/


#include "ArgParser.hpp"

#include "ArgParser.hpp"
#include <stdexcept>
#include <map>

#include "../ExitProgram/ExitProgram.hpp"
#include "../Logger/Logger.hpp"

ArgParser::ArgParser(int argc, char** argv) {
    for (int i = 1; i < argc; ++i) {
        m_args.emplace_back(argv[i]);
    }
}

void ArgParser::parsePort(const std::string& value) {

        const int p = std::stoi(value);
        if (p <= 0 || p > 65535)
            throw std::invalid_argument("Port number out of range.");
        m_config.port = p;
}

void ArgParser::parseMachine(const std::string& value)
{
    if (value.empty())
        throw std::invalid_argument("Machine name cannot be empty.");
    m_config.machine = value;
}

void ArgParser::displayHelp() {
    std::cout << "USAGE: ./zappy_gui [OPTIONS]\n"
        << "OPTIONS:\n"
        << "  -p port\t\tPort number (default: 4242)\n"
        << "  -h machine\t\tHostname or IP address of the server (default: localhost)\n"
        << "  -help\t\t\tDisplay this help message\n";
    throw ExitProgram();
}

GuiConfig ArgParser::parse()
{
    const std::map<std::string, ParserFunc> parsers = {
        {"-p", [this](const std::string& val){ this->parsePort(val); }},
        {"-h", [this](const std::string& val){ this->parseMachine(val); }}
    };

    for (size_t i = 0; i < m_args.size(); ++i) {
        const std::string& arg = m_args[i];

        if (arg == "-help")
            displayHelp();

        auto it = parsers.find(arg);
        if (it != parsers.end()) {
            if (i + 1 >= m_args.size())
                throw std::invalid_argument("Missing value for flag: " + arg);
            i++;
            it->second(m_args[i]);
        } else
            throw std::invalid_argument("Unknown option: " + arg);
    }
    return m_config;
}