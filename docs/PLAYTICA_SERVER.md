# Playtica Server Deployment

This flow moves `bunny.carroamix.com` off the local Mac and onto the Playtica server.

## What Changes

- the backend runs on Playtica at `127.0.0.1:8000`
- the public hostname stays `https://bunny.carroamix.com`
- a Cloudflare tunnel runs from Playtica instead of the Mac
- the server keeps the service alive with a small supervisor plus `crontab @reboot`

## Server Assumptions

- repo path: `/home/scshin/projects/bunny-app`
- user: `scshin`
- SSH alias: `playtica`
- public tunnel token stored at `/home/scshin/.config/bunny-app/cloudflare.token`
- model files stored under `/home/scshin/projects/bunny-app/models`

## Files To Prepare

1. Copy `.env.playtica.example` to `.env.playtica`
2. Adjust any absolute paths if the server layout differs
3. Create the tunnel token file with mode `600`

## Install Runtime

From the repo root on Playtica:

```bash
bash scripts/install_playtica_runtime.sh
```

This installs:

- Python packages into the user site-packages
- `cloudflared` into `~/.local/bin`
- `whisper-cli` into `~/.local/bin`

## Copy Models

Required server model paths:

- `models/whisper/ggml-large-v3-turbo.bin`
- `models/whisper/ggml-silero-v6.2.0.bin`
- `models/nllb-200-distilled-600M-ct2/`

## Start Public Service

```bash
cp .env.playtica.example .env.playtica
mkdir -p ~/.config/bunny-app
chmod 700 ~/.config/bunny-app
printf '%s' 'YOUR_CLOUDFLARE_TUNNEL_TOKEN' > ~/.config/bunny-app/cloudflare.token
chmod 600 ~/.config/bunny-app/cloudflare.token
bash scripts/bunny_playtica_public_start.sh
```

## Keep It Running Across Reboots

```bash
bash scripts/install_playtica_cron.sh
```

To launch the loop immediately:

```bash
nohup bash scripts/bunny_playtica_public_supervisor.sh >> run/supervisor.log 2>&1 &
```

## Cutover

Once Playtica is healthy:

1. stop the Mac tunnel and Mac backend
2. keep the Playtica tunnel running
3. verify `https://bunny.carroamix.com/healthz`

The easiest verification is checking that `healthz` no longer reports `/Users/sclshin/...` paths and instead shows `/home/scshin/...`.
