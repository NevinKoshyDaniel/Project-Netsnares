pipeline {
    agent any

    environment {
        APP_VERSION = "1.0.${BUILD_NUMBER}-temp"
        GIT_COMMIT_HASH = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
        IMAGE_NAME = "netsnares-analyzer"
        REGISTRY = "local-registry" 
    }

    stages {
        stage('1. Build') {
            steps {
                echo "Building Docker Images for Netsnares..."
                sh "docker build -t ${IMAGE_NAME}:${APP_VERSION} -t ${IMAGE_NAME}:latest -f traffic_generator/Dockerfile ./traffic_generator"
            }
        }

        stage('2. Test') {
            steps {
                echo "Running Automated Unit Tests..."
                sh """
                docker run --rm ${IMAGE_NAME}:${APP_VERSION} sh -c "pip install pytest && pytest tests/ --junitxml=test-results.xml"
                """
            }
            post {
                always {
                    junit 'test-results.xml' 
                }
            }
        }

        stage('3. Code Quality') {
            environment {
                scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh "${scannerHome}/bin/sonar-scanner"
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 1, unit: 'HOURS') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('4. Security') {
            steps {
                echo "Scanning Docker image for vulnerabilities using Trivy..."
                sh "trivy image --format table --exit-code 0 ${IMAGE_NAME}:${APP_VERSION} > vuln-report.txt"
                sh "trivy image --severity CRITICAL --exit-code 1 ${IMAGE_NAME}:${APP_VERSION}"
            }
            post {
                always {
                    archiveArtifacts artifacts: 'vuln-report.txt'
                }
            }
        }

        stage('5. Deploy (Staging)') {
            environment {
                ENV_CONTEXT = "staging"
            }
            steps {
                echo "Deploying to Staging Environment..."
                sh "docker-compose -f docker-compose.yml up -d"
            }
            post {
                failure {
                    echo "Deployment failed! Rolling back..."
                    sh "docker-compose down"
                }
            }
        }

        stage('6. Release (Production)') {
            environment {
                ENV_CONTEXT = "production"
                LOG_LEVEL = "INFO" 
            }
            steps {
                echo "Promoting Version ${APP_VERSION} to Production..."
                sh "docker tag ${IMAGE_NAME}:${APP_VERSION} ${IMAGE_NAME}:stable"
                echo "Release fully versioned and tagged as stable."
            }
        }

        stage('7. Monitoring') {
            steps {
                echo "Verifying Monitoring Stack..."
                sh "docker ps | grep grafana"
                sh "docker ps | grep loki"
                echo "Monitoring stack is active. Awaiting traffic simulation."
            }
        }
    }
}