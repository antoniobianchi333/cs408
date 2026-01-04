FROM ubuntu:22.04
RUN apt update && apt install -y python3 python3-pip
RUN rm -rf /var/lib/apt/lists/*
RUN pip install parsimonious
ADD submissions /submissions
ADD test_submissions /test_submissions
ADD grade.py /grade.py
ADD tests /tests