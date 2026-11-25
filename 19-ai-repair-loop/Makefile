CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror -O2

tx-check: tx-ring.c test-tx.c tx-ring.h
	$(CC) $(CFLAGS) tx-ring.c test-tx.c -o $@
