FROM w251/cuda:dev-tx2-4.2.1_b97

ARG URL=http://169.44.201.108:7002/jetpacks/4.2.1

RUN apt-get update && apt install -y git pkg-config wget build-essential cmake unzip python-pip

# Install OpenCV
RUN curl $URL/libopencv_3.3.1-2-g31ccdfe11_arm64.deb  -so libopencv_3.3.1-2-g31ccdfe11_arm64.deb
RUN curl $URL/libopencv-dev_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-dev_3.3.1-2-g31ccdfe11_arm64.deb
RUN curl $URL/libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb
RUN apt install -y  libtbb-dev libavcodec-dev libavformat-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev
RUN apt install -y libswscale-dev libv4l-dev
RUN dpkg -i *.deb

# Install Python dependencies
RUN apt-get update && apt-get install -y python3 python3-dev python3-pip libjpeg-dev python3-pil
RUN pip3 install paho-mqtt imutils dlib face_recognition 

# Install our developed code + model
COPY forwarder.py /
ENTRYPOINT python3 forwarder.py 
