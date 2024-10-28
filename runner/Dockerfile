#FROM mambaorg/micromamba:1.5.8-jammy
FROM continuumio/miniconda3

LABEL org.opencontainers.image.source=https://github.com/ssciwr/predicTCR
LABEL org.opencontainers.image.description="predicTCR runner image"
LABEL org.opencontainers.image.licenses=MIT

COPY env.yaml /tmp/env.yaml

RUN conda env create -f /tmp/env.yaml

WORKDIR /app

COPY . .

SHELL ["conda", "run", "-n", "predictcr", "/bin/bash", "-c"]

RUN python -m pip install . && rm -rf *

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "predictcr", "predicTCR_runner"]
