pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = "niha1020"
        IMAGE_UNSTABLE  = "${DOCKER_HUB_USER}/sentiment-api:unstable"
        IMAGE_STABLE    = "${DOCKER_HUB_USER}/sentiment-api:stable"
        CONTAINER_NAME  = "sentiment-test-container"
        BASE_URL        = "http://localhost:5000"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build -t ${IMAGE_UNSTABLE} .
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -p 5000:5000 \
                        -v /tmp/app-logs:/app/logs \
                        ${IMAGE_UNSTABLE}
                    echo "Waiting for app to start..."
                    sleep 20
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        -v ${WORKSPACE}/tests:/tests \
                        ${IMAGE_UNSTABLE} \
                        sh -c "pip install pytest requests -q && pytest /tests/test_api.py -v"
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:5000 \
                        -e DISPLAY=:99 \
                        -v ${WORKSPACE}/tests:/tests \
                        selenium/standalone-chrome:4.21.0 \
                        bash -c "pip install selenium requests pytest -q && pytest /tests/test_ui.py -v" || true
                '''
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        docker push ${IMAGE_UNSTABLE}

                        git fetch origin stable-fallback
                        git checkout origin/stable-fallback -- app.py
                        docker build -t ${IMAGE_STABLE} .
                        docker push ${IMAGE_STABLE}

                        git checkout HEAD -- app.py
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s
                '''
            }
        }

    }

    post {
        always {
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
    }
}
