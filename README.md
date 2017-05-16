# PyFSPro - Python Frame Sequence Processor
Multi purpose realtime frame sequence and video processor for a wide range of applications including:
* [Schlieren Videography](https://hackaday.io/project/9034-schlieren-videography) using the Moiré-effect.
* Realtime Astronomical video processing for live presentations.
* Software image intensifier (night vision).
* Weak video signal detection and enhancement.
This is the GUI version of PyFSPro with a Kivy based graphical user interface.  
The older command line only (non Kivy) version of PyFSPro can be found in the 'cli' folder.
More information and and a dataflow diagram can be found in the [PyFSPro Wiki](https://github.com/mark-orion/PyFSPro/wiki)  
The 'doc' folder contains the flow diagram and pattern files that can be used instead of the built-in pattern generator.

## Main features
* Resizable ring buffer for image "stacking".
* High accuracy processing core using floating point maths for image processing.
* Input from Camera, Image sequence or Video file.
* Output to Screen, Image sequence or Video file.
* Input and Output processing chains with basic image enhancement functions.
* Vectorscope for the visualization of small changes in video stream.
* Built-in pattern generator for Schlieren Videography.
* Parameters can be set through the UI, command line options and configuration files.
* Most Parameters can be changed on the fly via the Kivy user interface.
* framestacker.py library can be re-used in other projects. It does not depend on OpenCV and only requires Numpy.

## Image enhancement and analysis functions
* Image integration (rolling average)
* Image difference to fixed reference (dark) frame or rolling average.
* Cumulative deviation of stacked images.
* Convolution filters with customizable kernels.
* Image stabilizer (experimental)
* Automatic or manual gain and offset
* Histogram Equalization
* Contrast Limited Adaptive Histogram Equalization (CLAHE)
* Blurring
* DeNoising
* Pseudo Color

## Requirements
* Tested with Python 2.7, not ported to Python 3 yet!
* Kivy (tested with version 1.9.1)
* Numpy (tested with version 1.11)
* OpenCV with Python bindings (tested with version 2.4.9)
* [Scikit-Video](http://www.scikit-video.org) This library is needed as a workaround for a video recording bug in Linux OpenCV 2.4.  
On Debian / Ubuntu based systems the requirements can be installed with the following commands:  
sudo apt-get install python-numpy python-opencv  
sudo pip install sk-video
Please check the [Kivy Website](http://kivy.org) for Kivy installation instructions

## Usage
Installation: Clone or download PyFSPro  
Run the program: python PyFSPro.py  

## Graphical User Interface
The GUI is divided in five main sections:
* Top bar - controls the core image processing routine.
* Bottom bar - generic controls.
* Middle area - video displays (movable and resizeable with mouse or touch screen).
* Left bar - input and pre processing chain.
* Right bar - output and post processing chain.

## Description of GUI control elements
* Input / Output - show / hide input or output video
* PROC-OFF - choose processing mode (AVG, DIFF, CUMSUM)
* DynDark - (enabled by default) use stack average as dark frame for DIFF and CUMSUM. The moment the button gets disabled, the current frame will be used as fixed dark frame.
* Reset - resets all gain and offset settings to default values. Resets cumulative summing when in CUMSUM mode.
* The top slider sets the stack size. The number of frames is displayed to the right. It turns green when the stack is full and rolling.
* X / Y - flip image around X or Y axis.
* GREY - click to change color palette.
* EQ-OFF - choose equalization mode (Histogram or CLAHE - Contrast Limited Adaptive Histogram Equalization).
* FLT-OFF - choose convolution filter kernel defined in filters.py.
* LOCK - experimental image stabilizer.
* Blur, Denoise - toggle blurring and denoising.
* G, O, Auto - the sliders set Gain and Offset (contrast, brightness). Auto finds the optimum values for best dynamic resolution.
* > - (enabled by default) run / pause processing engine.
* Loop - loop inpu video if loaded from file.
* S - save current output frame as single image.
* RV - Record Video saves the output stream to AVI video.
* RI - Record Image Sequence saves the output stream as bmp image sequence.
* VEC - Vectorscope overlay of mean intesity over XY axis.
* ? - show dataflow diagram.
* OSD - (enabled by default) show / hide control bars.

## Working with different configurations
todo

## Files and Folders in the build directory
* PyFSPro.py - the main program.
* framestacker.py - frame stacker module for the main processing operation.
* filters.py - contains the convolution kernels used in the input and output filters. Custom kernels can be added to this file!
* videosource.py - manages video input from camera, videofile or image sequence.
* videosource_pi.py - video input for Raspberry Pi camera module.
* config.py - default configuration and config load / save functionality.
* output - default directory to store images, videos and screenshots.
* doc - various documents: Dataflow graph, schlieren background patterns etc.
* cli - contains the command line only (non Kivy) version of PyFSPro.

## Important command line arguments and parameters
Run 'python PyFSPro.py - --help' for a full list of command line options.  
* INPUT_SOURCE
 * name of the opened video file (eg. video.avi) or image sequence (eg. img_%02d.jpg, which will read samples like img_00.jpg, img_01.jpg, img_02.jpg, ...).
 * device-id of the opened video capturing device (i.e. a camera index). If there is a single camera connected, just pass 0.
* COLOR_MODE, INPUT_EQUALIZE, OUTPUT_EQUALIZE, INPUT_FILTER, OUTPUT_FILTER and PROCESSING_MODE are now taking string arguments that are equivalent to the choices offered for these parameters in the GUI.

Mark Dammer, Forres, Scotland 2017
