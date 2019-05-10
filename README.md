# PyFSPro - Python Frame Sequence Processor
## updated version with Kivy graphical user interface and now much better memory management.
Multi purpose realtime frame sequence and video processor for a wide range of applications including:
* [Schlieren Videography](https://hackaday.io/project/9034-schlieren-videography) using the Moiré-effect.
* Realtime Astronomical video processing for live presentations.
* Software image intensifier (night vision).
* Weak video signal detection and enhancement.
This is the GUI version of PyFSPro with a Kivy based graphical user interface.  
The older command line only (non Kivy) version of PyFSPro can be found in the 'cli' folder.
More information and and a dataflow diagram can be found in the [PyFSPro Wiki](https://github.com/mark-orion/PyFSPro/wiki)  
The 'doc' folder contains the flow diagram and pattern files that can be used for schlieren imaging.

## Main features
* Resizable ring buffer for image "stacking".
* High accuracy processing core using floating point maths for image processing.
* Input from Camera, Image sequence or Video file.
* Output to Screen, Image sequence or Video file.
* Input channel can be greyscale or extracted from RGB, HSV or YCrCb color space.
* Input and Output processing chains with basic image enhancement functions.
* Vectorscope for the visualization of small changes in video stream.
* Actuators can control third party applications with vectorscope data.
* Parameters can be set through the UI, command line options and configuration files.
* Most Parameters can be changed on the fly via the Kivy user interface.
* framestacker.py library can be re-used in other projects. It does not depend on OpenCV and only requires Numpy.

## Image enhancement and analysis functions
* Image integration (rolling average).
* Image difference to fixed reference (dark) frame or rolling average.
* Cumulative deviation of stacked images.
* Convolution filters with customizable kernels.
* Image stabilizer (experimental).
* Automatic or manual gain and offset.
* Histogram Equalization.
* Contrast Limited Adaptive Histogram Equalization (CLAHE).
* Blurring
* DeNoising
* Pseudo Color
* Histogram plot of input and output data (good for camera calibration).
* Transient filter (display or save frames that "stick out" of the sequence).

## Requirements
* Please refer to INSTALL.win for Windows installation instructions.
* Works with both Python 2 and 3
* Kivy (tested with version 1.9.1 and higher)
* Numpy (tested with version 1.11 and higher)
* OpenCV with Python bindings (supports both OpenCV 2 and 3)
On Debian / Ubuntu based systems the requirements can be installed with the following commands:  
sudo apt-get install python-numpy python-opencv  
Please check the [Kivy Website](http://kivy.org) for Kivy installation instructions.  

### Optional for video recording
* For high resolution video it is best practice to use the OpenCV based image sequence recording instead of scikit-video.
* [Scikit-Video](http://www.scikit-video.org) This library is needed as a workaround for a video recording bug in Linux OpenCV 2.4.  
sudo pip install sk-video  

### If you are using the Mouse, OSC or STSpilot actuators
* requests (sudo apt-get instal python-requests)
* liblo (sudo apt-get instal python-liblo)
* pyautogui (sudo pip install pyautogui)


## Usage
Installation: Clone or download PyFSPro from [Github](https://github.com/mark-orion/PyFSPro)  
Run the program: python PyFSPro.py  
Or alternatively python2/python3 PyFSPro.py  

## Graphical User Interface
The GUI is divided in five main sections:
* Top bar - controls the core image processing routine.
* Bottom bar - generic controls.
* Middle area - video displays (movable and resizeable with mouse or touch screen).
* Left bar - input and pre processing chain.
* Right bar - output and post processing chain.

## Description of GUI control elements
* Input / Output - show / hide input or output video.
* \> - control video processing: \> Play and Loop through video file, \>\|\| Play and Pause at end, \|\| Pause. The pause option will pause the entire system (input, processing, output). Looping and pausing at end are not working with a camera as input source.
* Proc-OFF - choose processing mode (OFF, AVG, DIFF, CUM-Z).  
AVG: Average of whole stack. DIFF: Frame - Darkframe. CUM-Z: Cumulative sum of Z-Scores.  
* Dark-OFF - choose darkframe mode for DIFF and CUMSUM (OFF, DynDark, Static, Grey). DynDark uses rolling average and Static uses the current frame as dark frame.
* Reset - resets all gain and offset settings to default values. Resets cumulative summing when in CUMSUM mode.
* TR-OFF - Transient Filter (OFF, Rising Intensity Slope, Falling Intensity Slope).
* The top slider sets the sensitivity of the vector output or the triggerlevel in transient mode.
* The bottom slider sets the stack size. The number of frames is displayed to the right. It turns green when the stack is full and rolling.
* X / Y - flip image around X or Y axis.
* GREY - click to change color palette from greyscale to pseudo color.
* EQ-OFF - choose equalization mode (Histogram or CLAHE - Contrast Limited Adaptive Histogram Equalization).
* Denoise - denoising filter (very CPU intensive!).
* FLT-OFF - choose convolution filter kernel defined in filters.py.
* LOCK - experimental image stabilizer.
* G, O, Auto - the sliders set Gain and Offset (contrast, brightness). Auto finds the optimum values for best dynamic resolution.
* Blur - toggle blurring.
* Hist - show input or output histogram (useful for camera adjustment).
* BW - choose channel from various color spaces or LSB mask for random number generation (BW = Greyscale, R, G, B, H, S, V, Y, Cr, Cb, RND, RNDX).  
RND returns LSB * 127  
RNDX works like RND but the output is XOR masked with a "chequerboard" array of ones and zeroes. In order to reduce bias, an inverted array is used for every second frame.    
* Save Config - save current configuration. The default save location is ./output/ and can be changed with the -od / --output_dir option.
* Rec-Off - save the output stream as video or image sequence. The default save location is ./output/ and can be changed with the -od / --output_dir option.
* HUD - Show vectorscope marker on the screen.
* Data Output (1) - Enable vector data processing. (1) = Joystick / Gamepad button 1.
* Zero Output (2) - Center vectorscope marker on screen.
* Joystick Override (3) - Allow Joystick to control vector output.
* Actuator Paused (4) - Enable Actuator.
* OSD - (enabled by default) show / hide control bars.

## Working with different configurations
A snapshot of the current configuration can be saved by pressing the "Save Config" button. The timestamped configuration file will be saved in the ./output/ directory  
or any folder defined via the -od / --output_dir command line option.  
Use the -c / --config_file option to load a configuration file on startup.  
Additional command line options can be used to override the ones specified in the configuration file.

## Files and Folders in the build directory
* PyFSPro.py - the main program.
* framestacker.py - frame stacker module for the main processing operation.
* filters.py - contains the convolution kernels used in the input and output filters. Custom kernels can be added to this file!
* videosource.py - manages video input from camera, videofile or image sequence.
* actuators.py - actuator classes that allow the application to interact with the outside world. The default 'Paint' actuator uses the vector data to draw a line on the screen. The line color depends on the generic brightness of the output image.
* config.py - default configuration and config load / save functionality.
* output - default directory to store images, videos and settings files.
* doc - various documents: Dataflow graph, schlieren background patterns etc.
* cli - contains the command line only (non Kivy) version of PyFSPro.

## Important command line arguments and parameters
Run 'python PyFSPro.py --help' for a full list of command line options.  
* INPUT_SOURCE
 * name of the opened video file (eg. video.avi) or image sequence (eg. img_%02d.jpg, which will read samples like img_00.jpg, img_01.jpg, img_02.jpg, ...).
 * device-id of the opened video capturing device (i.e. a camera index). If there is a single camera connected, just pass 0.
 * PICAMERA to use a RaspberryPi camera.


Mark Dammer, Forres, Scotland 2019
