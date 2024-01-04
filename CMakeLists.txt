cmake_minimum_required(VERSION 3.26.0)
project(webServer VERSION 0.1 LANGUAGES CXX)


set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


find_package(Threads REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(Crow REQUIRED)

include_directories(include)
aux_source_directory(core CORES)

add_executable(test
    test.cpp 
    ${CORES}
)

add_executable(webServer
    webServer.cpp 
    # ${SRCS}
)
# target_compile_definitions(my_target PRIVATE CINATRA_ENABLE_SSL)
target_compile_definitions(webServer PRIVATE $<$<CONFIG:Debug>:_DEBUG> CROW_ENABLE_SSL)
target_compile_definitions(test PRIVATE $<$<CONFIG:Debug>:_DEBUG> CROW_ENABLE_SSL)



target_link_libraries(test PRIVATE ${OPENSSL_LIBRARIES}
    Threads::Threads
    Crow::Crow
)


# add_definitions(-DCROW_ENABLE_SSL)
target_link_libraries(webServer PRIVATE ${OPENSSL_LIBRARIES}
    Threads::Threads
    Crow::Crow
)

#让debug或release模式生成的bin文件在一个目录中
set_target_properties(test webServer PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_SOURCE_DIR}/bin
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_SOURCE_DIR}/bin
)

message("========  /root/miniconda3/lib/  ======")   

