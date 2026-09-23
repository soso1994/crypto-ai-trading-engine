from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services' / 'ingest'))
from signals import build_signal_contract


def test_long_contract_has_ordered_targets():
    signal = build_signal_contract('btcusdt', '15m', {'signal': 'buy', 'confidence': .8, 'price': 100, 'atr': 4})
    assert signal['side'] == 'LONG'
    assert signal['stop_loss'] < signal['entry_price'] < signal['take_profit']
    assert signal['mode'] == 'signal_only'
    assert signal['execution_required'] is False


def test_short_contract_has_ordered_targets():
    signal = build_signal_contract('BTCUSDT', '15m', {'signal': 'sell', 'confidence': .7, 'price': 100, 'atr': 4})
    assert signal['side'] == 'SHORT'
    assert signal['take_profit'] < signal['entry_price'] < signal['stop_loss']


def test_flat_contract_has_no_targets():
    signal = build_signal_contract('BTCUSDT', '15m', {'signal': 'hold', 'confidence': .5, 'price': 100, 'atr': 4})
    assert signal['side'] == 'FLAT'
    assert signal['stop_loss'] is None
    assert signal['take_profit'] is None
