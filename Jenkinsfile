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
        stage('Build Container Image') {
            steps {
                script {
                    echo '>>> Building Docker Image...'
                    sh "docker build -t $APP_NAME ."
                }
            }
        }

        stage('Test') {
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

        stage('Push to ECR') {
            steps {
                script {
                    echo '>>> Login to ECR...'
                    sh "aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY"

                    def shortCommit = env.GIT_COMMIT.take(7)
                    def uniqueTag = "$ECR_REGISTRY/$APP_NAME:build-${env.BUILD_NUMBER}-${shortCommit}"
                    def latestTag = "$ECR_REGISTRY/$APP_NAME:latest"

                    echo ">>> Tagging and Pushing: $uniqueTag"
                    sh "docker tag $APP_NAME $uniqueTag"
                    sh "docker tag $APP_NAME $latestTag"
                    
                    sh "docker push $uniqueTag"
                    sh "docker push $latestTag"
                }
            }
        }

        stage('Deploy and Verify') {
            when { branch 'master' } 
            steps {
                sshagent(['prod-ssh-key']) { 
                    script {
                        echo ">>> Deploying to Production..."
                        
                        def remoteCmd = """
                            set -e
                           
                            echo "--- Pulling and Restarting ---"
                            aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
                            docker pull $ECR_REGISTRY/$APP_NAME:latest
                            docker stop calc-app || true
                            docker rm calc-app || true
                            docker run -d -p 5000:5000 --name calc-app $ECR_REGISTRY/$APP_NAME:latest

                            echo "--- Starting Health Check ---"
                            for i in 1 2 3 4 5 6; do
                                echo "Attempt \$i: Checking health..."
                                if curl -f http://localhost:5000/health; then
                                    echo " >> Health Check PASSED!"
                                    exit 0
                                fi
                                echo " >> Not ready yet, waiting 5s..."
                                sleep 5
                            done
                            
                            echo " >> Health Check FAILED after timeout!"
                            exit 1
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
