from pathlib import Path
import base64
import zlib

root = Path(__file__).resolve().parents[1]
payload = "".join(
    (root / f"scripts/_pv_payload_{index:02d}.txt").read_text(encoding="utf-8").strip()
    for index in range(3)
)
code = zlib.decompress(base64.b64decode(payload)).decode("utf-8")
exec(
    compile(code, "pv_visual_migration", "exec"),
    {
        "__file__": str(root / "scripts/_apply_pv_visual_review.py"),
        "__name__": "__main__",
    },
)
