# macOS Public Launcher

Use this flow when you want a simple desktop launcher for:

- starting the local backend
- starting the Cloudflare tunnel for `bunny.carroamix.com`
- stopping both later

If you want the same service to come up automatically whenever you log in to macOS, use [`docs/MAC_AUTOSTART.md`](/Users/sclshin/Projects/bunny-app/docs/MAC_AUTOSTART.md).

## Recommended Token Handling

The Cloudflare tunnel token should not live in shell history.

### 1. Refresh the tunnel token in Cloudflare

Inside the tunnel connector modal:

1. choose `Refresh token`
2. copy the new token or the new `cloudflared tunnel run --token ...` command

### 2. Store the refreshed token in the macOS Keychain

From the repo root:

```bash
bash scripts/store_cloudflare_tunnel_token.sh "paste-new-token-here"
```

If you omit the token argument, the script will prompt for it.

## Daily Scripts

### Start everything

```bash
bash scripts/bunny_public_start.sh
```

This will:

- start the backend if it is not already running
- wait for `/healthz`
- start the Cloudflare tunnel

Logs:

- backend: `run/backend.log`
- tunnel: `run/tunnel.log`

### Stop everything

```bash
bash scripts/bunny_public_stop.sh
```

### Check status

```bash
bash scripts/bunny_public_status.sh
```

## Desktop Launcher Option

On macOS, the easiest stable launcher is a `.command` file or a small AppleScript app that runs:

```bash
cd /Users/sclshin/Projects/bunny-app
bash scripts/bunny_public_start.sh
```

If you want, Codex can create desktop launchers such as:

- `Bunny Public Start.app`
- `Bunny Public Stop.app`
- `Bunny Update Tunnel Token.app`

That step requires writing to your Desktop.

The AppleScript sources for those apps live in:

- [`BunnyPublicStart.applescript`](/Users/sclshin/Projects/bunny-app/macos/BunnyPublicStart.applescript)
- [`BunnyPublicStop.applescript`](/Users/sclshin/Projects/bunny-app/macos/BunnyPublicStop.applescript)
- [`BunnyUpdateTunnelToken.applescript`](/Users/sclshin/Projects/bunny-app/macos/BunnyUpdateTunnelToken.applescript)

## Recommended Daily Flow

1. In Cloudflare, choose `Refresh token`
2. Open `Bunny Update Tunnel Token.app`
3. Paste the new token
4. Open `Bunny Public Stop.app`
5. Open `Bunny Public Start.app`
