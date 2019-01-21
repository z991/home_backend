FROM reg.xiaoneng.cn/oa/home_backend_base:latest

WORKDIR /src

COPY . .

ENV TZ "Asia/Shanghai"
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
CMD ["gunicorn", "home_backend.wsgi", "--workers=5", "--bind=0.0.0.0:8008", "--reload"]