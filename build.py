#!/usr/bin/env python3
"""src/template.html にライブラリとモデルを埋め込み、単一の gyotaku.html を作る。

使い方: python3 build.py <onnxruntime-web/dist ディレクトリ> <u2netp.onnx>
"""
import base64, gzip, hashlib, re, shutil, sys, pathlib

dist = pathlib.Path(sys.argv[1])
model = pathlib.Path(sys.argv[2])
root = pathlib.Path(__file__).parent
tpl = (root / "src" / "template.html").read_text(encoding="utf-8")

def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")

ort_js = (dist / "ort.bundle.min.mjs").read_text(encoding="utf-8")
assert "</script" not in ort_js.lower() and "<!--" not in ort_js
# ES モジュールの export 文を、グローバル変数 ort への代入に置き換える
m = re.search(r"export\{([^}]*)\}", ort_js)
names = dict(reversed(x.split(" as ")) for x in m.group(1).split(","))
ort_js = ort_js[:m.start()] + "globalThis.ort={InferenceSession:%s,Tensor:%s,env:%s};" % (
    names["InferenceSession"], names["Tensor"], names["env"]) + ort_js[m.end():]
repl = {
    "/*__ORT_JS__*/": ort_js,
    "/*__ORT_WASM_GZ_B64__*/": b64(gzip.compress((dist / "ort-wasm-simd-threaded.wasm").read_bytes(), 9, mtime=0)),
    "/*__MODEL_GZ_B64__*/": b64(gzip.compress(model.read_bytes(), 9, mtime=0)),
}
for k, v in repl.items():
    assert tpl.count(k) == 1, k
    tpl = tpl.replace(k, v)
out = root / "gyotaku.html"
out.write_text(tpl, encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size/1e6:.1f} MB)")

# Claude のページ（Artifact）用：外側の html/head/body タグを外した版
art = tpl
art = re.sub(r"<!DOCTYPE html>\s*<html[^>]*>\s*<head>", "", art, count=1)
art = art.replace("</head>\n<body>", "", 1)
art = art.replace("</body>\n</html>", "", 1)
art = re.sub(r'<meta charset="utf-8">\s*<meta name="viewport"[^>]*>\s*', "", art, count=1)
art = art.replace("<title>魚拓風写真アプリ</title>", "<title>魚拓写真</title>", 1)
assert "<body>" not in art and "<html" not in art
out2 = root / "artifact" / "gyotaku-artifact.html"
out2.parent.mkdir(exist_ok=True)
out2.write_text(art, encoding="utf-8")
print(f"wrote {out2} ({out2.stat().st_size/1e6:.1f} MB)")

# GitHub Pages 用：ホーム画面に追加でき、オフラインでも動く版（index.html ＋ 付属ファイル）
pwa_head = """<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="魚拓写真">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
</head>"""
pwa_sw = """<script>
if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
}
</script>
</body>"""
web = tpl.replace("</head>", pwa_head, 1)
web = web[: web.rindex("</body>")] + pwa_sw + web[web.rindex("</body>") + len("</body>"):]
(root / "index.html").write_text(web, encoding="utf-8")
pwa = root / "src" / "pwa"
for f in ["manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png"]:
    shutil.copy(pwa / f, root / f)
version = hashlib.sha256(web.encode("utf-8")).hexdigest()[:10]
(root / "sw.js").write_text((pwa / "sw.js").read_text(encoding="utf-8").replace("__VERSION__", version), encoding="utf-8")
(root / ".nojekyll").write_text("")
print(f"wrote index.html + sw.js (version {version})")
