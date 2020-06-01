# Treinamento Alura - Jenkins e Docker: Pipeline de entrega continua
https://cursos.alura.com.br/course/pipeline-ci-jenkins-docker

## Tecnologias utilizadas
```
Jenkins
MySQL
Python
Docker
Dockerhub
Github
Slack
Sonarcube
npm -v                                  <- Utilizei a 6.14.4
node -v                                 <- Utilizei a 12.17.0
```

## Ubuntu 18.04, meu perfil não é python, apontei para um Projeto Node, MySQL
git@github.com:gustavocarvalhoti/heroku-node.git

## Instalar
```bash
cd scripts/
./get-docker.sh
./docker.sh                     <- Install docker e pull image
./jenkins.sh                    <- Install

### Install MySQL
docker run -p 3306:3306 --name db-mysql -e MYSQL_ROOT_PASSWORD=root -d mysql:latest 
mysql -uroot -proot -h127.0.0.1                                 <- Conectar
mysql -udevops -pmestre -h127.0.0.1
mysql -udevops_dev -pmestre -h127.0.0.1
CREATE USER 'devops'@'172.17.0.1' IDENTIFIED BY 'mestre';       <- Create user
GRANT ALL PRIVILEGES ON *.* TO 'devops'@'172.17.0.1';           <- Dar privilégio
CREATE USER 'devops_dev'@'172.17.0.1' IDENTIFIED BY 'mestre';   <- Create user
GRANT ALL PRIVILEGES ON *.* TO 'devops_dev'@'172.17.0.1';       <- Dar privilégio
SHOW GRANTS FOR 'devops_dev'@'172.17.0.1';                      <- Verificar se deu certo
DROP USER 'devops'@'172.17.0.1'                                 <- Drop
### All
create user 'devops'@'%' identified by 'mestre';
create user 'devops_dev'@'%' identified by 'mestre';
create database todo;
create database todo_dev;
create database test_todo_dev;
grant all privileges on *.* to devops@'%';
grant all privileges on *.* to devops_dev@'%';

### Descobrir IPv4Address do container mysql
docker network inspect bridge
"Name": "db-mysql",
"IPv4Address": "****",

#Alterando o mysqld.cnf
cd configs/mysqld.cnf 
vim /etc/mysql/my.cnf <- Preencher com as informações do arquivo acima

### Recarregar as permissões
sudo usermod -aG docker $USER
sudo usermod -aG docker jenkins

### Python - Processo manual
sudo pip3 install virtualenv nose coverage nosexcover pylint
cd /home/padtec/dev-tools/projects/alura-pipeline/project-todo-list
virtualenv  --always-copy  venv-django-todolist
source venv-django-todolist/bin/activate
sudo pip install -r requirements.txt
#### Fazendo a migracao inicial dos dados
python manage.py makemigrations
python manage.py migrate
#### Criando o superuser para acessar a app
python manage.py createsuperuser
user: alura - pass: mestre123
# Rodando a app
python manage.py runserver 0:8000
http://localhost:8000

### Sonarqube
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts
```

