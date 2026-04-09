pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'suraj960' // ID of your credentials in Jenkins
        IMAGE_NAME = "suraj960/medtracker"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Sansuraj09/medtracker.git'
            }
        }

        stage('Lint & Static Check') {
            steps {
                echo 'Checking for syntax errors...'
                // Using a python container to lint the code
                sh 'docker run --rm python:3.9-slim pip install flake8 && flake8 .'
            }
        }

        stage('Unit Tests') {
            steps {
                echo 'Running Flask tests...'
                // Runs tests inside a temporary container
                sh 'docker build -t medtracker-test:latest .'
                sh 'docker run --rm medtracker-test:latest python -m pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Image: ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    docker.withRegistry('', DOCKERHUB_CREDENTIALS) {
                        sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                        sh "docker push ${IMAGE_NAME}:latest"
                    }
                }
            }
        }

        stage('Deploy (Docker Compose)') {
            steps {
                echo 'Deploying with Docker Compose...'
                // Pulls the latest image and restarts the container
                sh 'docker compose up -d --pull always'
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f' // Clean up dangling images
        }
    }
}
