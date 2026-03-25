# bunny.carroamix.com Setup Checklist

This checklist is for the exact target hostname:

- `bunny.carroamix.com`

It assumes:

- the backend runs on this Mac at `http://127.0.0.1:8000`
- you want other people to join from outside your network
- you want to keep using this Mac as the live host for now

## Current Local Status

Before the public setup, make sure the local backend is healthy:

```bash
curl -s --max-time 5 http://127.0.0.1:8000/healthz
```

Expected:

- `status: ok`
- `asr.ready: true`
- `translation.ready: true`

## Step 1. Create A Cloudflare Account

If you do not already have one, create a free Cloudflare account:

- <https://dash.cloudflare.com/sign-up>

## Step 2. Add carroamix.com To Cloudflare

In Cloudflare dashboard:

1. Select `Add a domain`.
2. Enter `carroamix.com`.
3. Choose the free plan.
4. Let Cloudflare scan the current DNS records.
5. Review the imported records carefully.

Important:

- If `carroamix.com` already uses a website or email, make sure the existing `A`, `CNAME`, `MX`, and `TXT` records are preserved before changing nameservers.

Official docs:

- <https://developers.cloudflare.com/learning-paths/get-started/add-domain-to-cf/>

## Step 3. Change Nameservers In GoDaddy

Cloudflare will show you two nameservers.

In GoDaddy:

1. Open `My Products`.
2. Select `carroamix.com`.
3. Find the `Nameservers` section.
4. Choose `Change`.
5. Choose the option to use your own nameservers.
6. Replace the existing nameservers with the two Cloudflare nameservers.
7. Save.

Wait until Cloudflare shows the domain as active.

Official docs:

- Cloudflare nameserver update:
  <https://developers.cloudflare.com/learning-paths/get-started/add-domain-to-cf/update-nameservers/>

## Step 4. Create A Named Tunnel

In Cloudflare dashboard:

1. Open `Zero Trust`.
2. Go to `Networks` -> `Tunnels`.
3. Create a new tunnel.
4. Name it something like `bunny-app-mac`.

Official docs:

- <https://developers.cloudflare.com/tunnel/setup/>

## Step 5. Add The Public Hostname

Inside the tunnel:

1. Go to `Routes`.
2. Select `Add route`.
3. Choose `Published application`.
4. Configure:
   - subdomain: `bunny`
   - domain: `carroamix.com`
   - service URL: `http://127.0.0.1:8000`
5. Save the route.

This should create:

- `https://bunny.carroamix.com`

Official docs:

- <https://developers.cloudflare.com/tunnel/setup/>
- <https://developers.cloudflare.com/tunnel/routing/>

## Step 6. Copy The Tunnel Token

In the same tunnel:

1. Select the tunnel.
2. Choose `Add a replica` or the install command view.
3. Copy the `cloudflared` command.
4. Extract the token value that starts with `eyJ...`

Official docs:

- <https://developers.cloudflare.com/tunnel/advanced/tunnel-tokens/>

## Step 7. Run It On This Mac

From the repo root:

```bash
bash scripts/run_real_demo.sh
```

Then:

```bash
export BUNNY_CLOUDFLARE_TUNNEL_TOKEN="paste-token-here"
bash scripts/run_cloudflare_public_tunnel.sh
```

## Step 8. Test The Public URL

Open:

- `https://bunny.carroamix.com`

Then:

1. Create a room.
2. Use the invite controls to send the link.
3. Open the received link on another device.

## Daily Usage

Whenever you want the service live:

1. start the backend
2. start the tunnel
3. keep this Mac awake

## Notes

- If this Mac sleeps, the public site stops.
- If you later move to a VM, you can keep the same hostname and point the tunnel there.
