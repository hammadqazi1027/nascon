pipeline {
  agent any
  environment {
    HUB = 'hammadqazi1027'
    KUBECONFIG = '/etc/rancher/k3s/k3s.yaml'
  }
  stages {
    stage('Build images') {
      steps {
        sh 'docker build -t $HUB/nascon-backend:$BUILD_NUMBER ./backend'
        sh 'docker build -t $HUB/nascon-frontend:$BUILD_NUMBER ./frontend'
      }
    }
    stage('Push images') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'U', passwordVariable: 'P')]) {
          sh 'echo $P | docker login -u $U --password-stdin'
          sh 'docker push $HUB/nascon-backend:$BUILD_NUMBER'
          sh 'docker push $HUB/nascon-frontend:$BUILD_NUMBER'
        }
      }
    }
    stage('Deploy to Kubernetes') {
      steps {
        sh 'sed -e "s/DOCKERHUB_USER/$HUB/g" -e "s/IMAGE_TAG/$BUILD_NUMBER/g" k8s/nascon.yaml | kubectl apply -f -'
        sh 'kubectl rollout status deployment/backend --timeout=180s'
        sh 'kubectl rollout status deployment/frontend --timeout=180s'
      }
    }
  }
}
