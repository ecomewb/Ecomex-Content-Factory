import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.render import render_deck, to_pdf
deck = json.loads(Path(sys.argv[1] if len(sys.argv)>1 else "tests/sample_deck.json").read_text())
master = Path(sys.argv[2] if len(sys.argv)>2 else "masters/demo_master.pptx")
pptx, rep = render_deck(deck, master)
Path("tests/out").mkdir(exist_ok=True)
Path("tests/out/sample.pptx").write_bytes(pptx)
Path("tests/out/sample.pdf").write_bytes(to_pdf(pptx))
print(json.dumps(rep, ensure_ascii=False, indent=1, default=str))
