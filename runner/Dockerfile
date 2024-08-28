FROM mambaorg/micromamba:1.5.8-jammy

LABEL org.opencontainers.image.source=https://github.com/ssciwr/predicTCR
LABEL org.opencontainers.image.description="predicTCR runner image"
LABEL org.opencontainers.image.licenses=MIT

COPY --chown=$MAMBA_USER:$MAMBA_USER env.yaml /tmp/env.yaml

RUN micromamba install -y -n base -f /tmp/env.yaml && \
    micromamba clean --all --yes && \
    rm -rf /tmp/env.yaml

WORKDIR /app

COPY runner.py /app/runner.py

COPY scripts /app/scripts

CMD ["python", "runner.py"]
