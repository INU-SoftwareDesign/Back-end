pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'feature/hjh', url: 'https://github.com/INU-SoftwareDesign/Back-end.git'
            }
        }

        stage('Inject .env') {
            steps {
                // EC2에 고정 저장된 .env.backend 파일을 Jenkins 작업 디렉토리로 복사
                sh 'cp /home/ubuntu/.env.backend .env'
            }
        }
        
        stage('Docker Cleanup') {
            steps {
                // 이전 컨테이너, 이미지 제거
                sh 'docker stop django-container || true'
                sh 'docker rm django-container || true'
                sh 'docker rmi django-backend || true'
            }
        }

        stage('Docker Build') {
            steps {
                // --no-cache 옵션 추가 (필요시)
                sh 'docker build --no-cache -t django-backend .'
            }
        }

        stage('Docker Run') {
            steps {
                sh 'docker run -d -p 5000:5000 --name django-container django-backend'
            }
        }

        stage('Collect Static Files') {
            steps {
                sh 'sleep 5'  // 컨테이너 부팅 대기
                sh 'docker exec django-container python manage.py collectstatic --noinput'
            }
        }
    }
}

// Webhook test http://52.73.19.160:8080/github-webhook/