pipeline {
    agent any

    environment {
        DOCKERHUB_USER   = 'niha1020'
        IMAGE_UNSTABLE   = "${DOCKERHUB_USER}/sentiment-api:unstable"
        IMAGE_STABLE     = "${DOCKERHUB_USER}/sentiment-api:stable"
        TEST_CONTAINER   = 'sentiment-test-container'
        APP_PORT         = '5000'
        // Public EC2 IP used by the UI test to hit the live NodePort service
        EC2_PUBLIC_IP    = '32.198.95.64'
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh "docker build -t ${IMAGE_UNSTABLE} ."
                sh "docker rm -f ${TEST_CONTAINER} || true"
                sh """
                    docker run -d --name ${TEST_CONTAINER} \
                        -p ${APP_PORT}:5000 \
                        -v /tmp/app-logs:/app/logs \
                        ${IMAGE_UNSTABLE}
                """
                echo 'Waiting for DistilBERT to load...'
                sh 'sleep 60'
                sh "curl -s http://localhost:${APP_PORT}/health"
                echo 'App is ready!'
            }
        }

        stage('Unit Test') {
            steps {
                sh """
                    docker run --rm --network host \
                        -e BASE_URL=http://localhost:${APP_PORT} \
                        -v ${WORKSPACE}/tests:/tests \
                        ${IMAGE_UNSTABLE} \
                        sh -c "pip3 install pytest requests -q && pytest /tests/test_api.py -v"
                """
            }
        }

        stage('UI Test') {
            steps {
                // Uses a prebuilt image with chromium + chromium-driver + selenium
                // already installed, so we don't apt-get 300 packages every build.
                // Build/push this once: docker build -f Dockerfile.selenium-test
                //   -t <dockerhub-user>/selenium-test-runner:latest .
                sh """
                    docker run --rm \
                        -e BASE_URL=http://${EC2_PUBLIC_IP}:32500 \
                        -v ${WORKSPACE}/tests:/tests \
                        ${DOCKERHUB_USER}/selenium-test-runner:latest \
                        pytest /tests/test_ui.py -v
                """
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"

                    // Unstable / blue image — already built above
                    sh "docker push ${IMAGE_UNSTABLE}"

                    // Stable / green image — build from the stable-fallback branch
                    sh "rm -rf stable-fallback-src"
                    sh """
                        git clone --branch stable-fallback --single-branch \
                            \$(git config --get remote.origin.url) stable-fallback-src
                    """
                    sh "docker build -t ${IMAGE_STABLE} stable-fallback-src"
                    sh "docker push ${IMAGE_STABLE}"

                    sh 'docker logout'
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh 'kubectl apply -f k8s/pvc.yaml'
                sh 'kubectl apply -f k8s/blue-deployment.yaml'
                sh 'kubectl apply -f k8s/green-deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
                sh 'kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s'
                sh 'kubectl rollout status deployment/sentiment-green-deployment --timeout=120s'
            }
        }
    }

    post {
        always {
            sh "docker rm -f ${TEST_CONTAINER} || true"
        }
    }
}
