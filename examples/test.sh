#!/bin/bash
set -euf -o pipefail

python -m wgadmin new-network --force
python -m wgadmin add-peer server --endpoint fkoehler.xyz
python -m wgadmin add-peer laptop
python -m wgadmin add-peer workstation
python -m wgadmin add-connection laptop server
python -m wgadmin add-connection workstation server
python -m wgadmin list-peers
python -m wgadmin generate-all-configs
