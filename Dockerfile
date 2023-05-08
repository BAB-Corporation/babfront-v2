# The default Docker image
ARG IMAGE_BASE_NAME
ARG BASE_IMAGE_HASH
ARG BASE_BUILDER_IMAGE_HASH

FROM ${IMAGE_BASE_NAME}:base-builder-${BASE_BUILDER_IMAGE_HASH} as builder
# copy files
COPY . /build/

# change working directory
WORKDIR /build

# install dependencies
# install dependencies
RUN python -m venv /opt/venv && \
  . /opt/venv/bin/activate && \
  pip install --no-cache-dir -U 'pip<20' && \
  pip install --no-cache-dir -U 'cryptography' && \
  pip install --no-cache-dir -U 'requests' && \
  poetry install --extras full --no-dev --no-root --no-interaction

RUN pip install wheel && \
  cd rasa_addons && \
  mkdir rasa_addons && \
  mv `\ls -1 . | grep -v -e setup.py -e rasa_addons` ./rasa_addons/ && \
  python setup.py install && \
  cd ..

RUN poetry build -f wheel -n && \
  pip install --no-deps dist/*.whl && \
  rm -rf dist *.egg-info

# start a new build stage
FROM ${IMAGE_BASE_NAME}:base-${BASE_IMAGE_HASH} as runner

# copy everything from /opt
COPY --from=builder /opt/venv /opt/venv

# make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# update permissions & change user to not run as root
WORKDIR /app
RUN chgrp -R 0 /app && chmod -R g=u /app
USER 1001

# create a volume for temporary data
VOLUME /tmp

# change shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# the entry point
EXPOSE 5005

CMD rasa run \
  $([ -n "$MODEL_PATH" ] && echo "-m $MODEL_PATH") \
  $([ -n "$AUTH_TOKEN" ] && echo "--auth-token $AUTH_TOKEN" ) \
  --enable-api --debug
