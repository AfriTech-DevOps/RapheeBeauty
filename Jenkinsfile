pipeline {
    agent any

    environment {
        SCANNER_HOME = tool 'sonar-scanner'
        DOCKERHUB_CREDENTIALS = credentials('d4506f04-b98c-47db-95ce-018ceac27ba6')
        BRANCH_NAME = "${GIT_BRANCH.split("/")[1]}"
        SLACK_WEBHOOK = credentials('11563aa0-e08f-4a9b-baa2-ac70c795ada9')
    }

    parameters {
        choice(name: 'DEPLOYMENT', choices: ['DockerContainer', 'Kubernetes'], description: 'Select deployment type')
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Git Checkout') {
            steps {
                checkout scmGit(branches: [[name: '*/dev'], [name: '*/qa'], [name: '*/prod']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/AfriTech-DevOps/RapheeBeauty.git']])
            }
        }

        stage('Sonarqube Analysis') {
            steps {
                script {
                    withSonarQubeEnv('sonar-server') {
                        sh "$SCANNER_HOME/bin/sonar-scanner -Dsonar.projectKey=rapheeBeauty -Dsonar.projectName=rapheeBeauty"
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    withSonarQubeEnv('sonar-server') {
                        waitForQualityGate abortPipeline: false, credentialsId: 'sonar-token'
                    }
                }
            }
        }

        stage('Trivy File Scan') {
            steps {
                sh "trivy fs . > trivy-${env.BRANCH_NAME}-raphee-beauty-result.txt"
            }
        }

        stage("Docker Login") {
            steps {
                sh "echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin"
                echo "Login Succeeded"
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    def imageTag = determineTargetEnvironment()
                    if (imageTag == 'prod') {
                        sh "sed -i 's/CMD \\[\"python\", \"app.py\"\\]/CMD \\[\"waitress-serve\", \"--listen=*:5000\", \"app:app\"\\]/' Dockerfile"
                        sh "docker build -t idrisniyi94/raphee-beauty:${imageTag}-${env.BUILD_ID} ."
                    }
                    else {
                        sh "docker build -t idrisniyi94/raphee-beauty:${imageTag}-${env.BUILD_ID} ."
                    }
                }
            }
        }

        stage('Trivy Image Scan') {
            steps {
                script {
                    def imageTag = determineTargetEnvironment()
                    sh "trivy image idrisniyi94/raphee-beauty:${imageTag}-${env.BUILD_ID} > raphee-beauty-${imageTag}-trivy-result.txt"
                }
            }
        }

        stage('Docker Push') {
            steps {
                script {
                    def imageTag = determineTargetEnvironment()
                    sh "docker push idrisniyi94/raphee-beauty:${imageTag}-${env.BUILD_ID}"
                }
            }
        }

        stage('Deployment') {
    steps {
        script {
            if (params.DEPLOYMENT == 'DockerContainer') {
                def containerName = "raphee-beauty-${env.BRANCH_NAME}"
                def isRunning = sh(script: "docker ps -a | grep ${containerName}", returnStatus: true)
                if (isRunning == 0) {
                    sh "docker rm -f ${containerName}"
                }
                if (env.BRANCH_NAME == 'prod') { 
                    sh "sed -i 's/CMD \\[\"python\", \"app.py\"\\]/CMD \\[\"waitress-serve\", \"--listen=*:5000\", \"app:app\"\\]/' Dockerfile"
                    sh "docker run -d -p 5530:5000 --name ${containerName} idrisniyi94/raphee-beauty:${env.BRANCH_NAME}-${env.BUILD_ID}"
                }
                else {
                    sh "docker run -d -p 5530:5000 --name ${containerName} idrisniyi94/raphee-beauty:${env.BRANCH_NAME}-${env.BUILD_ID}"
                }
            } else {
                dir('./k8s') {
                    kubeconfig(credentialsId: '500a0599-809f-4de0-a060-0fdbb6583332', serverUrl: '') {
                        def targetEnvironment = determineTargetEnvironment()
                        def deploymentName = "${targetEnvironment}-raphee-beauty-deployment"

                        // Check if the deployment exists
                        def deploymentExists = sh(script: "kubectl get deployment ${deploymentName}", returnStatus: true)

                        if (deploymentExists == 0) {
                            // Deployment exists, proceed with deletion and re-apply
                            sh "kubectl delete -f ${targetEnvironment}-deployment.yaml"
                            sh "sed -i 's/raphee-beauty:.*/raphee-beauty:${targetEnvironment}-${env.BUILD_ID}/' ${targetEnvironment}-deployment.yaml"
                            sh "kubectl apply -f ${targetEnvironment}-deployment.yaml"
                            sh "kubectl apply -f ${targetEnvironment}-service.yaml"
                        } else {
                            echo "Deployment does not exist. Skipping deletion and re-apply."
                        }
                    }
                }

            }
        }
    }
}

    }
    post {
        success {
           
            slackSend channel: '#alerts', color: 'good', message: "${currentBuild.currentResult}: \nJOB_NAME: ${env.JOB_NAME} \nBUILD_NUMBER: ${env.BUILD_NUMBER} \nBRANCH_NAME: ${env.BRANCH_NAME}. \n More Info ${env.BUILD_URL}"
        }
        failure {

            slackSend channel: '#alerts', color: 'danger', message: "${currentBuild.currentResult}: \nJOB_NAME: ${env.JOB_NAME} \nBUILD_NUMBER: ${env.BUILD_NUMBER} \nBRANCH_NAME: ${env.BRANCH_NAME}. \n More Info ${env.BUILD_URL}"
        }
    }      
}

def determineTargetEnvironment() {
    def branchName = env.BRANCH_NAME
    if (branchName == 'qa') {
        return 'qa'
    } else if (branchName == 'prod') {
        return 'prod'
    } else {
        return 'dev'
    }
}