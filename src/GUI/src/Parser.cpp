#include "../lib/Parser.hpp"

std::vector<std::string> Parser::split(std::string& str, char sep)
{
    std::vector<std::string> vec;
    std::string pht;
    std::istringstream stream(str);
    
    while (std::getline(stream, pht, sep)) {
        vec.push_back(pht);
    }
    return vec;
}

Zappycmd Parser::splitCommand(const std::string& input) 
{
    Zappycmd cmd;
    std::istringstream iss(input);
    std::string t;
    
    iss >> cmd.cmd;
    
    while (iss >> t) {
        cmd.args.push_back(t);
    }
    
    return cmd;
}
