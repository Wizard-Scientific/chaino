FROM python:3.9.17-slim-bullseye

RUN apt update \
  && apt -y install \
  git-core && \
  /bin/rm -f /var/cache/apt/archives/*.deb

RUN adduser \
  --uid 950 \
  --shell /bin/bash \
  --disabled-password \
  "chaino"

RUN mkdir /mnt/chaino \
  && chown chaino:chaino /mnt/chaino

USER chaino
WORKDIR /home/chaino
VOLUME ["/mnt/chaino"]

RUN python3.9 -m venv /home/chaino/venv
RUN /home/chaino/venv/bin/pip install \
    --no-cache-dir \
    'git+https://github.com/0xidm/chaino'

RUN echo source /home/chaino/venv/bin/activate >> /home/chaino/.bashrc
RUN /home/chaino/venv/bin/blockchain.py
CMD /bin/bash
