FROM pytorch/torchserve:latest-cpu

RUN pip install keybert
COPY archived_model/model.mar /home/model-server/model-store
COPY config.properties /home/model-server/
