"""
Session-wide test setup.

Sets RATE_LIMIT_ENABLED=false in the environment BEFORE any test
module gets a chance to `import app.core.config` (which builds the
`settings` singleton at import time, reading environment variables
once). Rate limiting is Redis-backed (see app/api/rate_limit.py) and
persists real state across test runs; without this, the test suite's
own rapid-fire requests to endpoints like /auth/register would trip
the very rate limits Phase 9 added, making the suite flaky and
order-dependent. This conftest.py is the one pytest guarantees to
import first (root of the tests/ tree), which is exactly why it lives
here rather than in any nested conftest.py.
"""

import os

os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
