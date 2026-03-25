# Cloudflare Named Tunnel For A Short Public URL

Use this flow when you want a short stable URL like:

- `bunny.your-domain.com`
- `chat.your-domain.com`

instead of a random `trycloudflare.com` address.

## What This Solves

- shorter and easier public URL
- stable hostname you can reuse in demos
- HTTPS handled by Cloudflare

Your Mac still stays on and continues running the local backend.

## What You Need

1. a domain name that is managed by Cloudflare DNS
2. `cloudflared` installed on the Mac
3. the local backend running on `http://127.0.0.1:8000`

This repo already has `cloudflared` available.

## Recommended Hostname

Pick one short hostname:

- `bunny.your-domain.com`
- `talk.your-domain.com`
- `demo.your-domain.com`

## One-Time Setup In Cloudflare Dashboard

1. Open Cloudflare Zero Trust.
2. Go to `Networks` -> `Tunnels`.
3. Create a new tunnel.
4. Choose a tunnel name such as `bunny-app-mac`.
5. In the tunnel public hostname settings, add:
   - hostname: your short subdomain such as `bunny.your-domain.com`
   - service type: `HTTP`
   - URL: `http://127.0.0.1:8000`
6. Copy the tunnel token that Cloudflare shows.

Official docs:

- Cloudflare Tunnel setup: <https://developers.cloudflare.com/tunnel/setup/>
- Cloudflare routing and public hostnames: <https://developers.cloudflare.com/tunnel/routing/>

## Local Run

### 1. Start the backend

From the repo root:

```bash
bash scripts/run_real_demo.sh
```

### 2. Store the tunnel token safely

```bash
bash scripts/store_cloudflare_tunnel_token.sh "paste-your-token-here"
```

### 3. Start the named tunnel

```bash
bash scripts/run_cloudflare_public_tunnel.sh
```

Once the tunnel is connected, your short public URL will point to this Mac.

## Optional Shell Profile Setup

The tunnel runner also supports `BUNNY_CLOUDFLARE_TUNNEL_TOKEN`, but the Keychain approach is safer on macOS.

## Daily Run

Whenever you want the app public:

1. run `bash scripts/run_real_demo.sh`
2. run `bash scripts/run_cloudflare_public_tunnel.sh`

For a one-command local launcher, see:

- [`docs/MAC_PUBLIC_LAUNCHER.md`](/Users/sclshin/Projects/bunny-app/docs/MAC_PUBLIC_LAUNCHER.md)

## Notes

- This keeps using your Mac as the real backend host.
- If the Mac sleeps, the public URL stops working.
- If you later move to a VM, you can keep the same Cloudflare hostname and repoint the tunnel there.
