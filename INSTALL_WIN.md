# Installation instructions for Windows
These installation instructions use Anaconda as Python environment because it is easy to install. Other Windows Python Distributions may work as well.  
## install Anaconda
* Download [Anaconda](https://www.continuum.io/downloads) for Python 2.7
* Start the downloaded .exe file
* Use the "Just Me (recommended)" installation type.
## install OpenCV 2.4
* Download [OpenCV Win Pack](https://sourceforge.net/projects/opencvlibrary/files/opencv-win/2.4.13/opencv-2.4.13.exe/download)
* Start the downloaded .exe file (self extracting zip) to C:\opencv
* Locate the appropriate cv2.pyd file for your system:  
C:\opencv\build\python\2.7\x64\cv2.pyd for 64bit architecture  
C:\opencv\build\python\2.7\x86\cv2.pyd for 32bit architecture  
* Copy cv2.pyd into Anacondas site-packages folder:  
c:\Users\YOURUSER\Anaconda2\Lib\site-packages
* Add the required user environment variable to your system:  
Variable: OPENCV_DIR  Value: C:\opencv\build\x64\vc12  
 or use C:\opencv\build\x86\vc12 for 32bit architecture
* Add %OPENCV_DIR%\bin to "Path" user environment variable.
## install Kivy (not needed for command line version in 'cli' folder)
* Open Anaconda Prompt and enter the following commands:
* Check you have the latest versions of pip and wheel  
python -m pip install --upgrade pip wheel setuptools
* Install the dependencies
python -m pip install docutils pygments pypiwin32 kivy.deps.sdl2 kivy.deps.glew kivy.deps.gstreamer
* Install Kivy  
python -m pip install kivy
* You may get errors and tracebacks during these installs. Problems can often be solved by simply repeating the command that caused the error.
## install and use PyFSPro
* Download or clone PyFSPro
* Start it from within Anaconda Prompt:  
python PyFSPro.py
