# Local Multi-Project Dev Policy

Use this document when multiple local projects run on the same Mac and one of them must stay publicly reachable.

## Goal

Prevent new local projects from breaking:

- Bunny public service at `https://bunny.carroamix.com`
- Bunny local backend on port `8000`
- any always-on service that should survive normal daily development work

## Current Reserved Resources

Treat these as contracts on this Mac:

- Bunny local backend: `8000`
- Bunny public URL: `https://bunny.carroamix.com`
- Preguntalo local API: `8010`
- Preguntalo local web: `3000`

When a new project is created, do not reuse reserved ports unless you are intentionally replacing that service.

## What Is Automatic Today

These protections already exist:

- Bunny startup fails fast if another app takes port `8000`
- Bunny public start/status scripts check launchd and public health
- Preguntalo uses `8010` by default instead of `8000`
- Preguntalo has `npm run doctor` to catch port and config conflicts before development starts

## What Is Not Automatic Yet

Brand new repositories do not automatically know this policy.

That means a new project still needs one setup pass:

1. choose non-conflicting ports
2. add a `doctor` or preflight check
3. document the reserved-port rule in that repo

After that first setup, the repo can protect itself.

## Standard Rules For New Projects

Follow these rules every time you start a new local project:

1. Check this file before choosing ports.
2. Keep Bunny on `8000`.
3. Pick the next free API port, for example `8020`, `8030`, `8040`.
4. Keep web UIs on their own ports such as `3000`, `3001`, `3002` only if they do not collide.
5. Add a project-local `doctor` script that validates env files and port usage.
6. Put the chosen ports in `.env.example`, real `.env`, Docker config, and README on the first day.

## New Project Checklist

Use this checklist when a new repo is created:

1. Decide whether the project is:
   - local-only
   - always-on local service
   - public-facing service
2. Reserve ports before writing app code.
3. Add `.env.example` with explicit `API_PORT` and frontend base URLs.
4. Add a `doctor` script.
5. Add a README section called `Local Run` or `Execution`.
6. If the project must stay available after login, use launchd or another supervisor.
7. If the project gets a public hostname, document the tunnel/proxy relationship separately.

## Doctor Script Requirements

Each new repo should have a small preflight script that checks:

- reserved Bunny port `8000` is not reused
- the repo's own API port and frontend URL agree
- the chosen port is not already listening

Preguntalo is the current reference implementation:

- doctor script: [`/Users/sclshin/Projects/preguntalo/scripts/dev_doctor.sh`](/Users/sclshin/Projects/preguntalo/scripts/dev_doctor.sh)
- command: `npm run doctor`

## Recommended Workflow With Codex

The safest pattern is to say this once when starting a new repo:

`This is a new local project. Apply the local multi-project dev policy, reserve ports, add a doctor script, and avoid breaking Bunny.`

That is enough context for setup work.

You do not need to paste this whole document every time, but you do need to mention that the repo is a new project unless the repo already has its own doctor/preflight flow.

## Recommended Workflow Without Codex

If you are setting up a repo manually:

1. open this document
2. choose ports that do not collide
3. add env defaults
4. add a preflight script
5. run the preflight script before first launch

## Operational Commands

Useful Bunny commands:

- start or recover public service: `bash scripts/bunny_public_start.sh`
- check Bunny local/public health: `bash scripts/bunny_public_status.sh`
- stop Bunny-managed services: `bash scripts/bunny_public_stop.sh`

Useful Preguntalo command:

- validate config before development: `cd /Users/sclshin/Projects/preguntalo && npm run doctor`

## If A Conflict Happens Again

Use this order:

1. check Bunny status
2. identify which process took the conflicting port
3. move the new project to another port
4. rerun Bunny public start

Do not solve future conflicts by moving Bunny off `8000` unless you are intentionally changing the service contract.
