# aktarai module

### download and install
`git clone git@github.com:mostafamoradipour/Aktar.git`


### torchvision
```
$ sudo apt-get install libjpeg-dev zlib1g-dev libpython3-dev libopenblas-dev libavcodec-dev libavformat-dev libswscale-dev
$ git clone --branch <version> https://github.com/pytorch/vision torchvision   # see below for version of torchvision to download
$ cd torchvision
$ export BUILD_VERSION=0.x.0  # where 0.14.1 is the torchvision version  
$ python3 setup.py install --user
$ cd ../
$ pip install 'pillow<7' # always needed for Python 2.7, not needed torchvision v0.5.0+ with Python 3.6
```
Ref: https://forums.developer.nvidia.com/t/pytorch-for-jetson/72048

### gi
```
sudo apt install libcairo2-dev libxt-dev libgirepository1.0-dev
pip install pycairo PyGObject
```

### build and distribute
```
source menv/bin/activate
python3 setup.py bdist_wheel
```
