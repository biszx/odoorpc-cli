#!/usr/bin/env bash

# bump_version.sh – update package version in __init__.py and Homebrew formula
# Usage: ./bump_version.sh <new_version>
# Example: ./bump_version.sh 1.3.0

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <new_version>"
  exit 1
fi

NEW_VERSION="$1"

# Paths (relative to project root)
INIT_PY="odoorpc_cli/__init__.py"
FORMULA="tap/Formula/odoorpc_cli.rb"

# Update __init__.py
if [[ -f "$INIT_PY" ]]; then
  sed -i '' -E "s/^(__version__ = \").*(\")/\1$NEW_VERSION\2/" "$INIT_PY"
  echo "Updated $INIT_PY to version $NEW_VERSION"
else
  echo "Error: $INIT_PY not found"
  exit 1
fi

# Update version line in Homebrew formula
if [[ -f "$FORMULA" ]]; then
  sed -i '' -E "s/^(  version \").*(\")/\1$NEW_VERSION\2/" "$FORMULA"
  echo "Updated $FORMULA to version $NEW_VERSION"
else
  echo "Error: $FORMULA not found"
  exit 1
fi

echo "Version bump complete."
