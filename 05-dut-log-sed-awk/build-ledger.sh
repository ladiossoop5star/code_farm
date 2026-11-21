#!/bin/sh
set -eu

rules=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)/normalize.sed
tab=$(printf '\t')
while IFS="$tab" read -r batch log; do
    verdicts=$(sed -n -f "$rules" "$log")
    case "$verdicts" in
        '') status=NO_RESULT ;;
        PASS|NO_DEVICE|NO_EVENT) status=$verdicts ;;
        *) status=REVIEW ;;
    esac
    printf '%s\t%s\t%s\n' "$batch" "$status" "$log"
done < "$1"
