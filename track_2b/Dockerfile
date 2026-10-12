FROM python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOST=0.0.0.0 PORT=4377
WORKDIR /app
COPY src/ ./src/
COPY data/ ./data/
COPY download_model.py ./download_model.py
USER 10001:10001
EXPOSE 4377
CMD ["python", "src/server.py"]
