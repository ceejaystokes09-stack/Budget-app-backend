#!/usr/bin/env bash
set -e

cd "$(dirname "${BASH_SOURCE[0]}")/my-react-app"
npm run dev -- --host 0.0.0.0