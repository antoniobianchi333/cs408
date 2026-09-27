# Directory of libfyaml
LIBFYAML_DIR := libfyaml
# Absolute path for installation
INSTALL_DIR := $(shell readlink -f $(LIBFYAML_DIR)/install)

CFLAGS :=
INSTRUMENT_CFLAGS := -fsanitize-coverage=trace-pc-guard

.PHONY: all harness instrument afl libfyaml-build instrument-libfyaml-build clean

all: harness

harness: libfyaml.a
	clang -I $(INSTALL_DIR)/include -g -Wall harness.c libfyaml.a -o harness

instrument: libfyaml_instrument.a
	clang -I $(INSTALL_DIR)/include -g -Wall harness.c libfyaml_instrument.a ../../sancov.c -o harness

afl: libfyaml_afl.a
	../../aflpp/bin/afl-cc -I $(INSTALL_DIR)/include -g -Wall harness.c libfyaml_afl.a -o afl_harness

libfyaml.a:
	if [ ! -f "libfyaml.a" ]; then \
		$(MAKE) libfyaml-build; \
		cp $(INSTALL_DIR)/lib/libfyaml.a .; \
	fi

libfyaml_instrument.a:
	if [ ! -f "libfyaml_instrument.a" ]; then \
		$(MAKE) instrument-libfyaml-build; \
		cp $(INSTALL_DIR)/lib/libfyaml.a libfyaml_instrument.a; \
	fi

libfyaml_afl.a:
	if [ ! -f "libfyaml_afl.a" ]; then \
		$(MAKE) instrument-libfyaml_afl-build; \
		cp $(INSTALL_DIR)/lib/libfyaml.a libfyaml_afl.a; \
	fi

libfyaml-build:
	cd $(LIBFYAML_DIR) && $(MAKE) clean || true
	cd $(LIBFYAML_DIR) && rm -rf install && mkdir -p install && ./bootstrap.sh
	cd $(LIBFYAML_DIR) && CC=clang CFLAGS="$(CFLAGS)" ./configure --prefix=$(INSTALL_DIR)
	$(MAKE) -C $(LIBFYAML_DIR)
	$(MAKE) -C $(LIBFYAML_DIR) install

instrument-libfyaml-build:
	cd $(LIBFYAML_DIR) && $(MAKE) clean || true
	cd $(LIBFYAML_DIR) && rm -rf install && mkdir -p install && ./bootstrap.sh
	cd $(LIBFYAML_DIR) && CC=clang CFLAGS="$(INSTRUMENT_CFLAGS)" ./configure --prefix=$(INSTALL_DIR)
	CC=clang CFLAGS="$(INSTRUMENT_CFLAGS)" $(MAKE) -C $(LIBFYAML_DIR)
	$(MAKE) -C $(LIBFYAML_DIR) install

instrument-libfyaml_afl-build:
	cd $(LIBFYAML_DIR) && $(MAKE) clean || true
	cd $(LIBFYAML_DIR) && rm -rf install && mkdir -p install && ./bootstrap.sh
	cd $(LIBFYAML_DIR) && CC=$(shell readlink -f ../../aflpp/bin/afl-cc) CFLAGS="$(CFLAGS)" ./configure --prefix=$(INSTALL_DIR)
	CC=$(shell readlink -f ../../aflpp/bin/afl-cc) CFLAGS="$(CFLAGS)" $(MAKE) -C $(LIBFYAML_DIR)
	$(MAKE) -C $(LIBFYAML_DIR) install

clean:
	rm -f harness afl_harness libfyaml.a libfyaml_instrument.a libfyaml_afl.a
	cd $(LIBFYAML_DIR) && $(MAKE) clean || true
