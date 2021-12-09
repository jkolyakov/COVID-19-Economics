#!/bin/sh

set -e

apk add python3
apk add python3-dev
apk add py3-pip

# Runtime dependencies
apk add py3-pandas

# Test dependencies
apk add py3-pytest
apk add py3-hypothesis
