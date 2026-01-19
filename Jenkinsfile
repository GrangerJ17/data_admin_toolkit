pipeline {
    agent any

    environment {
        WEBSCRAPER = "false"
        VECTORISER = "false"
        WEBSCRAPER_RUNNING = "false"
        VERSION = ""
    }

    stages {

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

       

        stage('Test') {
            steps {
                 sh """
                  python3 -m venv components/scraper/venv
                  . components/scraper/venv/bin/activate
                  pip install -r components/scraper/requirements.txt
                  ls components/scraper/scraper_tests/
                  python components/scraper/scraper_tests/test_listings.py
                  """
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

        stage('Schedule Scraper') {
            when {
                allOf {
                    branch 'main'
                    expression { env.WEBSCRAPER == "true" }
                }
            }
            steps {
                script {
                    sh '''
                    VERSION=$(date +%Y%m%d%H%M%S)

                    echo New version created: $VERSION

                    mkdir -p /home/james/scripts/scraper/versions/$VERSION

                    echo New directory made: /home/james/scripts/scraper/versions/$VERSION 

                    cp -r components/scraper/* /home/james/scripts/scraper/versions/$VERSION/ 

                    echo Copied contents of repo to new directory

                    # Stop previous run if running
                    pkill -f /home/james/scripts/scraper/current/src/seed_database.py || true

                    # Atomically update 'current' symlink
                    ln -sfn /home/james/scripts/scraper/versions/$VERSION /home/james/scripts/scraper/current

                    echo New link created
                    '''
                }
            }
        }

    } // end stages
} // end pipeline
