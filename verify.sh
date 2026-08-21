#!/usr/bin/env bash
# Verify how the deployed demo classifies requests.
#
# Usage:
#   ./verify.sh <deployment-url> default   # expect: is_local=true, /admin 200 (the bug)
#   ./verify.sh <deployment-url> star      # after DEMO_TRUSTED_PROXY=* : expect real IP, /admin 403
set -u

URL="${1:?usage: ./verify.sh <url> [default|star]}"
MODE="${2:-default}"
FAIL=0

check() { # name expected actual
    if [ "$2" = "$3" ]; then
        printf 'PASS  %-42s %s\n' "$1" "$3"
    else
        printf 'FAIL  %-42s expected=%s actual=%s\n' "$1" "$2" "$3"
        FAIL=1
    fi
}

WHO=$(curl -fsS "$URL/whoami") || { echo "cannot reach $URL/whoami"; exit 1; }
ADMIN=$(curl -s -o /dev/null -w '%{http_code}' "$URL/admin")

CLIENT_HOST=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['client_host'])" "$WHO")
IS_LOCAL=$(python3 -c "import json,sys;print(str(json.loads(sys.argv[1])['is_local']).lower())" "$WHO")
XFF=$(python3 -c "import json,sys;print(json.loads(sys.argv[1])['x_forwarded_for'])" "$WHO")

echo "== $MODE mode @ $URL"
echo "whoami: $WHO"
echo

if [ "$MODE" = "star" ]; then
    MY_IP=$(curl -fsS https://api.ipify.org)
    check "client_host == my public IP ($MY_IP)" "$MY_IP" "$CLIENT_HOST"
    check "is_local" "false" "$IS_LOCAL"
    check "/admin status" "403" "$ADMIN"
else
    check "is_local (edge IP counts as local)" "true" "$IS_LOCAL"
    check "/admin status (anonymous admin!)" "200" "$ADMIN"
fi

echo
[ "$FAIL" -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $FAIL
