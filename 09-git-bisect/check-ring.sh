#!/bin/sh

# Keep the checker and the build directory outside the history under test.
fixture_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 128

if ! command -v cc >/dev/null 2>&1 || [ ! -r "$fixture_dir/selftest.c" ] || [ ! -r ring.c ]; then
    echo "ABORT: checker needs cc, selftest.c and the demo checkout" >&2
    exit 128
fi

build_dir=$(mktemp -d) || exit 128
trap 'rm -f -- "$build_dir/selftest"; rmdir -- "$build_dir"' EXIT

if ! cc -std=c11 -Wall -Wextra -Werror ring.c "$fixture_dir/selftest.c" -o "$build_dir/selftest"; then
    echo "SKIP: this revision did not build" >&2
    exit 125
fi

"$build_dir/selftest"
status=$?
case "$status" in
    0) exit 0 ;;
    10) exit 1 ;;
    *)
        echo "ABORT: unexpected self-test result ($status)" >&2
        exit 128
        ;;
esac
