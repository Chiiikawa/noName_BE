From python:3.11-slim

ENV PYTHONUNBUFFERED=1
RUN apt update


# 가상환경 설치 && 실행
RUN python3 -m venv myvenv
RUN echo "source myvenv/bin/activate"

# workspace 폴더 생성
RUN mkdir -p /srv/workspace/noName_BE
WORKDIR /srv/workspace/noName_BE
# WORKDIR 이동



# requirements 설치
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary


EXPOSE 8000
