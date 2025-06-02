pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'mario322/django-backend-test'
        SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/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'
    }

    stages {
        stage('Slack Notify Start') {
            steps {
                sh """
                curl -X POST -H 'Content-type: application/json' \
                --data '{"text":"🚀 [Jenkins] Backend-dev 빌드 시작: #${BUILD_NUMBER}"}' \
                ${SLACK_WEBHOOK_URL}
                """
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.CURRENT_BRANCH = 'develop'
                    env.TAG = "dev-${env.BUILD_NUMBER}"
                    echo "✅ 테스트 브랜치: develop"
                    echo "📦 이미지 태그: ${env.TAG}"
                }
            }
        }

        // 개발환경 테스트나 필요시 환경변수 임시로 세팅 (이미지 빌드와는 무관)
        stage('Test (Optional)') {
            steps {
                withCredentials([
                    string(credentialsId: 'KAKAO_REST_API_KEY', variable: 'KAKAO_REST_API_KEY'),
                    string(credentialsId: 'GOOGLE_CLIENT_ID', variable: 'GOOGLE_CLIENT_ID'),
                    string(credentialsId: 'GOOGLE_CLIENT_SECRET', variable: 'GOOGLE_CLIENT_SECRET'),
                    string(credentialsId: 'NAVER_CLIENT_ID', variable: 'NAVER_CLIENT_ID'),
                    string(credentialsId: 'NAVER_CLIENT_SECRET', variable: 'NAVER_CLIENT_SECRET'),
                    string(credentialsId: 'NAVER_CALLBACK_TEST_URL', variable: 'NAVER_CALLBACK_URL'),
                    // string(credentialsId: 'SLACK_WEBHOOK_URL', variable: 'SLACK_WEBHOOK_URL')
                ]) {
                    sh '''
                    export KAKAO_REST_API_KEY=$KAKAO_REST_API_KEY
                    export GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
                    export GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
                    export NAVER_CLIENT_ID=$NAVER_CLIENT_ID
                    export NAVER_CLIENT_SECRET=$NAVER_CLIENT_SECRET
                    export NAVER_CALLBACK_URL=$NAVER_CALLBACK_URL
                    # export SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL
                    # 여기서 pytest 등 유닛테스트 필요시 실행
                    # pytest
                    '''
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
                        cd DevOps/helm/backend/dev

                        sed -i "s/tag:.*/tag: $TAG/" values.yaml

                        git add values.yaml
                        git commit -m "🔄 Update backend-dev image tag to $TAG"
                        git push origin main
                    '''
                }
            }
        }
    }

    post {
        success {
            sh """
            curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"✅ [Jenkins] Backend-dev 빌드 성공: #${BUILD_NUMBER}"}' \
            ${SLACK_WEBHOOK_URL}
            """
        }
        failure {
            sh """
            curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"❌ [Jenkins] Backend-dev 빌드 실패: #${BUILD_NUMBER}"}' \
            ${SLACK_WEBHOOK_URL}
            """
        }
        always {
            sh 'docker container prune -f'
            sh 'docker rmi $DOCKER_IMAGE:$TAG || true'
            cleanWs()
        }
    }
}
