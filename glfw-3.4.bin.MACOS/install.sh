#!/bin/bash

set -e

# install.sh'nin kendi dizini (betiğin bulunduğu dizin)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARGET_DIR="vendor"
ARCH=$(uname -m)

echo "[INFO] Installing GLFW locally to: $TARGET_DIR/"
echo "[INFO] Detected architecture: $ARCH"

# 1. Include dosyaları
mkdir -p "$TARGET_DIR/include/GLFW"
cp -r "$SCRIPT_DIR/include/GLFW/"* "$TARGET_DIR/include/GLFW/"

# 2. Mimariye göre lib klasörü seç
case "$ARCH" in
  arm64)
    LIBDIR="lib-arm64"
    ;;
  x86_64)
    LIBDIR="lib-x86_64"
    ;;
  *)
    echo "[ERROR] Unsupported architecture: $ARCH"
    exit 1
    ;;
esac

# 3. Lib dosyaları
mkdir -p "$TARGET_DIR/lib"
cp -r "$SCRIPT_DIR/$LIBDIR/"* "$TARGET_DIR/lib/"

echo "[SUCCESS] GLFW installed to ./$TARGET_DIR"
