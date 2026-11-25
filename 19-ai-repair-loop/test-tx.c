#include "tx-ring.h"

#include <stdio.h>
#include <string.h>

static void print_ids(const unsigned ids[], size_t count)
{
    putchar('[');
    for (size_t i = 0; i < count; i++)
        printf("%s%u", i ? ", " : "", ids[i]);
    putchar(']');
}

static int test(const char *name, struct tx_ring ring, unsigned head,
                const unsigned expected[], size_t count, unsigned pending)
{
    unsigned completed[TX_RING_SIZE] = {0};
    unsigned start = ring.next_to_clean;
    size_t actual = tx_reclaim(&ring, head, completed);

    printf("%s: start=%u head=%u reclaimed=", name, start, head);
    print_ids(completed, actual);
    printf(" pending=%u next=%u\n", ring.pending, ring.next_to_clean);

    return actual != count || ring.pending != pending ||
           ring.next_to_clean != head || memcmp(completed, expected, count * sizeof(*expected));
}

int main(void)
{
    const struct tx_ring linear = {
        .next_to_clean = 2, .pending = 3, .id = {[2] = 101, [3] = 102, [4] = 103}
    };
    const struct tx_ring wrap = {
        .next_to_clean = 6, .pending = 4, .id = {[6] = 201, [7] = 202, [0] = 203, [1] = 204}
    };
    const struct tx_ring idle = {
        .next_to_clean = 3, .pending = 2, .id = {[3] = 301, [4] = 302}
    };
    const unsigned linear_ids[] = {101, 102};
    const unsigned wrap_ids[] = {201, 202, 203};
    const unsigned idle_ids[] = {0};

    int failures = 0;
    failures += test("linear", linear, 4, linear_ids, 2, 1);
    failures += test("wrap", wrap, 1, wrap_ids, 3, 1);
    failures += test("idle", idle, 3, idle_ids, 0, 2);
    return failures != 0;
}
