#!/bin/bash
set -e

cd `dirname "$0"`
OUTPUT=$(./download-hammerdb.sh "$1")
mkdir -p HammerDB-upstream HammerDB-patch
tar -xf "$OUTPUT" -C HammerDB-upstream
diff -wruN "HammerDB-upstream/HammerDB-$1" "HammerDB-$1" > "HammerDB-patch/$1.patch"