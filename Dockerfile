FROM python:3.9

# Create folder and user
RUN adduser ambnum && \
    chmod 777 /home/ambnum && \
    chown ambnum:ambnum /home/ambnum

# # update package repositories
RUN apt-get update -y
RUN pip install --upgrade pip setuptools wheel

# install code
WORKDIR /home/ambnum
RUN pip install -e git+https://github.com/JustAnotherArchivist/snscrape.git#egg=snscrape
RUN pip install social-networks-graph-generator

CMD [ "/bin/bash" ]
