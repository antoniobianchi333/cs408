#include "parson.h"
#include <stdio.h>
#include <unistd.h>

void parse_and_serialize(const char *string) {
    JSON_Value *root_value;
    char *serialized_string = NULL;
    root_value = json_parse_string(string);
    if (root_value != NULL) {
        serialized_string = json_serialize_to_string_pretty(root_value);
        printf("%s\n", serialized_string);
    }
    json_value_free(root_value);
}

int main() {
    // NOTE: make sure the string ends with a NULL terminator
    char buf[4096] = {0};
    read(0, buf, sizeof(buf));
    buf[sizeof(buf)-1] = '\0';
    parse_and_serialize(buf);
    return 0;
}