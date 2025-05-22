pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'mario322/django-backend'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.CURRENT_BRANCH = 'main'
                    env.TAG = "prod-${env.BUILD_NUMBER}"
                    env.PORT = '5000'
                    echo "✅ 운영 브랜치: main"
                    echo "📦 이미지 태그: ${env.TAG}"
                }
            }
        }

                stage('Prepare Environment') {
            steps {
                // Secret File Credential로부터 .env 파일을 받아서 워크스페이스에 복사
                withCredentials([file(credentialsId: 'backend-env-prod', variable: 'ENV_FILE')]) {
                    sh 'cp $ENV_FILE .env'
                    sh 'ls -l .env'
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub-token', variable: 'DOCKER_TOKEN')]) {
                    sh '''
                        docker build -t $DOCKER_IMAGE:$TAG .
                        echo "$DOCKER_TOKEN" | docker login -u mario322 --password-stdin
                        docker push $DOCKER_IMAGE:$TAG
                    '''
                }
            }
        }

        stage('Update GitOps') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'github-cred', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh '''
                        git config --global user.name "Jenkins"
                        git config --global user.email "jenkins@example.com"

                        git clone https://$GIT_USER:$GIT_TOKEN@github.com/platypus322/DevOps.git
                        cd DevOps/helm/backend/prod

                        sed -i "s/tag:.*/tag: $TAG/" values.yaml

                        git add values.yaml
                        git commit -m "🔄 Update backend-prod image tag to $TAG"
                        git push origin main
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker container prune -f'
            sh 'docker rmi $DOCKER_IMAGE:$TAG || true'
            cleanWs()
        }
    }
}
