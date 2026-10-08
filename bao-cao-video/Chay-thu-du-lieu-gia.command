#!/bin/bash
# Bấm đúp để chạy thử trên DỮ LIỆU GIẢ (samples/demo) - không đụng tới dữ liệu thật.
cd "$(dirname "$0")" || exit 1
exec bash ./Chay-bao-cao.command --demo
