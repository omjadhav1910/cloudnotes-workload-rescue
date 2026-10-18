FROM python:3.12-slim-bookworm
WORKDIR /app
COPY app/app.py .
RUN mkdir -p /data /archive && chmod 1777 /data /archive
USER 10001:10001
EXPOSE 8080
CMD ["python", "app.py"]
