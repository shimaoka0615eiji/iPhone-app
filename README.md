# 魚拓風写真アプリ

スマホのブラウザで動く、釣った魚の写真を魚拓風の画像にするアプリです。

- **公開URL（GitHub Pages）**：https://shimaoka0615eiji.github.io/iPhone-app/
  - `index.html` と付属ファイル（`sw.js`, `manifest.webmanifest`, `icon-*.png`）で動きます。
  - 一度開くと端末に保存され、ホーム画面に追加すればオフラインでも起動できます。
  - `qr-safari.png` … このURLを開くQRコード
- **`gyotaku.html`** … アプリ本体（この1ファイルだけで動きます。約10MB）
  - 背景除去AI（U²-Netp）と ONNX Runtime Web を内蔵しているため、**オフラインで動作**します。
  - 写真は端末内で処理され、外部へ送信されません。
- `artifact/gyotaku-artifact.html` … Claude のページ公開用（外側の html/head/body タグを外した版）
- `artifact/qr.png` … 公開ページ https://claude.ai/artifact/LgFsSRtSZ6RtMNet3cquEs を開く QR コード
  （非公開ページのため、開くには Claude へのログインが必要。他の人に使ってもらうにはページの「共有」から公開範囲を変更）
- `src/template.html` … アプリのソース（ライブラリ埋め込み前）
- `build.py` … ライブラリとモデルを埋め込んで `gyotaku.html` を作るスクリプト

## 作り直す場合

```bash
npm pack onnxruntime-web@1.20.1 && tar xzf onnxruntime-web-1.20.1.tgz
curl -L -o u2netp.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx
python3 build.py package/dist u2netp.onnx
```

## 動作環境

iOS 16.4 以降の Safari、Android の最近の Chrome など（WebAssembly SIMD と DecompressionStream が必要）。
古いブラウザでは自動切り抜きが使えませんが、ブラシで手作業の切り抜きはできます。

## ライセンス

- ONNX Runtime Web: MIT License (© Microsoft)
- U²-Net: Apache License 2.0 (© Xuebin Qin)
