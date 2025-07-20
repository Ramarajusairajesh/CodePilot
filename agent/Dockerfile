FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
	xvfb xdotool fluxbox tigervnc-standalone-server novnc websockify \
	python3 python3-pip nodejs npm git curl && \
	pip3 install jupyter flask

# Pre-create X11 socket dir for non-root user
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

RUN useradd -ms /bin/bash agent
WORKDIR /home/agent
COPY . /home/agent/
COPY start.sh /start.sh
RUN chmod +x /start.sh
EXPOSE 5901 8080 5000 8888
USER agent
CMD ["/start.sh"] 
