FROM python:3.9-slim

RUN pip install redis

RUN apt-get update && apt-get install -y curl unzip && \
    curl -O https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip && \
    unzip terraform_1.5.0_linux_amd64.zip -d /usr/local/bin/ && \
    rm terraform_1.5.0_linux_amd64.zip

COPY autoscaler.py /app/autoscaler.py
WORKDIR /app

# infra/azure se monteaza din afara: -v $(pwd)/infra/azure:/infra
# Autentificarea Azure se face prin ARM_CLIENT_ID / ARM_CLIENT_SECRET / ARM_TENANT_ID / ARM_SUBSCRIPTION_ID
ENV TF_DIR=/infra
CMD ["python", "-u", "autoscaler.py"]
