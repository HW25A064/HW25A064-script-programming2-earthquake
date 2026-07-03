pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '15'))
    }

    environment {
        PYTHONUNBUFFERED = '1'
        LANG = 'ja_JP.UTF-8'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Tool versions') {
            steps {
                sh 'python3 --version'
                sh 'node --version'
                sh 'git --version'
            }
        }
        stage('Unit tests') {
            steps {
                sh 'python3 -m unittest discover -s tests -v'
            }
        }
        stage('Earthquake data output') {
            steps {
                sh 'rm -rf output && mkdir -p output'
                sh 'python3 src/earthquake_fetcher.py --days 7 --min-magnitude 2.5 --allow-fallback'
            }
        }
        stage('JavaScript dashboard extension') {
            steps {
                sh 'node src/build_dashboard.mjs output/earthquakes.json output/index.html'
            }
        }
        stage('Verify outputs') {
            steps {
                sh 'python3 src/verify_outputs.py'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'output/earthquakes.json,output/earthquakes.csv,output/index.html,output/build_summary.json', fingerprint: true, onlyIfSuccessful: false
        }
        success {
            sh 'python3 src/notify_discord.py SUCCESS || true'
        }
        failure {
            sh 'python3 src/notify_discord.py FAILURE || true'
        }
    }
}
