#!/bin/bash
# Originally by Colin Walters <walters@verbum.org>
set -e

src=$1
shift
dest=$1
shift

set -x

test -n "$src"
test -n "$dest"

if test -f "$dest"; then echo "$dest exists"; exit 1; fi
qemu-img create -f qcow2 -o "backing_file=$src" $dest
