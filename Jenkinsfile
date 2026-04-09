pipeline {
    // Allows Jenkins to run this on any available agent
    agent any
    
    environment {
        // --- CONFIGURATION ---
        DOCKER_CREDENTIALS_ID = 'suraj960' // The ID of your credentials in Jenkins
        DOCKER_IMAGE          = 'suraj960/medtracker'
        AWS_REGION            = 'ap-south-1'      
        EKS_CLUSTER_NAME      = 'medtracker-cluster'
    }
    
    stages {
        stage('Pull Latest Code') {
            steps {
                // Jenkins automatically pulls code from the defined SCM before this,
                // but we explicitly state it for pipeline visibility.
                checkout scm
                echo "Code pulled successfully."
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building MedTracker Docker image..."
                    // We tag with both the specific Jenkins Build Number AND 'latest'
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }
        
        stage('Push to Docker Hub') {
            steps {
                // Securely injects Docker Hub credentials without exposing them in logs
                withCredentials([usernamePassword(credentialsId: "${DOCKER_CREDENTIALS_ID}", passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh "echo \$DOCKER_PASSWORD | docker login -u \$DOCKER_USERNAME --password-stdin"
                    
                    echo "Pushing images to Docker Hub..."
                    sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Deploy to EKS') {
            steps {
                script {
                    echo "Authenticating to EKS via IAM Role..."
                    // This command uses the IAM Role attached to the Jenkins EC2 instance 
                    // to securely generate the kubeconfig file required by kubectl.
                    sh "aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER_NAME}"
                    
                    echo "Injecting new image tag into Kubernetes manifests..."
                    // This dynamically updates your deployment file to use the exact build we just created
                    sh "sed -i 's|${DOCKER_IMAGE}:.*|${DOCKER_IMAGE}:${BUILD_NUMBER}|g' k8s/deployment.yaml"
                    
                    echo "Applying changes to the live cluster..."
                    sh "kubectl apply -f k8s/"
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline complete. Cleaning up local Docker images to prevent disk exhaustion..."
            // Removes the images from the Jenkins server to keep the environment clean
            sh "docker rmi ${DOCKER_IMAGE}:${BUILD_NUMBER} || true"
            sh "docker rmi ${DOCKER_IMAGE}:latest || true"
            sh "docker logout"
        }
        success {
            echo "✅ MedTracker deployment was successful!"
        }
        failure {
            echo "❌ Pipeline failed. Please check the Jenkins logs."
        }
    }
}
