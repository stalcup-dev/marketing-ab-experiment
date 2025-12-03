import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"  # decision_pack/src
sys.path.insert(0, str(SRC))
