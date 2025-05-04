pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'feature/hjh', url: 'https://github.com/INU-SoftwareDesign/Back-end.git'
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
    }
}
