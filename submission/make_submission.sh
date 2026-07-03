#!/bin/zsh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIDEO="${1:-$ROOT/submission/evidence/jenkins実行動画_HW25A064.mp4}"
LOG="${2:-$ROOT/submission/evidence/jenkins_console_HW25A064.txt}"
FINAL="$ROOT/submission/final"
ZIP="$ROOT/HW25A064_スクリプトプログラミング演習2_提出.zip"

if [[ ! -f "$VIDEO" ]]; then echo "動画がありません: $VIDEO" >&2; exit 1; fi
if [[ ! -f "$LOG" ]]; then echo "Jenkinsログがありません: $LOG" >&2; exit 1; fi
if ! grep -q "Finished: SUCCESS" "$LOG"; then echo "成功ログではありません" >&2; exit 1; fi

rm -rf "$FINAL" "$ZIP"
mkdir -p "$FINAL/project" "$FINAL/output" "$FINAL/evidence" "$FINAL/report"
rsync -a --exclude '.git' --exclude 'submission/final' --exclude 'submission/evidence' --exclude 'output' "$ROOT/" "$FINAL/project/"
cp "$ROOT/output/earthquakes.json" "$ROOT/output/earthquakes.csv" "$ROOT/output/index.html" "$ROOT/output/build_summary.json" "$FINAL/output/"
cp "$VIDEO" "$FINAL/evidence/jenkins実行動画_HW25A064.mp4"
cp "$LOG" "$FINAL/evidence/jenkins_console_HW25A064.txt"
cp "$ROOT/HW25A064_最終レポート.pdf" "$FINAL/report/"

cd "$ROOT/submission"
/usr/bin/zip -qr "$ZIP" final

echo "作成完了: $ZIP"
