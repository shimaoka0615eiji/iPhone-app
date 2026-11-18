#!/usr/bin/env python3
"""src/template.html にライブラリとモデルを埋め込み、単一の gyotaku.html を作る。

使い方: python3 build.py <onnxruntime-web/dist ディレクトリ> <u2netp.onnx>
"""
import base64, gzip, sys, pathlib

dist = pathlib.Path(sys.argv[1])
model = pathlib.Path(sys.argv[2])
root = pathlib.Path(__file__).parent
tpl = (root / "src" / "template.html").read_text(encoding="utf-8")

def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")

ort_js = (dist / "ort.wasm.min.js").read_text(encoding="utf-8")
assert "</script" not in ort_js.lower()
glue = (dist / "ort-wasm-simd-threaded.mjs").read_text(encoding="utf-8")
# blob: URL からの相対パス解決は失敗するため、使われない wasm パスの計算を固定文字列に置き換える
bad = '(new URL("ort-wasm-simd-threaded.wasm",import.meta.url)).href'
assert glue.count(bad) == 1
glue = glue.replace(bad, '"ort-wasm-simd-threaded.wasm"')
repl = {
    "/*__ORT_JS__*/": ort_js,
    "/*__ORT_GLUE_B64__*/": b64(glue.encode("utf-8")),
    "/*__ORT_WASM_GZ_B64__*/": b64(gzip.compress((dist / "ort-wasm-simd-threaded.wasm").read_bytes(), 9, mtime=0)),
    "/*__MODEL_GZ_B64__*/": b64(gzip.compress(model.read_bytes(), 9, mtime=0)),
}
for k, v in repl.items():
    assert tpl.count(k) == 1, k
    tpl = tpl.replace(k, v)
out = root / "gyotaku.html"
out.write_text(tpl, encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size/1e6:.1f} MB)")
