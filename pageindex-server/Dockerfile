FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV OPENAI_API_KEY=""
ENV PAGEINDEX_DATA_DIR=""
ENV PAGEINDEX_PORT="37779"

EXPOSE 37779

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "37779"]
