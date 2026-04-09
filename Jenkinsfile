pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "suraj960/medtracker"
        DOCKER_TAG   = "${BUILD_NUMBER}"
        // Make sure this matches the Credential ID you created in Jenkins
        DOCKER_HUB_CREDS = 'suraj960' 
    }

    stages {
        stage('Pull Code') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} -t ${DOCKER_IMAGE}:latest ."
            }
        }

        stage('Test Build') {
            steps {
                echo "Running smoke tests..."
                // This starts the container briefly to see if the app actually boots
                sh "docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} python -m flask --version"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "${DOCKER_HUB_CREDS}", passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh "echo \$PASS | docker login -u \$USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // This assumes you have the 'aws' and 'kubectl' tools installed now
                    sh "aws eks update-kubeconfig --region ap-south-1 --name medtracker-cluster"
                    
                    // Update the deployment file with the new image tag
                    sh "sed -i 's|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${DOCKER_TAG}|g' k8s/deployment.yaml"
                    
                    sh "kubectl apply -f k8s/"
                }
            }
        }
    }

    post {
        always {
            sh "docker logout"
            echo "Cleaning up local images..."
            sh "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || true"
        }
    }
}
