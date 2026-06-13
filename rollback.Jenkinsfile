pipeline {
    agent any

    stages {
        stage('Switch Traffic to Stable (Green)') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config

                    # Patch service to green
                    kubectl patch service sentiment-api-service \
                        -p '{"spec":{"selector":{"app":"sentiment-api","slot":"green"}}}'

                    echo "Traffic switched to stable green slot"
                    kubectl get service sentiment-api-service -o jsonpath='{.spec.selector}'

                    # Kill old port-forward
                    sudo pkill -f "kubectl port-forward" || true
                    sleep 3

                    # Start fresh port-forward in background
                    nohup kubectl port-forward \
                        --address 0.0.0.0 \
                        svc/sentiment-api-service \
                        32500:5000 \
                        > /tmp/portforward.log 2>&1 &

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
        failure {
            echo "Rollback failed — check kubectl access"
        }
    }
}
