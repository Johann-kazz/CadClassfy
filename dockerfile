FROM ubuntu:20.04
USER root

WORKDIR /app

RUN apt update
RUN apt install -y python3.8
RUN apt install -y python3-pip
RUN apt-get install build-essential
RUN apt-get install python3-dev python3.8-dev
#RUN apt curl
#RUN apt software-properties-common

RUN rm -rf /var/lib/apt/lists/*

#COPY requirements.txt .
COPY . .
RUN python3.8 -m pip install -r requirements.txt

EXPOSE 8501

ENV SITE_DOMAIN=CadClassfy.takedaTech.com

ENTRYPOINT ["streamlit", "run", "dxf_fasttext_app.py", "--server.port=8501", "--server.address=0.0.0.0"]