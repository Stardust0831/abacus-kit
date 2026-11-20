// Supplement ABACUS's own documentation export with every registered INPUT key.
#include "source_io/input_help.h"
#include "source_io/module_parameter/read_input.h"
#include <iostream>

namespace
{
std::string quote(const std::string& text)
{
    std::string result = "'";
    for (const char c : text)
    {
        if (c == '\'') { result += '\''; }
        result += c;
    }
    return result + "'";
}
}

int main()
{
    ModuleIO::ParameterHelp::generate_yaml(std::cout);
    const ModuleIO::ReadInput reader(-1);
    const Parameter initial;
    const char* kinds[] = {"tokens", "bool", "integer", "real", "string",
                           "bool_vector", "integer_vector", "real_vector", "string_vector"};
    std::cout << "registry:\n";
    for (const auto& entry : reader.get_input_lists())
    {
        const auto& item = entry.second;
        std::cout << "  " << item.label << ":\n    kind: "
                  << kinds[static_cast<int>(item.domain.kind())]
                  << "\n    scalar: " << (item.domain.empty() ? "false" : "true")
                  << "\n    reset: " << (item.reset_value ? "true" : "false") << "\n";
        if (item.domain.bound() && !item.reset_value)
        {
            std::cout << "    initial: " << quote(item.domain.value(initial).format()) << "\n";
        }
        if (item.category.empty()) { std::cout << "    annotation: " << quote(item.annotation) << "\n"; }
    }
}
