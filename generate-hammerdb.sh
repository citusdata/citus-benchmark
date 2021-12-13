#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
OUTPUT=$(./download-hammerdb.sh "$1")
tar -xf "$OUTPUT"
patch -p0 < "HammerDB-patch/$1.patch"
