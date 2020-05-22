# Treinamento Alura - Jenkins e Docker: Pipeline de entrega continua
https://cursos.alura.com.br/course/pipeline-ci-jenkins-docker

## SO utilizado Ubuntu 18.04

## Instalar
```bash
cd scripts/
./get-docker.sh
./docker.sh                     <- Install docker e pull image
./jenkins.sh                    <- Install

Install MySQL
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
```

## Comandos
```bash
http://localhost:8080/                                          <- Jenkins
sudo cat /var/lib/jenkins/secrets/initialAdminPassword          <- Senha Jenkins, instalar os plugins default
user: adm
pass: mestre123
```
