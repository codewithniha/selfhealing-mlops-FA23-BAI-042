pipeline {
    agent any

    stages {
        stage('Switch Traffic to Stable (Green)') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    # Scale green back up first
                    kubectl scale deployment sentiment-green-deployment --replicas=2
                    sleep 10

                    # Wait for green pods ready
                    kubectl rollout status deployment/sentiment-green-deployment --timeout=60s

                    # Patch service to green
                    kubectl patch service sentiment-api-service \
                        -p '{"spec":{"selector":{"app":"sentiment-api","slot":"green"}}}'

                    echo "Traffic switched to stable green slot"
                    kubectl get service sentiment-api-service \
                        -o jsonpath='{.spec.selector}'

                    # Restart port-forward
                    sudo /home/ubuntu/portforward-manager.sh
                    sleep 5
                    echo "Port-forward restarted"
                '''
            }
        }
    }

    post {
        success {
            echo "Self-healing complete — stable-v0-8639 is now serving traffic"
        }
    }
}
