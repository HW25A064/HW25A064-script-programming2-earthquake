# Codex実行指示 - HW25A064 實光駿斗 / macOS

このフォルダの課題プロジェクトを監査し、本人のMac上で実際にGitHub・ngrok・Jenkinsを連携させ、最終提出ZIPを作成してください。

## 厳守事項

- 動画、Jenkinsログ、スクリーンショット、成功結果を捏造しない。
- トークン、パスワード、Discord Webhook URL、ngrok authtokenをソース・ログ・動画・Git履歴へ入れない。
- ログインや秘密情報入力が必要な場面だけ本人に入力を依頼して待機する。
- 手順説明だけで終わらず、最終ZIP生成まで進める。
- 既存コードを名前だけ変えた別人の提出物にせず、この地震情報テーマの独立実装を維持する。

## 1. 最初に読む

- README.md
- Jenkinsfile
- submission/README_最初に読む.txt
- submission/GitHub_ngrok_Jenkins設定手順.md
- submission/実行動画_撮影手順.md
- submission/Jenkinsログ_保存手順.md
- submission/提出前チェックリスト.txt
- submission/make_submission.sh

## 2. ローカル検証

```zsh
pwd
ls -la
python3 --version
node --version
git --version
./run_local.sh --offline
./run_local.sh
```

通信失敗時にfixtureへ切り替わることは許容するが、単体テストと4成果物の検証は必ず成功させる。

## 3. 必要ツール

不足していればHomebrewを利用する。

```zsh
brew install python node git ngrok jenkins-lts
brew install --cask temurin@17
```

Jenkinsを開始する。

```zsh
brew services start jenkins-lts
open http://localhost:8080
```

初回Jenkinsログインは本人へ依頼する。

## 4. GitHub

本人アカウントで `HW25A064-script-programming2-earthquake` を作成し、秘密情報がないことを検査してpushする。GitHubログインは本人へ依頼する。

## 5. Jenkins

`HW25A064-earthquake-dashboard` というPipelineジョブを作成する。

- Pipeline script from SCM
- Git
- 本人のリポジトリURL
- Branch `*/main`
- Script Path `Jenkinsfile`
- GitHub hook trigger for GITScm polling ON

まず手動ビルドを成功させる。必要ならPATHやJava設定を修正する。テストを削除・弱体化して成功させてはいけない。

## 6. ngrokとWebhook

```zsh
ngrok http 8080
```

認証が必要なら本人へ依頼する。GitHub Webhookを以下で設定する。

- `https://<ngrok公開URL>/github-webhook/`
- application/json
- Just the push event
- Active ON

Recent Deliveries、ngrokの `POST /github-webhook/ 200 OK`、Jenkins自動開始の3点を確認する。

## 7. Discord通知

本人がWebhookを用意できる場合だけJenkins CredentialsへSecret textで登録し、`DISCORD_WEBHOOK_URL` として使う。値を表示・保存しない。

## 8. 本番動画

リハーサル成功後、macOSの画面収録を使う。Codexが録画を開始できない場合だけ本人に `Shift + Command + 5` の操作を依頼する。

動画に必ず含める:

- Jenkinsジョブと最新ビルド番号
- ngrok onlineと転送先
- README変更、commit、push
- ngrok `POST /github-webhook/ 200 OK`
- Jenkins自動開始
- 全ステージ成功と `Finished: SUCCESS`
- 4 Artifacts
- index.htmlの一覧、検索、M絞り込み、日別グラフ

保存先:

```text
submission/evidence/jenkins実行動画_HW25A064.mp4
```

## 9. ログ

動画と同じ成功ビルドのConsole Outputを保存する。

```text
submission/evidence/jenkins_console_HW25A064.txt
```

## 10. レポート監査

`HW25A064_最終レポート.docx` とPDFを実際のリポジトリ名、ジョブ名、テスト件数、成果物、実行結果に合わせて更新する。架空のビルド番号や架空の証跡を書かない。DOCX更新後はPDFへ再変換し、全ページを目視確認する。

## 11. 最終ZIP

```zsh
./submission/make_submission.sh \
  ./submission/evidence/jenkins実行動画_HW25A064.mp4 \
  ./submission/evidence/jenkins_console_HW25A064.txt
```

ZIPを一時フォルダへ展開し、動画再生、ログ、4成果物、レポート、ソース、秘密情報混入を検査する。

## 完了報告

1. 最終ZIP絶対パス
2. GitHubリポジトリURL
3. Jenkins成功ビルド番号
4. Webhook HTTP結果
5. テスト件数と結果
6. 動画の保存先と再生確認
7. ログ保存先
8. 秘密情報検査結果
9. 残課題
