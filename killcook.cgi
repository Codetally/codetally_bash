#!/bin/bash

echo "Set-Cookie: X-AUTH-TOKEN=deleted; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT"
echo "Location: /index.html"
echo "Status: 302"
echo ""
exit 0
