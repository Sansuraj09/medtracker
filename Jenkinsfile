pipeline {
    // You can restrict this to a specific agent with Docker installed, e.g., agent { label 'docker-node' }
    agent any 
    
    environment {
        // Replace 'docker-hub-credentials-id' with the actual ID you set in Jenkins Credentials
        DOCKER_CREDS = credentials('docker-hub-credentials') 
        IMAGE_NAME = "suraj960/medtracker"
        IMAGE_TAG = "v${env.BUILD_NUMBER}" // Tags the image with the Jenkins build number for version control
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                // Automatically checks out the code from the repository configured in your Jenkins pipeline job
                checkout scm 
            }
        }

        stage('Test Code') {
            steps {
                echo 'Setting up environment and running tests...'
                sh '''
                    # Setting up a virtual environment for isolated testing
                    python3 -m venv myenv
                    source myenv/bin/activate
                    
                    # Install dependencies and run tests (adjust commands to your specific framework)
                    pip install -r requirements.txt
                    pytest tests/
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}..."
                // Builds the image using the Dockerfile in the root directory
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                
                // Also tag it as 'latest' for convenience
                sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
            }
        }

        stage('Push to Registry') {
            steps {
                echo 'Authenticating and pushing image to Docker Hub...'
                // Securely logging into Docker using the credentials bound in the environment block
                sh 'echo $DOCKER_CREDS_PSW | docker login -u $DOCKER_CREDS_USR --password-stdin'
                
                // Push both the versioned tag and the latest tag
                sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker push ${IMAGE_NAME}:latest"
            }
        }
    }

    // The post block executes actions based on the pipeline's outcome
    post {
        always {
            echo 'Cleaning up workspace and logging out...'
            // Clears the Jenkins workspace to save disk space and prevent state leakage between builds
            cleanWs() 
            sh 'docker logout'
        }
        success {
            echo 'Pipeline completed successfully! CI/CD automation executed.'
        }
        failure {
            echo 'Pipeline failed during execution. Please check the stage logs.'
        }
    }
}
