FROM python:3.6.8 

RUN pip install -U pip 
COPY . /now_sheet
RUN pip install -r /now_sheet/requirements.txt
RUN pip install gunicorn
RUN pip install uvloop==0.14.0 httptools

RUN pip install -e /now_sheet
WORKDIR /now_sheet

CMD gunicorn --workers=1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 index:app --access-logfile -
