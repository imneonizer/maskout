FROM nvcr.io/nvidia/deepstream-l4t:5.0.1-20.09-samples

ENV DS_PYTHON="/opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps"
RUN git clone https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git $DS_PYTHON
RUN bash -c "cd /opt/nvidia/deepstream/deepstream/lib && python3 setup.py install"
RUN apt-get update -y \
    && apt-get install vim python3-numpy python3-opencv -y \
    && apt install python3-gi python3-dev python3-gst-1.0 -y

WORKDIR $DS_PYTHON/apps/maskout
COPY . .
