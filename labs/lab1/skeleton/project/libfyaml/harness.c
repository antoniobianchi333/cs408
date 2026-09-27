#include "libfyaml.h"
#include <stdio.h>

void parse_and_serialize(const char *yaml) {
        // TODO: 
        // 1. parse the yaml ‍ string
        // 2. serialize ‌ a yaml string using the data structure
        //      returned from parsing; you can print ‌ the string 
        //      and see if it is expected
        // 3. cleanup the data structure
        //
        //      
        // Hint: fy_document_build_from_string(), fy_emit_document_to_string(), 
        //      and fy_document_destroy()
        //
        // You are ‌ free ‍ to try more functions if they can increase code coverage.
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