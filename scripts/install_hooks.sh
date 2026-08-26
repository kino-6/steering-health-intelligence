#!/bin/sh
# Install the pre-commit check. Git hooks are not versioned, so a fresh clone
# has none -- run this once after cloning.
#
#   sh scripts/install_hooks.sh
set -e
root=$(git rev-parse --show-toplevel)
cat > "$root/.git/hooks/pre-commit" <<'HOOK'
#!/bin/sh
exec python3 "$(git rev-parse --show-toplevel)/scripts/check_repo.py"
HOOK
chmod +x "$root/.git/hooks/pre-commit"
echo "installed $root/.git/hooks/pre-commit"
