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
                script {
                    try {
                        sh "docker run -d --name test-runner --entrypoint tail ${IMAGE_NAME}:${APP_VERSION} -f /dev/null"
                        sh "docker cp tests/ test-runner:/tests/"
                        sh "docker cp analyzer.py test-runner:/tests/analyzer.py"
                        // FIX 1: Save the XML to the universally writable /tmp/ directory
                        sh "docker exec test-runner sh -c 'pip install pytest pandas && python -m pytest /tests/ -p no:cacheprovider --junitxml=/tmp/test-results.xml'"
                        
                    } finally {
                        // FIX 2: Copy the file out of the /tmp/ directory to your Jenkins workspace
                        sh "docker cp test-runner:/tmp/test-results.xml ./test-results.xml || true"
                        sh "docker rm -f test-runner || true"
                    }
                }
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

        stage('4. Security (SBOM)') {
            steps {
                echo "Generating CycloneDX SBOM using Syft..."
                sh "docker run --rm -v /var/run/docker.sock:/var/run/docker.sock anchore/syft ${IMAGE_NAME}:${APP_VERSION} -o cyclonedx-json > sbom.json"
            }
            post {
                always {
                    archiveArtifacts artifacts: 'sbom.json'
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