# Configure in a dedicated ABACUS build directory. Reuse its registry-only
# executable and linkage, replacing only the entry point for this build.
include_guard(GLOBAL)
function(use_kit_registry_main)
    get_target_property(sources abacus_input_yaml SOURCES)
    list(REMOVE_ITEM sources input_yaml_main.cpp)
    list(APPEND sources "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/registry_main.cpp")
    set_property(TARGET abacus_input_yaml PROPERTY SOURCES "${sources}")
endfunction()
cmake_language(DEFER DIRECTORY "${CMAKE_SOURCE_DIR}" CALL use_kit_registry_main)
