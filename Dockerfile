FROM python:3.7-stretch

RUN apt-get update && apt-get install -yq \
    unzip \
    chromium=62.0.3202.89-1~deb9u1


# chromeDriver v2.35
RUN wget -q "https://chromedriver.storage.googleapis.com/2.35/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/bin/ \
    && rm /tmp/chromedriver.zip

# create symlinks to chromedriver (to the PATH)
RUN ln -s /usr/bin/chromium-browser \
    && chmod 777 /usr/bin/chromium-browser

ADD . /wsv
WORKDIR /wsv

# Should not be already included?
# RUN apt-get install -qy python3
# RUN apt-get install -qy python3-pip

RUN pip3 install -r requirements.txt

# Add job to crontab
RUN apt-get update && apt-get -y install cron
COPY wsv-cron /etc/cron.d/wsv-cron
RUN chmod 0644 /etc/cron.d/wsv-cron
RUN crontab /etc/cron.d/wsv-cron

RUN chmod 0744 WSV.py
RUN touch WSV.log
CMD cron && tail -f /wsv/WSV.log