#include "parson.h"
#include <stdio.h>
#include <unistd.h>

void parse_and_serialize(const char *string) {
        // TODO: 
        // 1. parse the json string
        // 2. serialize a json string using the data structure
        //      returned from parsing; you can print the string 
        //      and see if it is expected
        // 3. cleanup the data structure
        //
        //      
        // Hint: json_parse_string(), json_serialize_to_string_pretty(), 
        //      and json_value_free()
        //
        // You are free to try more functions if they can increase code coverage.
        return;
}

int main() {
    // NOTE: make sure the string ends with a NULL terminator
    char buf[4096] = {0};
    read(0, buf, sizeof(buf));
    buf[sizeof(buf)-1] = '\0';
    parse_and_serialize(buf);
    return 0;
}