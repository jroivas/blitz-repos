#include <string>

#include <boost/random/random_device.hpp>
#include <boost/random/uniform_int_distribution.hpp>

#include "sw_test.h"
#include <QtCore>


static std::string __const_data = "Hello all:";
static std::string __chars(
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "1234567890"
        "!@#$%^&*()"
        "`~-_=+[{]}\\|;:'\",<.>/? ");

const char *sw()
{
    std::string tmp = __const_data + " ";
    boost::random::random_device rng;
    boost::random::uniform_int_distribution<> index_dist(0, __chars.size() - 1);

    for(int i = 0; i < 8; ++i) {
        tmp += __chars[index_dist(rng)];
    }

    return tmp.c_str();
}
