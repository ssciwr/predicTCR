FROM ghcr.io/mamba-org/micromamba:debian11-slim

LABEL org.opencontainers.image.source=https://github.com/ssciwr/predicTCR
LABEL org.opencontainers.image.description="predicTCR runner image"
LABEL org.opencontainers.image.licenses=MIT

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml

RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1

WORKDIR /app

COPY --chown=$MAMBA_USER:$MAMBA_USER . .

RUN python -m pip install . && rm -rf *

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "predicTCR_runner"]
