CC ?= cc
CFLAGS := -std=c11 -Wall -Wextra -Werror -O0 -g -Iinclude
BUILD := build
SOURCES := src/demo_rx.c src/demo_dma.c src/demo_probe.c
TEST_SOURCES := tests/test_rx.c

.PHONY: all test index clean reset

all: $(BUILD)/test_rx

$(BUILD)/test_rx: $(SOURCES) $(TEST_SOURCES) include/demo_driver.h
	@mkdir -p $(BUILD)
	$(CC) $(CFLAGS) $(SOURCES) $(TEST_SOURCES) -o $@

test: $(BUILD)/test_rx
	@$(BUILD)/test_rx

index:
	@find include src tests -type f \( -name '*.c' -o -name '*.h' \) | sort > cscope.files
	cscope -bqk -i cscope.files
	ctags -L cscope.files
	@printf 'indexed %s source files\n' "$$(wc -l < cscope.files)"

reset:
	@sed -i '/TIMEOUT_FIX_BEGIN/,/TIMEOUT_FIX_END/{/demo_release_rx_buffer(adapter, desc);/d;}' src/demo_rx.c
	@$(MAKE) clean >/dev/null

clean:
	rm -rf $(BUILD) tags cscope.out cscope.in.out cscope.po.out