## Comandos
```bash
http://localhost:8080/                                          <- Jenkins
sudo cat /var/lib/jenkins/secrets/initialAdminPassword          <- Senha Jenkins, instalar os plugins default
user: adm
pass: mestre123
service jenkins stop                                            <- Stop Jenkins
service jenkins start                                           <- Start Jenkins

### Adicionando credenciais
Credentials -> 
Jenkins -> 
Global credentials (unrestricted) -> 
Add Credentials -> 
SSH Username with private key (Para o github) ->
ID: github-ssh
Description: github-ssh
Username: git (Sempre pq vai utilizar SSH)
cat ~/.ssh/id_rsa

### Novo job
Home -> Novo job -> jenkins-todo-list-principal -> Construir um projeto de software free-style
-> Gerenciamento de código fonte -> Git -> git@github.com:gustavocarvalhoti/heroku-node.git
Ambiente de build -> Delete workspace before build starts           <- Para evitar sujeira de código
Trigger de builds -> Consultar periodicamente o SCM -> * * * * *    <- Verifica a cada minuto, verificar crontab

### Permitir que o Jenkins controle o Docker - Expor o deamon do docker
sudo mkdir -p /etc/systemd/system/docker.service.d/
sudo vi /etc/systemd/system/docker.service.d/override.conf
    [Service]
    ExecStart=
    ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2376
sudo systemctl daemon-reload
sudo systemctl restart docker.service

### Instalando os plugins
Gerenciar Jenkins -> Gerenciar Plugins -> Disponíveis
# docker
Install without restart -> Depois reiniciar o jenkins
Gerenciar Jenkins -> Configurar o sistema -> Nuvem
# Name: docker
# URI: tcp://127.0.0.1:2376
# Enabled
# This project is parameterized: 
DOCKER_HOST
tcp://127.0.0.1:2376
# Voltar no job criado na aula anterior
# Manter a mesma configuracao do GIT para desenvolvimento
# Build step 1: Executar Shell
# Validando a sintaxe do Dockerfile
cd project-todo-list
docker run --rm -i hadolint/hadolint < Dockerfile <- Não utilizei no projeto Node
# Build step 2: Build/Publish Docker Image
Directory for Dockerfile: ./project-todo-list/
Cloud: docker
Image: rafaelvzago/django_todolist_image_build
Cloud details - Configure Clouds - Enabled

### Instalar o plugin Config File Provider
Jenkins - Gerenciador de plugins - Config File Provider
depois de instalar
Jenkins - Managed files - Add a new Config - Custom file - Submit
##### Configurar o Managed Files para Dev
# Name : .env-dev
[config]
# Secret configuration
SECRET_KEY = 'r*5ltfzw-61ksdm41fuul8+hxs$86yo9%k1%k=(!@=-wv4qtyv'
# conf
DEBUG=True
# Database
DB_NAME = "todo_dev"
DB_USER = "devops_dev"
DB_PASSWORD = "mestre"
DB_HOST = "localhost"
DB_PORT = "3306"
#### Configurar o Managed Files para Prod
# Name: .env.-prod
[config]
# Secret configuration
SECRET_KEY = 'r*5ltfzw-61ksdm41fuul8+hxs$86yo9%k1%k=(!@=-wv4qtyv'
# conf
DEBUG=False
# Database
DB_NAME = "todo"
DB_USER = "devops"
DB_PASSWORD = "mestre"
DB_HOST = "localhost"
DB_PORT = "3306"
# No job: jenkins-todo-list-principal importar o env de dev para teste:
Adicionar passo no build: Provide configuration Files
File: .env-dev
Target: ./project-todo-list/to_do/.env
Adicionar passo no build: Executar Shell
# Criando o Script para Subir o container com o arquivo de env e testar a app:
#!/bin/sh
# Subindo o container de teste
docker run -d -p 82:8000 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v /var/lib/jenkins/workspace/jenkins-todo-list-principal/project-todo-lis/to_do/.env:/usr/src/app/to_do/.env --name=todo-list-teste django_todolist_image_build
# Testando a imagem <- Não utilizei no projeto node
docker exec -i todo-list-teste python manage.py test --keep
exit_code=$?
# Derrubando o container velho
docker rm -f heroku-node-dev
if [ $exit_code -ne 0 ]; then
exit 1
fi

### Instalar o plugin: Parameterized Trigger - Passa parametro de um build para outro
# Modificar o Job para startar com 2 parametros:
# No job agora - Geral - Este build é parametrizado - Param String - 
Este build é parametrizado com 2 parametros de string
Nome: image
Valor padrão: gustavocarvalhoti/heroku-node-build
Nome: DOCKER_HOST
Valor padrão: tcp://127.0.0.1:2376
# No build step: Build / Publish Docker Image
# Mudar o nome da imagem para: <seu-usuario-no-dockerhub>/django_todolist_image_build
# Marcar: Push Image e configurar **suas credenciais** no dockerhub
# Mudar no job de teste a imagem para: ${image}
docker run -d -p 82:8000 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v /var/lib/jenkins/workspace/jenkins-todo-list-principal/to_do/.env:/usr/src/app/to_do/.env --name=todo-list-teste ${image}

### Criar app no slack: alura-jenkins.slack.com
URL básico: <Url do Jenkins app no seu canal do Slack>
Token de integração: <Token do Jenkins app no seu canal do Slack>
# Instalar o plugin do slack: Gerenciar Jenkins > Gerenciar Plugins > Disponíveis: Slack Notification
# Configurar no jenkins: Gerenciar Jenkins > Configuraçao o sistema > Global Slack Notifier Settings
# Slack compatible app URL (optional): <Url do Jenkins app no seu canal do Slack>
# Integration Token Credential ID : ADD > Jenkins > Secret Text
# Secret: <Token do Jenkins app no seu canal do Slack>
# ID: slack-token
# Channel or Slack ID: pipeline-todolist
# As notificações vão funcionar da seguinte maneira:
Job: todo-list-desenvolvimento será feito pelo Jenkinsfile (Próximas aulas)
Job: todo-list-producao: Ações de pós-build > Slack Notifications: Notify Success e Notify Every Failure

### Novo Job: todo-list-desenvolvimento - Ele dá o play na imagem
# Tipo: Pipeline
# Este build é parametrizado com 2 Builds de Strings:
Nome: image
Valor padrão: - Vazio, pois o valor sera recebido do job anterior.
Nome: DOCKER_HOST
Valor padrão: tcp://127.0.0.1:2376
Pipeline - Pipeline script
#Exemplo 1
pipeline {
    agent any  
    stages {
        stage('Oi Mundo Pipeline como Codigo') {
            steps {
                sh 'echo "Oi Mundo"'
            }
        }
    }
}

#Definitivo
pipeline {
    environment {
        dockerImage = "${image}"
    }
    agent any
    stages {
        stage('Carregando o ENV de desenvolvimento') {
            steps {
                configFileProvider([configFile(fileId: '<id do seu arquivo de desenvolvimento>', variable: 'env')]) {
                    sh 'cat $env > .env'
                }
            }
        }
        stage('Derrubando o container antigo') {
            steps {
                script {
                    try {
                        sh 'docker rm -f heroku-node-dev'
                    } catch (Exception e) {
                        sh "echo $e"
                    }
                }
            }
        }        
        stage('Subindo o container novo') {
            steps {
                script {
                    try {
                        sh 'docker run -d -p 81:8000 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v /var/lib/jenkins/workspace/jenkins-todo-list-desenvolvimento/.env:/usr/src/app/to_do/.env --name=django-todolist-dev ' + dockerImage + ':latest'
                    } catch (Exception e) {
                        slackSend (color: 'error', message: "[ FALHA ] Não foi possivel subir o container - ${BUILD_URL} em ${currentBuild.duration}s", tokenCredentialId: 'slack-token')
                        sh "echo $e"
                        currentBuild.result = 'ABORTED'
                        error('Erro')
                    }
                }
            }
        }
        stage('Notificando o usuario') {
            steps {
                slackSend (color: 'good', message: '[ Sucesso ] O novo build esta disponivel em: http://192.168.33.10:81/ ', tokenCredentialId: 'slack-token')
            }
        }
    }
}
# todo-list-principal
# Definir post build: image=$image

### Criar o job para colocar a app em producao:
Nome: todo-list-producao
Tipo: Freestyle
# Este build é parametrizado com 2 Builds de Strings:
    Nome: image
    Valor padrão: - Vazio, pois o valor sera recebido do job anterior.
    Nome: DOCKER_HOST
    Valor padrão: tcp://127.0.0.1:2376

# Ambiente de build > Provide configuration files
    File: .env-prod
    Target: .env

### Build > Executar shell
#Execute shell
#!/bin/sh
{ 
    docker run -d -p 80:8000 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v /var/lib/jenkins/workspace/todo-list-producao/.env:/usr/src/app/to_do/.env --name=django-todolist-prod $image:latest
} || { # catch
    docker rm -f django-todolist-prod
    docker run -d -p 80:8000 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v /var/lib/jenkins/workspace/todo-list-producao/.env:/usr/src/app/to_do/.env --name=django-todolist-prod $image:latest
}
Ações de pós-build > Slack Notifications: Notify Success e Notify Every Failure

### Post build actions para os 3 jobs
Job: jenkins-todo-list-principal > Ações de pós-build > Trigger parameterized buld on other projects
    Projects to build: todo-list-desenvolvimento
    # Add parameters > Predefined parameters
        image=${image}
Job: todo-list-desenvolvimento
pipeline {
    environment {
        dockerImage = "${image}"
    }
    agent any    
    stages {
        stage('Carregando o ENV de desenvolvimento') {
            steps {
                configFileProvider([configFile(fileId: '71bbc5b0-00b1-4f58-8e81-a16fcf99dbed', variable: 'env')]) {
                    sh 'cat $env > .env'
                }
            }
        }
        stage('Derrubando o container antigo') {
            steps {
                script {
                    try {
                        sh 'docker rm -f django-todolist-dev'
                    } catch (Exception e) {
                        sh "echo $e"
                    }
                }
            }
        }        
        stage('Subindo o container novo') {
            steps {
                script {
                    try {
                        sh 'docker run -p 81:3000 -d --name=heroku-node-dev ' + dockerImage + ':latest'
                        // sh 'docker run -d -p 81:8000 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v /var/lib/jenkins/workspace/todo-list-desenvolvimento/.env:/usr/src/app/to_do/.env --name=django-todolist-dev ' + dockerImage + ':latest'
                    } catch (Exception e) {
                        // slackSend (color: 'error', message: "[ FALHA ] Não foi possivel subir o container - ${BUILD_URL} em ${currentBuild.duration}s", tokenCredentialId: 'slack-token')
                        sh "echo $e"
                        currentBuild.result = 'ABORTED'
                        error('Erro')
                    }
                }
            }
        }
        stage('Notificando o usuario') {
            steps {
                #slackSend (color: 'good', message: '[ Sucesso ] O novo build esta disponivel em: http://192.168.33.10:81/ ', tokenCredentialId: 'slack-token')
            }
        }
        stage ('Fazer o deploy em producao?') {
            steps {
                script {
                    #slackSend (color: 'warning', message: "Para aplicar a mudança em produção, acesse [Janela de 10 minutos]: ${JOB_URL}", tokenCredentialId: 'slack-token')
                    timeout(time: 10, unit: 'MINUTES') {
                        input(id: "Deploy Gate", message: "Deploy em produção?", ok: 'Deploy')
                    }
                }
            }
        }
        stage (deploy) {
            steps {
                script {
                    try {
                        build job: 'todo-list-producao', parameters: [[$class: 'StringParameterValue', name: 'image', value: dockerImage]]
                    } catch (Exception e) {
                        // slackSend (color: 'error', message: "[ FALHA ] Não foi possivel subir o container em producao - ${BUILD_URL}", tokenCredentialId: 'slack-token')
                        sh "echo $e"
                        currentBuild.result = 'ABORTED'
                        error('Erro')
                    }
                }
            }
        }
    }
}

### Criar o job para colocar a app em producao:
Nome: todo-list-producao
Tipo: Freestyle
# Este build é parametrizado com 2 Builds de Strings:
    Nome: image
    Valor padrão: - Vazio, pois o valor sera recebido do job anterior.
    Nome: DOCKER_HOST
    Valor padrão: tcp://127.0.0.1:2376
# Ambiente de build > Provide configuration files
    File: .env-prod
    Target: .env
# Build > Executar shell
    #Execute shell
    #!/bin/sh
    {   
        docker run -p 82:3000 -d --name=heroku-node-homologacao $image:latest
    } || { 
        # catch
        docker rm -f heroku-node-homologacao
        docker run -p 82:3000 -d --name=heroku-node-homologacao $image:latest
    }
Ações de pós-build > Slack Notifications: Notify Success e Notify Every Failure

### Post build actions para os 3 jobs
Job: jenkins-todo-list-principal > Ações de pós-build > Trigger parameterized buld on other projects
    Projects to build: todo-list-desenvolvimento
    # Add parameters > Predefined parameters
        image=${image}
Job: todo-list-desenvolvimento
pipeline {
    environment {
        dockerImage = "${image}"
    }
    agent any
    stages {
        stage('Carregando o ENV de desenvolvimento') {
            steps {
                configFileProvider([configFile(fileId: '2ed9697c-45fc-4713-a131-53bdbeea2ae6', variable: 'env')]) {
                    sh 'cat $env > .env'
                }
            }
        }
        stage('Derrubando o container antigo') {
            steps {
                script {
                    try {
                        sh 'docker rm -f django-todolist-dev'
                    } catch (Exception e) {
                        sh "echo $e"
                    }
                }
            }
        }        
        stage('Subindo o container novo') {
            steps {
                script {
                    try {
                        sh 'docker run -d -p 81:8000 -v /var/run/mysqld/mysqld.sock:/var/run/mysqld/mysqld.sock -v /var/lib/jenkins/workspace/todo-list-desenvolvimento/.env:/usr/src/app/to_do/.env --name=django-todolist-dev ' + dockerImage + ':latest'
                    } catch (Exception e) {
                        slackSend (color: 'error', message: "[ FALHA ] Não foi possivel subir o container - ${BUILD_URL} em ${currentBuild.duration}s", tokenCredentialId: 'slack-token')
                        sh "echo $e"
                        currentBuild.result = 'ABORTED'
                        error('Erro')
                    }
                }
            }
        }
        stage('Notificando o usuario') {
            steps {
                slackSend (color: 'good', message: '[ Sucesso ] O novo build esta disponivel em: http://192.168.33.10:81/ ', tokenCredentialId: 'slack-token')
            }
        }
        stage ('Fazer o deploy em producao?') {
            steps {
                script {
                    slackSend (color: 'warning', message: "Para aplicar a mudança em produção, acesse [Janela de 10 minutos]: ${JOB_URL}", tokenCredentialId: 'slack-token')
                    timeout(time: 10, unit: 'MINUTES') {
                        input(id: "Deploy Gate", message: "Deploy em produção?", ok: 'Deploy')
                    }
                }
            }
        }
        stage (deploy) {
            steps {
                script {
                    try {
                        build job: 'todo-list-producao', parameters: [[$class: 'StringParameterValue', name: 'image', value: dockerImage]]
                    } catch (Exception e) {
                        slackSend (color: 'error', message: "[ FALHA ] Não foi possivel subir o container em producao - ${BUILD_URL}", tokenCredentialId: 'slack-token')
                        sh "echo $e"
                        currentBuild.result = 'ABORTED'
                        error('Erro')
                    }
                }
            }
        }
    }
}

### Subindo o container com o Sonarcube
Na máquina devops (Vagrant): docker run -d --name sonarqube -p 9000:9000 sonarqube:lts
# Acessar: http://localhost:9000
Usuário: admin
Senha: admin
New project
Name: jenkins-todolist
    Provide a token: jenkins-todolist e anotar o seu token
    Run analysis on your project > Other (JS, Python, PHP, ...) > Linux > django-todo-list
# Copie o shell script fornecido
sonar-scanner \
  -Dsonar.projectKey=jenkins-todolist \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=2c354e1782796f46b18ccc970c2d1284b663d029

# Criar um job para Coverage com o nome: todo-list-sonarqube - free-style
# Gerenciamento de código fonte > Git
    git: git@github.com:gustavocarvalhoti/heroku-node.git (Selecione as mesmas credenciais)
    branch: master
    Pool SCM: * * * * *
    Delete workspace before build starts
    Execute Script:
# Build > Adicionar passo no build > Executar Shell
#!/bin/bash
# Baixando o Sonarqube
wget https://s3.amazonaws.com/caelum-online-public/1110-jenkins/05/sonar-scanner-cli-3.3.0.1492-linux.zip
# Descompactando o scanner
unzip sonar-scanner-cli-3.3.0.1492-linux.zip
# Rodando o Scanner
./sonar-scanner-3.3.0.1492-linux/bin/sonar-scanner   -X \
  -Dsonar.projectKey=jenkins-todolist \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=86d59838b116dd62fb9f82c0a199af6c03e6fa2a
```
