#!/bin/bash

working_dir=$(pwd)
echo $working_dir
python3 -m venv menv
source menv/bin/activate
sudo apt install -y libcairo2-dev libxt-dev libgirepository1.0-dev
sudo apt-get install -y libjpeg-dev zlib1g-dev libpython3-dev libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev
pip install --upgrade pip
pip install wheel

pip install ultralytics==8.0.148
# ultralytics=$(pip freeze | grep ultralytics)
# if [ $ultralytics == "" ]
# then
#     pip install ultralytics==8.0.148
# else
#     echo ultralytics "v8.0.148" is previously installed
# fi

pip install -r requirements.txt
cd ../aktar-automation/services
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
