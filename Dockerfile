# docker build -t prjct_noname .
# docker run --name dockercontainer
From python:3.11-slim

ENV PYTHONUNBUFFERED=1
RUN apt update

# 가상환경 설치 && 실행
RUN python3 -m venv myvenv
RUN source myvenv/bin/activate

# workspace 폴더 생성
RUN mkdir /srv/workspace
# WORKDIR 이동
WORKDIR /srv/workspace

# requirements 설치
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 8000
CMD ["python3", "./project_noName/manage.py", "runserver", "0.0.0.0:8000"]
