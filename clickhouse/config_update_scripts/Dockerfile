FROM python

WORKDIR /update_scripts

COPY . /update_scripts/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3","update_trigger.py"]