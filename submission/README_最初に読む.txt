スクリプトプログラミング演習2 最終課題
学籍番号: HW25A064
氏名: 實光駿斗
テーマ: Japan Earthquake Monitor

このフォルダは、Mac上でGitHub・ngrok・Jenkinsの実動作証跡を作り、最終提出ZIPを生成するためのものです。

1. ルートで `./run_local.sh --offline` を実行し、テストと出力を確認する。
2. GitHubに本人用リポジトリを作成してpushする。
3. Jenkins Pipelineジョブを作成し、Jenkinsfileを指定する。
4. ngrokで localhost:8080 を公開する。
5. GitHub WebhookのURLを `https://<ngrok-domain>/github-webhook/` にする。
6. READMEを1行変更してpushし、Jenkinsが自動起動することを確認する。
7. 3アプリ連携が分かる動画を撮影する。
8. 成功ビルドのコンソールログを保存する。
9. `./submission/make_submission.sh <動画> <ログ>` を実行する。

ログイン情報、トークン、Webhook URLをソースや動画へ残さないでください。
