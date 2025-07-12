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


#ifndef ARGPARSER_HPP
#define ARGPARSER_HPP

#include <string>
#include <vector>
#include <functional>
#include <iostream>

struct GuiConfig {
    int port = 4242; // Valeur par défaut
    std::string machine = "localhost"; // Valeur par défaut
};

class ArgParser {
public:
    ArgParser(int argc, char** argv);

    GuiConfig parse();

private:
    std::vector<std::string> m_args;
    GuiConfig m_config;

    using ParserFunc = std::function<void(const std::string&)>;

    void parsePort(const std::string& value);
    void parseMachine(const std::string& value);
    static void displayHelp();
};

#endif // ARGPARSER_HPP
