#!/bin/sh
# CI と同じ条件でテストする（CI のサーバーは UTC）
cd "$(dirname "$0")" && TZ=UTC python3 -W default -m unittest -v
