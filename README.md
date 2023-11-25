# aktarai module

### download and install
git clone repo


### torchvision
```
$ sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev
$ git clone --branch <version> https://github.com/pytorch/vision torchvision   # see below for version of torchvision to download
$ cd torchvision
$ export BUILD_VERSION=0.x.0  # where 0.x.0 is the torchvision version  
$ python3 setup.py install --user
$ cd ../
$ pip install 'pillow<7' # always needed for Python 2.7, not needed torchvision v0.5.0+ with Python 3.6
```
---
Select the version of torchvision to download depending on the version of PyTorch that you have installed:
- PyTorch v1.0 - torchvision v0.2.2
- PyTorch v1.1 - torchvision v0.3.0
- PyTorch v1.2 - torchvision v0.4.0
- PyTorch v1.3 - torchvision v0.4.2
- PyTorch v1.4 - torchvision v0.5.0
- PyTorch v1.5 - torchvision v0.6.0
- PyTorch v1.6 - torchvision v0.7.0
- PyTorch v1.7 - torchvision v0.8.1
- PyTorch v1.8 - torchvision v0.9.0
- PyTorch v1.9 - torchvision v0.10.0
- PyTorch v1.10 - torchvision v0.11.1
- PyTorch v1.11 - torchvision v0.12.0
- PyTorch v1.12 - torchvision v0.13.0
- PyTorch v1.13 - torchvision v0.13.0
- PyTorch v1.14 - torchvision v0.14.1
- PyTorch v2.0.0 - torchvision v0.15.1
---
Ref: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048

### gi
```
sudo apt install libcairo2-dev libxt-dev libgirepository1.0-dev
pip install pycairo PyGObject
```

### build and distribute
python3 setup.py build_ext --inplace
python3 setup.py bdist_wheel
