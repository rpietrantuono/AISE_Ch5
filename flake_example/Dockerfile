FROM python:3.10-slim AS builder
COPY . /src
WORKDIR /src
RUN pip install --user --no-cache-dir -r requirements.txt


FROM python:3.10-slim AS app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /src .

ENV PATH=/root/.local:$PATH
EXPOSE 5000

CMD ["python3", "app.py"]

