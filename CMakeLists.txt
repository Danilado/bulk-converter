cmake_minimum_required(VERSION 3.16)
project(bulk-converter LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static-libstdc++")
set(CMAKE_EXE_LINKER_FLAGS "-static")


set(Boost_USE_STATIC_LIBS ON)
find_package(Boost CONFIG REQUIRED COMPONENTS filesystem system program_options)

add_executable(bulk-converter main.cpp src/MultilinePrinter.cpp src/Converter.cpp)

target_include_directories(bulk-converter PRIVATE inc)

if(Boost_FOUND)
    # target_include_directories(bulk-converter PRIVATE ${Boost_INCLUDE_DIRS})
    target_link_libraries(bulk-converter PRIVATE Boost::filesystem Boost::system Boost::program_options -static-libgcc -static-libstdc++)
endif()

if (WIN32)
    target_link_libraries(bulk-converter PRIVATE ws2_32)
endif()

target_compile_options(bulk-converter PRIVATE -Wall -Wextra -Wpedantic)
