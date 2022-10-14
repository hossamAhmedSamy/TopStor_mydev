FROM httpd
# Add application sources
#ADD app-src/index.html /var/www/html/index.html
RUN apt update
RUN apt upgrade
RUN apt install -y git 
# The run script uses standard ways to run the application
