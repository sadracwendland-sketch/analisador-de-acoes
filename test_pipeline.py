from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path('/home/user/stock-analyzer/backend')
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.services.pipeline import run_full_analysis

payload = run_full_analysis('AAPL', '1d', 100000, 7)
print(json.dumps({
    'ticker': payload['ticker'],
    'signal': payload['signal'],
    'forecast': payload['forecast'],
    'risk': payload['risk'],
    'backtest_stats': payload['backtest']['stats'],
    'rows': payload['meta'],
}, ensure_ascii=False, indent=2))
