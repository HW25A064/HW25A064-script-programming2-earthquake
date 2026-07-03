# GitHub・ngrok・Jenkins設定手順（macOS）

## 1. 必要ツール

```zsh
brew install python node git ngrok
brew install --cask temurin@17
brew install jenkins-lts
```

Jenkinsを開始:

```zsh
brew services start jenkins-lts
open http://localhost:8080
```

## 2. GitHub

本人アカウントで新規リポジトリ `HW25A064-script-programming2-earthquake` を作成し、このフォルダをpushする。

## 3. Jenkinsジョブ

- 種類: Pipeline
- ジョブ名: `HW25A064-earthquake-dashboard`
- Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: 本人のGitHubリポジトリ
- Branch: `*/main`
- Script Path: `Jenkinsfile`
- Build Triggers: `GitHub hook trigger for GITScm polling`

まず手動ビルドで `Finished: SUCCESS` まで確認する。

## 4. ngrok

```zsh
ngrok config add-authtoken <本人のトークン>
ngrok http 8080
```

固定ドメインがある場合:

```zsh
ngrok http --url=<固定ドメイン>.ngrok-free.app 8080
```

## 5. GitHub Webhook

GitHubの `Settings > Webhooks` で追加:

- Payload URL: `https://<ngrok公開URL>/github-webhook/`
- Content type: `application/json`
- Event: Just the push event
- Active: ON

Recent Deliveriesが成功し、ngrokに `POST /github-webhook/ 200 OK` が出ることを確認する。

## 6. Discord通知（任意の加点要素）

Discord Webhook URLをソースへ書かず、Jenkins CredentialsでSecret textとして登録する。Pipelineで環境変数 `DISCORD_WEBHOOK_URL` として利用できるようにする。
