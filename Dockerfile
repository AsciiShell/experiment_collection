FROM snakepacker/python:all as builder
RUN python3.8 -m venv /usr/share/python3/app
RUN /usr/share/python3/app/bin/pip install -U pip

COPY requirements_server.txt /mnt/
RUN /usr/share/python3/app/bin/pip install -Ur /mnt/requirements_server.txt

COPY dist/experiment_collection_server* /mnt/dist/
RUN /usr/share/python3/app/bin/pip install /mnt/dist/* && /usr/share/python3/app/bin/pip check

FROM snakepacker/python:3.8 as api

COPY --from=builder /usr/share/python3/app /usr/share/python3/app

RUN ln -snf /usr/share/python3/app/bin/experiment_collection_server /usr/local/bin/
CMD ["experiment_collection_server"]
