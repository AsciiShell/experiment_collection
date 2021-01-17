FROM snakepacker/python:all as builder

# Install psycopg2 utils
RUN apt-get update && \
	apt-get install -y --no-install-recommends libpq-dev && \
	rm -fr /var/lib/apt/lists /var/lib/cache/* /var/log/*

RUN python3.8 -m venv /usr/share/python3/app
RUN /usr/share/python3/app/bin/pip install -U pip

COPY requirements_server.txt /mnt/
RUN /usr/share/python3/app/bin/pip install -Ur /mnt/requirements_server.txt

COPY dist/experiment_collection_server*.whl /mnt/dist/
RUN /usr/share/python3/app/bin/pip install /mnt/dist/* && /usr/share/python3/app/bin/pip check

FROM snakepacker/python:3.8 as api

# Install psycopg2 utils
RUN apt-get update && \
	apt-get install -y --no-install-recommends libpq-dev && \
	rm -fr /var/lib/apt/lists /var/lib/cache/* /var/log/*

COPY --from=builder /usr/share/python3/app /usr/share/python3/app

RUN ln -snf /usr/share/python3/app/bin/experiment_collection_server /usr/local/bin/
CMD experiment_collection_server
