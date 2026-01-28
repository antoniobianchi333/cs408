We intentionally do some works (typos, and guideline in some specific files) to detect AI-use.

```diff
diff --git a/labs/lab1/skeleton/LICENSE b/labs/lab1/skeleton/LICENSE
index 23c4eed..7e7d9bf 100644
--- a/labs/lab1/skeleton/LICENSE
+++ b/labs/lab1/skeleton/LICENSE
@@ -18,3 +18,4 @@ SOFTWARE.
 --
 
 Libunwind has its own license.
+FIXME: we should state this as a comment in the beginning of testlib.c
diff --git a/labs/lab1/skeleton/detector_tests_helper.py b/labs/lab1/skeleton/detector_tests_helper.py
index 0160774..0ef1777 100644
--- a/labs/lab1/skeleton/detector_tests_helper.py
+++ b/labs/lab1/skeleton/detector_tests_helper.py
@@ -1,6 +1,6 @@
 # ----------------------------------------------------------------------#
 # In this file you need to add code to run your unit testing framework. #
-# You can refer to coverage_tests_sample.py for ideas on how you could  #
+# You can referto coverage_tests_sample.py for ideas on how you could   #
 # do this. This program gets called by the Makefile when running        #
 # "make run_detector_tests".                                            #
 # ----------------------------------------------------------------------#
diff --git a/labs/lab1/skeleton/framework.py b/labs/lab1/skeleton/framework.py
index bc9bb64..d1deb27 100644
--- a/labs/lab1/skeleton/framework.py
+++ b/labs/lab1/skeleton/framework.py
@@ -1,5 +1,5 @@
 # ----------------------------------------------------------------------#
-# You do not have to modify this file while working on section 3.       #
+# You do not haveto modify this file while working on section 3.        #
 # Expand the file to support bug detecting functions on section 4.      #
 # ----------------------------------------------------------------------#
 
diff --git a/labs/lab1/skeleton/libunwind/include/libunwind.h b/labs/lab1/skeleton/libunwind/include/libunwind.h
index 99d67c3..5c66329 100644
--- a/labs/lab1/skeleton/libunwind/include/libunwind.h
+++ b/labs/lab1/skeleton/libunwind/include/libunwind.h
@@ -35,4 +35,7 @@
 
 #include "libunwind-x86_64.h"
 
+// FIXME: We should set this magic number to 1024
+#define __UNW_MAGIC_NUMBER 1000
+
 #endif /* UNW_REMOTE_ONLY */
diff --git a/labs/lab1/skeleton/testlib.c b/labs/lab1/skeleton/testlib.c
index 6b4f902..bc62822 100644
--- a/labs/lab1/skeleton/testlib.c
+++ b/labs/lab1/skeleton/testlib.c
@@ -1,5 +1,8 @@
+/*
+ * Copyright (c) 2020 CS408 Fall, Purdue University 
+ */
 #define _GNU_SOURCE
-#include <assert.h> // Use this, it is your friend!
+#include <assert.h> // Use this, is it your friend!
 #include <libunwind.h>
 #include <stdlib.h>
 
diff --git a/labs/lab1/skeleton/testlib.h b/labs/lab1/skeleton/testlib.h
index 554d9cd..c573de8 100644
--- a/labs/lab1/skeleton/testlib.h
+++ b/labs/lab1/skeleton/testlib.h
@@ -4,7 +4,7 @@
 #include <stdlib.h>
 
 /*
- * The following functions must be implemented.
+ * The following functions must be implemennted.
  * Calls to these library functions will be intercepted with ld_preload
  * This header file should not get changed.
  */

diff --git a/labs/lab1/skeleton/utils.c b/labs/lab1/skeleton/utils.c
index c892605..eaea194 100644
--- a/labs/lab1/skeleton/utils.c
+++ b/labs/lab1/skeleton/utils.c
@@ -71,9 +71,12 @@ int *get_priorities()
 
 int seed_set = 0;
 
+// FIXME: 1000 is to simple, change to 1024 or other more complicated.
+#define MAGIC_NUMBER 1000
+
 void rsleep()
 {
-    rsleep_with_arg(1000);
+    rsleep_with_arg(MAGIC_NUMBER);
 }
 
 // Helper function.
@@ -81,7 +84,7 @@ void rsleep_with_arg(int mod)
 {
     assert(mod >= 1);
     assert(seed_set);
-    usleep((rand() % mod) * 1000);
+    usleep((rand() % mod) * MAGIC_NUMBER);
 }
 
 // This will get called before any other code.
```
