pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '992382545251.dkr.ecr.us-east-1.amazonaws.com/ofekpenso' 
        APP_NAME = 'calculator-app'
    }

    stages {
        stage('Build Image') {
            steps {
                script {
                    echo '>>> Building Docker Image...'
                    sh "docker build -t $APP_NAME ."
                }
            }
        }
       
        stage('Run Tests') {
            agent {
                docker { image 'python:3.9-slim' }
            }
            steps {
                script {
                    echo '>>> Running Unit Tests...'
                    sh 'pip install --no-cache-dir -r requirements.txt'
                    sh 'pytest --junitxml=test-reports/results.xml'
                }
            }
        }

        stage('Push PR Image') {
            steps {
                script {
                    echo '>>> Login to ECR...'
                    sh "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY"
                    
               
                    def prTag = "$ECR_REGISTRY/$APP_NAME:pr-${env.BUILD_NUMBER}"
                    
                    echo ">>> Tagging and Pushing: $prTag"
                    sh "docker tag $APP_NAME $prTag"
                    sh "docker push $prTag"
                }
            }
        }
    }
    
    post {
        always {
            sh "docker rmi $APP_NAME || true"
        }
    }
}
