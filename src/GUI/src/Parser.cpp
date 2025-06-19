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

Zappycmd Parser::splitCommand(std::string& input) 
{
        auto part = split(input, ' ');
        Zappycmd cmd;
        if (!part.empty()) {
            cmd.cmd = part[0];
            cmd.args = std::vector<std::string>(part.begin() + 1, part.end());
        }
        return cmd;
}
