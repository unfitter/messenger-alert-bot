ARG PYTHON3_IMAGE=

FROM ${PYTHON3_IMAGE}

LABEL maintainer="Oleg Shvets <olegsvec742@gmail.com>"

COPY messenger-alert-bot/ /messenger-alert-bot

WORKDIR /messenger-alert-bot

RUN pip install --break-system-packages --no-cache-dir -r ./requirements.txt

RUN apt-get update && apt-get -y install libglib2.0-0 libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*



RUN pip install --no-cache-dir --break-system-packages 

CMD ["main:app", "--host", "0.0.0.0", "--port", "80"]

ENTRYPOINT ["uvicorn"]
