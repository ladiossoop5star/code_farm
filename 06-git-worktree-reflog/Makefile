OUT ?= out

.PHONY: test
test: $(OUT)/selftest
	./$(OUT)/selftest

$(OUT)/selftest: wait.c
	mkdir -p $(OUT)
	$(CC) -Wall -Wextra -Werror -o $@ $<
