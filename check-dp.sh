#!/bin/bash
# Manual DP Check Script with Telegram Update
# Run this to check DP and get result on Telegram

cd /teamspace/studios/this_studio/dp-tracker

echo "=== Starting Manual DP Check ==="
echo ""

# Build if needed
npx tsc 2>/dev/null

# Run the check
node dist/manual-check.js

echo ""
echo "=== Check Complete ==="
