pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = 'dockerhub-auth' // ID of your credentials in Jenkins
        IMAGE_NAME = "your-dockerhub-username/medtracker"
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-username/medtracker.git'
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

        stage('Deploy (Optional)') {
            steps {
                echo 'Deploying to EC2...'
                // Restarts the container with the new image
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
