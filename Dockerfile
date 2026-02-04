FROM python:3.9

WORKDIR /code

# Install requirements
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy everything else
COPY . .

# Required for Hugging Face Spaces to show the website
CMD ["streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
