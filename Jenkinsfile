pipeline {
  agent any

    environment {
    WEBSCRAPER = "false"
    VECTORISER = "false"
    WEBSCRAPER_RUNNING = "false"
    VERSION = ""
  }

  stages {
    stage('Docker Debug') {
      steps {
        sh '''
          whoami
          id
          groups
          ls -l /var/run/docker.sock
          docker ps
        '''
      }
    }

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Init Version') {
      steps {
        script {
          env.VERSION = sh(
            script: "git rev-parse --short HEAD",
            returnStdout: true
          ).trim()
        }
      }
    }

    stage('Bootstrap Webscraper') {
      steps {
        script {
          def exists = sh(
            script: "docker ps -a --filter name=webscraper --format '{{.Names}}'",
            returnStdout: true
          ).trim()

          if (!exists) {
            echo "Webscraper not found — bootstrapping"

            sh '''
              docker build -t webscraper:latest webscrape/
              docker run -d --name webscraper webscraper:latest
            '''

            echo "Bootstrap complete — stopping pipeline"
            currentBuild.result = 'SUCCESS'
            return
          }

          echo "Webscraper exists — continuing pipeline"
        }
      }
    }

    stage('Detect Changes') {
      steps {
        script {
          def filesChanged = sh(
            script: '''
              if [ -n "$CHANGE_ID" ]; then
                git diff --name-only origin/main...HEAD
              else
                git diff --name-only HEAD~1 HEAD
              fi
            ''',
            returnStdout: true
          ).trim()

          echo "Changed files:\n${filesChanged}"

          if (filesChanged.contains("webscrape/")) {
            env.WEBSCRAPER = "true"
            echo "Pending update to webscraper"
          }

          if (filesChanged.contains("embedding_handling/")) {
            env.VECTORISER = "true"
            echo "Pending update to vectoriser"
          }
        }
      }
    }

    stage('Detect Runtime State') {
      steps {
        script {
          def running = sh(
            script: "docker ps --filter name=webscraper --format '{{.Names}}'",
            returnStdout: true
          ).trim()

          env.WEBSCRAPER_RUNNING = running.contains("webscraper") ? "true" : "false"
        }
      }
    }

    stage('Build Scraper') {
      when {
        allOf {
          branch 'main'
          anyOf {
            expression { env.WEBSCRAPER == "true" }
            expression { env.WEBSCRAPER_RUNNING == "false" }
          }
        }
      }
      steps {
        sh "docker build -t webscraper:${env.VERSION} webscrape/"
      }
    }

    stage('Run Scraper Container') {
      when {
        allOf {
          branch 'main'
          anyOf {
            expression { env.WEBSCRAPER == "true" }
            expression { env.WEBSCRAPER_RUNNING == "false" }
          }
        }
      }
      steps {
        sh '''
          docker stop webscraper || true
          docker rm webscraper || true
          docker run -d --name webscraper webscraper:${VERSION}
        '''
      }
    }
  }
}
