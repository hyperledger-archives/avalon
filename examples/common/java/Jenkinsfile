pipeline {

    agent {
        label 'jenkins-agent-machine-1'
    }

    stages {

        stage('Test') {
            steps {
                 withCredentials([
                    string(credentialsId: 'ADDRESS_SONAR', variable: 'address_sonar'),
                    string(credentialsId: 'SONAR_WORKER_TOKEN', variable: 'worker_token')]){
                    sh './gradlew clean test sonarqube -Dsonar.projectKey=iexec-worker -Dsonar.host.url=$address_sonar -Dsonar.login=$worker_token --refresh-dependencies --no-daemon'
                 }
                 junit 'build/test-results/**/*.xml'
            }
        }

        stage('Build') {
            steps {
                sh './gradlew build --refresh-dependencies --no-daemon'
            }
        }

        stage('Upload Jars') {
            when {
                branch 'master'
            }
            steps {
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'nexus', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASSWORD']]) {
                    sh './gradlew -PnexusUser=$NEXUS_USER -PnexusPassword=$NEXUS_PASSWORD uploadArchives --no-daemon'
                }
            }
        }

        stage('Build/Upload Docker image') {
            when {
                branch 'master'
            }
            steps {
                withCredentials([[$class: 'UsernamePasswordMultiBinding', credentialsId: 'nexus', usernameVariable: 'NEXUS_USER', passwordVariable: 'NEXUS_PASSWORD']]) {
                    sh './gradlew -PnexusUser=$NEXUS_USER -PnexusPassword=$NEXUS_PASSWORD pushImage --no-daemon'
                }
            }
        }
    }

}
