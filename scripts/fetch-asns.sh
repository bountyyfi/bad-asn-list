#!/bin/bash
# Fetch ASNs from various sources and compare with our list

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIST_FILE="$SCRIPT_DIR/../all.txt"
TEMP_DIR=$(mktemp -d)

echo "=== Fetching ASNs from external sources ==="

# Extract current ASN numbers from our list
echo "Extracting current ASNs..."
grep -oE '^AS[0-9]+' "$LIST_FILE" | sed 's/AS//' | sort -n | uniq > "$TEMP_DIR/current.txt"
CURRENT_COUNT=$(wc -l < "$TEMP_DIR/current.txt")
echo "Current list: $CURRENT_COUNT ASNs"

# Fetch X4BNet datacenter ASN list
echo ""
echo "Fetching X4BNet datacenter ASN list..."
curl -s "https://raw.githubusercontent.com/X4BNet/lists_vpn/main/input/datacenter/ASN.txt" 2>/dev/null | \
    grep -oE '^[0-9]+' | sort -n | uniq > "$TEMP_DIR/x4bnet.txt" || echo "Failed to fetch X4BNet list"

if [ -s "$TEMP_DIR/x4bnet.txt" ]; then
    X4B_COUNT=$(wc -l < "$TEMP_DIR/x4bnet.txt")
    echo "X4BNet list: $X4B_COUNT ASNs"

    # Find missing ASNs
    comm -23 "$TEMP_DIR/x4bnet.txt" "$TEMP_DIR/current.txt" > "$TEMP_DIR/x4bnet_missing.txt"
    MISSING=$(wc -l < "$TEMP_DIR/x4bnet_missing.txt")
    echo "Missing from our list: $MISSING ASNs"

    if [ "$MISSING" -gt 0 ] && [ "$MISSING" -lt 50 ]; then
        echo ""
        echo "Missing ASNs from X4BNet:"
        head -20 "$TEMP_DIR/x4bnet_missing.txt" | while read asn; do
            echo "AS$asn"
        done
        if [ "$MISSING" -gt 20 ]; then
            echo "... and $((MISSING - 20)) more"
        fi
    fi
fi

# Fetch brianhama bad-asn-list
echo ""
echo "Fetching brianhama/bad-asn-list..."
curl -s "https://raw.githubusercontent.com/brianhama/bad-asn-list/master/bad-asn-list.csv" 2>/dev/null | \
    tail -n +2 | cut -d',' -f1 | grep -oE '[0-9]+' | sort -n | uniq > "$TEMP_DIR/brianhama.txt" || echo "Failed to fetch brianhama list"

if [ -s "$TEMP_DIR/brianhama.txt" ]; then
    BH_COUNT=$(wc -l < "$TEMP_DIR/brianhama.txt")
    echo "brianhama list: $BH_COUNT ASNs"

    comm -23 "$TEMP_DIR/brianhama.txt" "$TEMP_DIR/current.txt" > "$TEMP_DIR/brianhama_missing.txt"
    MISSING=$(wc -l < "$TEMP_DIR/brianhama_missing.txt")
    echo "Missing from our list: $MISSING ASNs"
fi

# Fetch ipapi.is abusive ASN list (if available)
echo ""
echo "Checking ipapi.is..."
# Note: ipapi.is requires API access, showing placeholder
echo "ipapi.is requires API access - visit https://ipapi.is/most-abusive-asn.html manually"

# Summary
echo ""
echo "=== Summary ==="
echo "Current list: $CURRENT_COUNT ASNs"
echo ""
echo "To add missing ASNs, check:"
echo "  $TEMP_DIR/x4bnet_missing.txt"
echo "  $TEMP_DIR/brianhama_missing.txt"
echo ""
echo "Manual sources to check:"
echo "  - https://ipapi.is/most-abusive-asn.html"
echo "  - https://spur.us/ (requires account)"
echo "  - https://github.com/X4BNet/lists_vpn"
echo "  - https://www.spamhaus.org/blocklists/do-not-route-or-peer/"

# Cleanup option
echo ""
read -p "Clean up temp files? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$TEMP_DIR"
    echo "Cleaned up."
else
    echo "Temp files at: $TEMP_DIR"
fi
