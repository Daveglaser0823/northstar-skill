#!/usr/bin/env bash
# Northstar Installer
# Installs the Northstar skill and configures it for use with OpenClaw.

set -e

SKILL_DIR="$HOME/.clawd/skills/northstar"
SCRIPTS_DIR="$SKILL_DIR/scripts"
CONFIG_DIR="$SKILL_DIR/config"
BIN_DIR="/usr/local/bin"

echo "Installing Northstar Daily Business Briefing..."
echo ""

# Create directories
mkdir -p "$SCRIPTS_DIR" "$CONFIG_DIR"

# Copy scripts
INSTALL_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$INSTALL_SRC/northstar.py" "$SCRIPTS_DIR/northstar.py"
chmod +x "$SCRIPTS_DIR/northstar.py"

# Copy config example (don't overwrite existing config)
CONFIG_EXAMPLE="$(cd "$INSTALL_SRC/.." && pwd)/config/northstar.json.example"
if [ -f "$CONFIG_EXAMPLE" ]; then
    cp "$CONFIG_EXAMPLE" "$CONFIG_DIR/northstar.json.example"
    if [ ! -f "$CONFIG_DIR/northstar.json" ]; then
        cp "$CONFIG_EXAMPLE" "$CONFIG_DIR/northstar.json"
        echo "  ✓ Config created at: $CONFIG_DIR/northstar.json"
        echo "    Edit it with your API keys before running."
    else
        echo "  ✓ Config already exists (not overwritten): $CONFIG_DIR/northstar.json"
    fi
fi

# Create wrapper script in /usr/local/bin
WRAPPER="$BIN_DIR/northstar"
cat > "$WRAPPER" << 'EOF'
#!/usr/bin/env bash
exec python3 "$HOME/.clawd/skills/northstar/scripts/northstar.py" "$@"
EOF
chmod +x "$WRAPPER"
echo "  ✓ Installed: $WRAPPER"

# Install Python dependencies
echo ""
echo "Checking Python dependencies..."
python3 -c "import stripe" 2>/dev/null || {
    echo "  Installing stripe..."
    pip3 install stripe -q
}
echo "  ✓ Dependencies ready"

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit your config: $CONFIG_DIR/northstar.json"
echo "  2. Add your Stripe API key (and Shopify if needed)"
echo "  3. Test it: northstar test"
echo "  4. Schedule it (optional): add to OpenClaw cron"
echo "     0 6 * * * northstar run"
echo ""
echo "Docs: See SKILL.md in the northstar skill directory"
