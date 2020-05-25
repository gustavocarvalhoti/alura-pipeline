# Treinamento Alura - Jenkins e Docker: Pipeline de entrega continua
https://cursos.alura.com.br/course/pipeline-ci-jenkins-docker

## Ubuntu 18.04
https://github.com/gustavocarvalhoti/alura-pipeline/tree/master/project-todo-list

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
CREATE USER 'devops'@'172.17.0.1' IDENTIFIED BY 'mestre';
GRANT ALL PRIVILEGES ON *.* TO 'devops'@'172.17.0.1';
CREATE USER 'devops_dev'@'172.17.0.1' IDENTIFIED BY 'mestre';
GRANT ALL PRIVILEGES ON *.* TO 'devops_dev'@'172.17.0.1';
CREATE USER 'devops_dev'@'127.0.0.1' IDENTIFIED BY 'mestre';
GRANT ALL PRIVILEGES ON *.* TO 'devops_dev'@'127.0.0.1';
create database todo;
create database todo_dev;

CREATE USER 'devops'@'localhost' IDENTIFIED BY 'mestre';
GRANT ALL PRIVILEGES ON *.* TO 'devops'@'localhost';
CREATE USER 'devops'@'127.0.0.1' IDENTIFIED BY 'mestre';
GRANT ALL PRIVILEGES ON *.* TO 'devops'@'127.0.0.1';
CREATE USER 'devops'@'192.168.0.17' IDENTIFIED BY 'mestre';
GRANT ALL PRIVILEGES ON *.* TO 'devops'@'192.168.0.17';

### Recarregar as permissões
sudo usermod -aG docker $USER
sudo usermod -aG docker jenkins

### Python - Processo manual
sudo pip3 install virtualenv nose coverage nosexcover pylint
cd /home/padtec/dev-tools/projects/alura-pipeline/project-todo-list
source venv-django-todolist/bin/activate
pip install -r requirements.txt
#### Fazendo a migracao inicial dos dados
python manage.py makemigrations
python manage.py migrate
#### Criando o superuser para acessar a app
python manage.py createsuperuser
user: alura - pass: mestre123
# Rodando a app
python manage.py runserver 0:8000
http://localhost:8000
```

## Comandos
```bash
http://localhost:8080/                                          <- Jenkins
sudo cat /var/lib/jenkins/secrets/initialAdminPassword          <- Senha Jenkins, instalar os plugins default
user: adm
pass: mestre123

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
-> Gerenciamento de código fonte -> Git -> git@github.com:gustavocarvalhoti/alura-pipeline.git
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
docker run --rm -i hadolint/hadolint < Dockerfile
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
# Testando a imagem
docker exec -i todo-list-teste python manage.py test --keep
exit_code=$?
# Derrubando o container velho
docker rm -f todo-list-teste
if [ $exit_code -ne 0 ]; then
exit 1
fi

### Instalar o plugin: Parameterized Trigger - Passa parametro de um build para outro
# Modificar o Job para startar com 2 parametros:
# No job agora - Geral - Este build é parametrizado - Param String - 
Este build é parametrizado com 2 parametros de string
Nome: image
Valor padrão: gustavocarvalhoti/django_todolist_image_build
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

### Novo Job: todo-list-desenvolvimento
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
```
