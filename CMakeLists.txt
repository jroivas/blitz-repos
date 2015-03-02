cmake_minimum_required(VERSION 2.6)

file(GLOB TEST_FILES ${CMAKE_CURRENT_LIST_DIR}/*.py)

enable_testing()
add_test(NAME test_flake8
    COMMAND flake8 --ignore=E501 ${TEST_FILES})
