# macOS Auto Start

Use this flow if you want `bunny-app` to start automatically after your Mac boots and you log in.

This setup uses user-level `launchd` agents because the project depends on:

- your user workspace under `/Users/sclshin/Projects`
- your login keychain for the Cloudflare tunnel token

That means the service starts automatically after login, not before the macOS login screen.

## What Starts Automatically

Two launch agents are installed:

- `com.sclshin.bunny.backend`
- `com.sclshin.bunny.tunnel`

They run these existing scripts directly:

- [`scripts/run_real_demo.sh`](/Users/sclshin/Projects/bunny-app/scripts/run_real_demo.sh)
- [`scripts/run_cloudflare_public_tunnel.sh`](/Users/sclshin/Projects/bunny-app/scripts/run_cloudflare_public_tunnel.sh)

## One-Time Setup

1. Make sure the backend works manually first:

```bash
bash scripts/run_real_demo.sh
```

2. Make sure your Cloudflare tunnel token is already stored in Keychain:

```bash
bash scripts/store_cloudflare_tunnel_token.sh
```

3. Install the launch agents:

```bash
bash scripts/install_macos_launch_agents.sh
```

## Check Status

```bash
bash scripts/bunny_launchd_status.sh
```

Useful logs:

- `run/launchd-backend.log`
- `run/launchd-tunnel.log`

## Remove Auto Start

```bash
bash scripts/uninstall_macos_launch_agents.sh
```

## Notes

- `launchd` has a minimal environment, so the plist templates set a fixed `PATH` that includes `/opt/homebrew/bin`.
- If `cloudflared`, `whisper-cli`, or the `bunny2` virtualenv moves, reinstall the agents after updating your paths.
- If you need a true pre-login boot service, that should be a system `LaunchDaemon`, but this project is not a good fit for that because it reads from your login keychain.
