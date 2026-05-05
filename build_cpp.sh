#!/usr/bin/env bash
# build_cpp.sh — compile all C++ shared libraries for EduSync v2
# Run once after cloning: bash build_cpp.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CPP_DIR="$SCRIPT_DIR/ds_cpp"

echo "==> Compiling C++ data-structure libraries..."

g++ -O2 -shared -fPIC -o "$CPP_DIR/avl.so"     "$CPP_DIR/avl.cpp"
g++ -O2 -shared -fPIC -o "$CPP_DIR/heap.so"    "$CPP_DIR/heap.cpp"
g++ -O2 -shared -fPIC -o "$CPP_DIR/ds_misc.so" "$CPP_DIR/ds_misc.cpp"

echo "==> Build complete."
ls -lh "$CPP_DIR"/*.so
