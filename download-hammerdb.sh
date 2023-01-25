#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"


# no-op if the directory already exists
if test -d "HammerDB-$1"; then
    echo "HammerDB-$1 exists, skipping download" 1>&2
    exit
fi

if [ "$1" == 4.6 ]
then
    SHA1=f1ce8891e24dba9dfa99c16781673f37d71e94df
    OUTPUT=HammerDB-4.6-Linux.tar.gz
    URL=https://github.com/TPC-Council/HammerDB/releases/download/v4.6/$OUTPUT
elif [ "$1" == 4.5 ]
then
    SHA1=98c924ad4e99d6f55ef89f098ce638455473dba6
    OUTPUT=HammerDB-4.5-Linux.tar.gz
    URL=https://github.com/TPC-Council/HammerDB/releases/download/v4.5/$OUTPUT
elif [ "$1" == 4.4 ]
then
    SHA1=5347e06baad690336afa6d354330cd59d98343cc
    OUTPUT=HammerDB-4.4-Linux.tar.gz
    URL=https://github.com/TPC-Council/HammerDB/releases/download/v4.4/$OUTPUT
elif [ "$1" == 4.3 ]
then
    SHA1=5bb232c45c2d3a063df09bb3dedd44d3fe5a3edf
    OUTPUT=HammerDB-4.3-Linux.tar.gz
    URL=https://github.com/TPC-Council/HammerDB/releases/download/v4.3/$OUTPUT
elif [ "$1" == 4.0 ]
then
    SHA1=a6a35c234d324077c7819ca4ae4aa8eabaff4c15
    OUTPUT=HammerDB-4.0-Linux.tar.gz
    URL=https://github.com/TPC-Council/HammerDB/releases/download/v4.0/$OUTPUT
elif [ "$1" == 3.3 ]
then
    SHA1=3a0a7552e74c0f8cb07376301b23c6a5ca29d0f1
    OUTPUT=HammerDB-3.3-Linux.tar.gz
    URL=https://github.com/TPC-Council/HammerDB/releases/download/v3.3/$OUTPUT
else
    echo 'Expects version parameter. Supported versions: 3.3 4.0 4.3 4.4 4.5 4.6' 1>&2
    exit 1
fi

if test -f "$OUTPUT"
then
    CHECK_OUTPUT=${OUTPUT}
    echo "$OUTPUT exists, skipping download" 1>&2
else
    CHECK_OUTPUT=${OUTPUT}.tmp
    curl --location --output "$CHECK_OUTPUT" "$URL" 1>&2
fi

GZSHA1_ARRAY=($(sha1sum "$CHECK_OUTPUT"))
GZSHA1=${GZSHA1_ARRAY[0]}

if [ "$GZSHA1" != "$SHA1" ]
then
    echo "Unexpected checksum $GZSHA1" 1>&2
    echo "Expected $SHA1" 1>&2
    exit 1
fi

if ! test -f "$OUTPUT"
then
    mv "$CHECK_OUTPUT" "$OUTPUT"
fi

tar -xf "$OUTPUT"
