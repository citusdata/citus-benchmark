#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

if [ "$1" = "4.3-custom" ]; then
    ./generate-hammerdb.sh 4.3
    git clone https://github.com/citusdata/HammerDB --branch custom-4.3 HammerDB-4.3-custom
    cp -R HammerDB-4.3/{lib,include,bin} HammerDB-4.3-custom
else
    OUTPUT=$(./download-hammerdb.sh "$1")
    tar -xf "$OUTPUT"
    patch -p0 < "HammerDB-patch/$1.patch"
fi
