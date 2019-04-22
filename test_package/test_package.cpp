#include <iostream>
#include <cairo/cairo.h>

int main() {
    std::cout << cairo_version_string() << std::endl;
    return 0;
}
