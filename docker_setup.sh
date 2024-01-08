#!/bin/bash

working_dir=$(pwd)
apt install -y libcairo2-dev libxt-dev libgirepository1.0-dev
apt-get install -y libjpeg-dev zlib1g-dev libpython3-dev libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
wget http://78.135.73.226:8000/aktarai-0.1.3-cp38-cp38-linux_aarch64.whl
wget http://78.135.73.226:8000/onnxruntime_gpu-1.12.1-cp38-cp38-linux_aarch64.whl
wget http://78.135.73.226:8000/torch-1.14.0a0%2B44dac51c.nv23.02-cp38-cp38-linux_aarch64.whl
pip install packages/onnxruntime_gpu-1.12.1-cp38-cp38-linux_aarch64.whl
pip install packages/torch-1.14.0a0+44dac51c.nv23.02-cp38-cp38-linux_aarch64.whl
pip uninstall -y torchvision
pip install packages/torchvision-0.14.1a0+5e8e2f1-cp38-cp38-linux_aarch64.whl

torchvision=$(pip freeze | grep torchvision)
if [ "$torchvision" == "" ]
then
    cd packages
    git clone --branch v0.14.1  https://github.com/pytorch/vision torchvision
    cd torchvision
    git pull
    export BUILD_VERSION="0.14.1"
    python setup.py install
    cd ..
else
    echo torchvision "0.14.1" is previously installed
fi
cd ../../aktar-ai
