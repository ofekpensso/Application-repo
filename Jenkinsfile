pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        ECR_REGISTRY = '992382545251.dkr.ecr.us-east-1.amazonaws.com' 
        APP_NAME = 'ofekpenso'
        PROD_IP = '3.92.213.59'
        PROD_USER = 'ubuntu'
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
                     
                    sh 'pip install pytest'

                    sh 'export PYTHONPATH=. && pytest --junitxml=test-reports/results.xml'

                    
                }
            }
        }

        stage('Push PR Image') {
            steps {
                script {
                    echo '>>> Login to ECR...'
                    sh "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY"
                    
               
                    def prTag = "$ECR_REGISTRY/$APP_NAME:pr-${env.BUILD_NUMBER}"
                    def latestTag = "$ECR_REGISTRY/$APP_NAME:latest"

                    echo ">>> Tagging and Pushing: $prTag"
                    sh "docker tag $APP_NAME $prTag"
                    sh "docker push $prTag"
                }
            }
        }
        
        stage('Deploy to Production') {
            when { branch 'master' } 
            steps {
                sshagent(['prod-ssh-key']) { 
                    script {
                        echo ">>> Deploying to Production..."
                        def remoteCmd = """
                            aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
                            docker pull $ECR_REGISTRY/$APP_NAME:latest
                            docker stop calc-app || true
                            docker rm calc-app || true
                            docker run -d -p 5000:5000 --name calc-app $ECR_REGISTRY/$APP_NAME:latest
                        """
                        sh "ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_IP '$remoteCmd'"
                    }
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
