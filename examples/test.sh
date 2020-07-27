#!/bin/bash
set -euf -o pipefail

python -m wgadmin new-network --force wg.json
python -m wgadmin add-peer wg.json server --endpoint example.org
python -m wgadmin add-peer wg.json laptop
python -m wgadmin add-connection wg.json laptop server
python -m wgadmin list-peers wg.json
