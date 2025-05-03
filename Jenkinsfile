pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'feature/hjh', url: 'https://github.com/INU-SoftwareDesign/Back-end.git'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t django-backend .'
            }
        }

        stage('Docker Run') {
            steps {
                sh 'docker stop django-container || true'
                sh 'docker rm django-container || true'
                sh 'docker run -d -p 5000:5000 --name django-container django-backend'
            }
        }
    }
}
