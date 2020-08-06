#!/bin/bash
set -euf -o pipefail

python -m wgadmin new-network --force
python -m wgadmin add-peer server --endpoint example.org
python -m wgadmin add-peer laptop
python -m wgadmin add-connection laptop server
python -m wgadmin list-peers
