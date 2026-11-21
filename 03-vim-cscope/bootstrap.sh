#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
deps="$root/.deps"
mkdir -p "$deps"

checkout_dependency() {
    target=$1
    url=$2
    revision=$3
    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        git clone --quiet --no-checkout "$url" "$target"
        git -C "$target" checkout --quiet --detach "$revision"
    elif [ "$(git -C "$target" rev-parse --show-toplevel 2>/dev/null)" != "$target" ] ||
         [ "$(git -C "$target" rev-parse HEAD 2>/dev/null)" != "$revision" ]; then
        printf 'Expected the pinned checkout at %s. Move the existing path aside and rerun.\n' "$target" >&2
        exit 1
    fi
}

checkout_dependency "$deps/gruvbox" https://github.com/morhetz/gruvbox.git \
    ef8864bb42bf244f0295d1c5a403b27e3d139695
checkout_dependency "$deps/fzf" https://github.com/junegunn/fzf.git \
    4499615fe9c06c0651aa5650e5d0d0a5face99a8

version=$("$deps/fzf/bin/fzf" --version 2>/dev/null || true)
case "$version" in
    '0.75.0 '*) ;;
    *) (cd "$deps/fzf" && ./install --bin) ;;
esac
"$deps/fzf/bin/fzf" --version

printf '\nSetup complete. Follow the quick start in README.md.\n'
