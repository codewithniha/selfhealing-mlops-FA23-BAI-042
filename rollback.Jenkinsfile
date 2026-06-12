pipeline {
    agent any

    stages {

        stage('Switch Traffic to Stable (Green)') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl patch service sentiment-api-service \
                        -p '{"spec":{"selector":{"app":"sentiment-api","slot":"green"}}}'
                    echo "Traffic switched to stable green slot"
                    kubectl get service sentiment-api-service -o jsonpath='{.spec.selector}'
                '''
            }
        }

    }

    post {
        success {
            echo "Self-healing complete — stable-v0-8639 is now serving traffic"
        }
        failure {
            echo "Rollback failed — check kubectl access"
        }
    }
}
