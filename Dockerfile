FROM "ubuntu"

Run apt-get update && yes | apt-get upgrade

RUN mkdir -p /server
RUN mkdir -p /tensorflow/models

RUN apt-get install -y git python-pip

RUN pip install tensorflow==1.4

RUN apt-get install -y protobuf-compiler python-pil python-lxml
RUN pip install jupyter
RUN pip install matplotlib
RUN pip install flask

RUN git clone https://github.com/tensorflow/models.git /tensorflow/models


WORKDIR /tensorflow/models/research

RUN protoc object_detection/protos/*.proto --python_out=.

RUN export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim

RUN jupyter notebook --generate-config --allow-root
RUN echo "c.NotebookApp.password = u'sha1:6a3f528eec40:6e896b6e4828f525a6e20e5411cd1c8075d68619'" >> /root/.jupyter/jupyter_notebook_config.py

EXPOSE 8888

#CMD ["jupyter", "notebook", "--allow-root", "--notebook-dir=/server", "--ip='*'", "--port=8888", "--no-browser"]

WORKDIR /server

RUN git config --global user.email "t.brown@helyx.co.uk"
RUN git config --global user.name "theoesque"

RUN git clone https://theoesque:7uryR0ad!234!@bitbucket.org/theoesque/lstf.git

WORKDIR /server/lstf
RUN mkdir -p /server/lstf/uploads
CMD ["export", "FLASK_APP=app.py"]
CMD ["flask", "run"]
