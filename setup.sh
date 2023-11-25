#!/bin/bash

working_dir=$(pwd)
echo $working_dir
python3 -m venv menv
source menv/bin/activate
pip install --upgrade pip
if [ $(pip freeze | grep ultralytics) == "ultralytics==8.0.148" ]
then
    echo ultralytics "v8.0.148" is previously installed
else
    pip install ultralytics==8.0.148
fi
cd /mnt/storage/projects/Aktar/aktar-automation/services/packages
pip install onnxruntime_gpu-1.12.1-cp38-cp38-linux_aarch64.whl
pip install torch-1.14.0a0+44dac51c.nv23.02-cp38-cp38-linux_aarch64.whl
pip uninstall -y torchvision
git clone --branch v0.14.1  https://github.com/pytorch/vision torchvision
cd torchvision
export BUILD_VERSION="0.14.1"
python setup.py install
echo $working_dir
cd $working_dir
pip install -r requirements.txt
