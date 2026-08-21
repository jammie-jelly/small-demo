# small-demo

Minimal FastAPI repro of the clinic app's network-based admin gate, deployed to
Vercel to confirm how `request.client.host` / `X-Forwarded-For` behave behind
Vercel's proxy.

Mirrors the clinic stack exactly:

* in-app `uvicorn.middleware.proxy_headers.ProxyHeadersMiddleware`, added
  **outermost**, trusting `DEMO_TRUSTED_PROXY` (default loopback `127.0.0.1/32,::1/128`)
* `is_local()` = peer IP within `DEMO_ALLOWED_NETWORKS`
  (default loopback + RFC1918 private ranges — same list as the clinic app)
* `/admin` returns **200 for any request classified as local** (no session logic)

## Endpoints

| Route | Behavior |
| --- | --- |
| `GET /whoami` | JSON: resolved `client_host`, raw `x_forwarded_for`, `is_local`, active `trusted_proxies` |
| `GET /admin` | 200 if `is_local`, else 403 |

## Expected results on Vercel

| Config | `client_host` | `is_local` | `/admin` |
| --- | --- | --- | --- |
| default (`DEMO_TRUSTED_PROXY` unset) | Vercel internal edge IP (private range) | **true** | **200 — anonymous admin** |
| `DEMO_TRUSTED_PROXY=*` (Vercel overwrites XFF) | visitor's real public IP | false | 403 |

Caveat: with `*`, if a request arrives **without** `X-Forwarded-For`, the raw
peer address is used — which on Vercel is still a private edge IP → local →
admin. Safe only because Vercel always sets XFF; never reuse `*` on an
infrastructure that doesn't guarantee it.

## Verify

```bash
./verify.sh https://<deployment>.vercel.app default   # before setting env var
# then: vercel env add DEMO_TRUSTED_PROXY  # value: *
./verify.sh https://<deployment>.vercel.app star      # after redeploy
```

Exit code 0 = all checks passed.

## Local run

```bash
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

Note: with the default config a direct local connection is admin (loopback is
trusted) — that is correct and mirrors the clinic app's dev behavior.
