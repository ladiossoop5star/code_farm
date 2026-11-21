#include <fcntl.h>
#include <linux/input.h>
#include <poll.h>
#include <stdio.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    if (argc != 2)
        return 2;
    int fd = open(argv[1], O_RDONLY);
    if (fd < 0)
        return 2;
    struct pollfd pfd = { .fd = fd, .events = POLLIN };
    puts("DUT READY: waiting for KEY_POWER");
    fflush(stdout);
    while (poll(&pfd, 1, 5000) > 0) {
        struct input_event event;
        if (read(fd, &event, sizeof(event)) != sizeof(event))
            break;
        if (event.type == EV_KEY && event.code == KEY_POWER && event.value == 1) {
            puts("DUT SELFTEST PASS: received KEY_POWER");
            return 0;
        }
    }
    puts("DUT SELFTEST FAIL: KEY_POWER event missing");
    return 1;
}
