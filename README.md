# Japan Earthquake Monitor - HW25A064

スクリプトプログラミング演習2の最終課題として作成した、**日本周辺の地震情報を自動取得・集計・可視化するJenkins Pipeline**です。

## 学生情報

- 学籍番号: HW25A064
- 氏名: 實光駿斗
- 開発環境: macOS

## 独自テーマ

元課題の候補にあるデータ取得・Web出力を発展させ、USGS Earthquake Catalog APIから日本周辺の地震情報を取得します。PythonでJSON/CSVを生成し、JavaScriptで検索・絞り込み・日別グラフを備えたHTMLダッシュボードを作ります。

## Jenkins処理

1. GitHubからソースをCheckout
2. Python / Node.js / Gitのバージョン確認
3. Python単体テスト
4. 地震データ取得（通信障害時は同梱fixtureへ安全に切替）
5. JavaScriptによるHTMLダッシュボード生成
6. JSON・CSV・HTML間の整合性検査
7. 4成果物をJenkins Artifactsへ保存
8. 設定されている場合のみDiscordへ結果通知

## 出力

- `output/earthquakes.json`
- `output/earthquakes.csv`
- `output/index.html`
- `output/build_summary.json`

## ローカル実行

```zsh
./run_local.sh --offline
```

実データを利用する場合:

```zsh
./run_local.sh
```

## セキュリティ

Discord Webhook、ngrok authtoken、GitHubトークンはリポジトリへ保存しません。秘密情報はJenkins Credentialsまたは各サービスの安全な設定画面にのみ入力します。

詳細は `submission/README_最初に読む.txt` を参照してください。
