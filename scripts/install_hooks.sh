#!/bin/sh
# Install the pre-commit check. Git hooks are not versioned, so a fresh clone
# has none -- run this once after cloning.
#
#   sh scripts/install_hooks.sh
set -e
root=$(git rev-parse --show-toplevel)
cat > "$root/.git/hooks/pre-commit" <<'HOOK'
#!/bin/sh
# See CHECKS.md. sync_troubles.py writes new failures into TROUBLES.md and
# stages it, so nothing is lost; check_repo.py then blocks until each one has
# been put under a type.
root=$(git rev-parse --show-toplevel)
python3 "$root/scripts/sync_troubles.py" || exit 1
exec python3 "$root/scripts/check_repo.py"
HOOK
chmod +x "$root/.git/hooks/pre-commit"
echo "installed $root/.git/hooks/pre-commit"
