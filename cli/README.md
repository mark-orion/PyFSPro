# PyFSPro - Python Frame Sequence Processor
Multi purpose realtime frame sequence and video processor for a wide range of applications including:
* [Schlieren Videography](https://hackaday.io/project/9034-schlieren-videography) using the Moiré-effect.
* Realtime Astronomical video processing for live presentations.
* Software image intensifier (night vision).
* Weak video signal detection and enhancement.
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
* Parameters can be set through command line options and configuration files.
* Most Parameters can be changed on the fly via keyboard shortcuts.
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
* Numpy (tested with version 1.11)
* OpenCV with Python bindings (tested with version 2.4.9)  
On Debian / Ubuntu based systems the requirements can be installed with the following commands:  
sudo apt-get install python-numpy python-opencv

## Optional for video recording
* For high resolution video it is best practice to use the OpenCV based image sequence recording instead of scikit-video.
* [Scikit-Video](http://www.scikit-video.org) This library is needed as a workaround for a video recording bug in Linux OpenCV 2.4.  
sudo pip install sk-video

## Usage
Installation: Clone or download PyFSPro  
Run the program: python PyFSPro.py  
Press the 'h' key for a list of keyboard shortcuts in the terminal window.

## Working with different configurations
Pressing 's' saves the current configuration to a config file in this format:  
SavedSettings-[DATE-TIME].conf  
Pressing 'S' reloads the last saved configuration or 'default.conf' if this file exists and no configuration was saved before.
python PyFSPro.py -c CONFIGFILE loads configuration CONFIGFILE. Settings defined by additional command line arguments  
will be used instead of the settings defined in the configuration file.

## Files and Folders in the build directory
* PyFSPro.py - the main program.
* framestacker.py - frame stacker module for the main processing operation.
* filters.py - contains the convolution kernels used in the input and output filters. Custom kernels can be added to this file!
* videosource.py - manages video input from camera, videofile or image sequence.
* videosource_pi.py - video input for Raspberry Pi camera module.
* config.py - default configuration and config load / save functionality.
* output - default directory to store images, videos and screenshots.
* settings - some example configurations.
* doc - various documents: Dataflow graph, schlieren background patterns etc.

## Important command line arguments and parameters
Run 'python PyFSPro.py --help' for a full list of command line options.  
* INPUT_SOURCE
 * name of the opened video file (eg. video.avi) or image sequence (eg. img_%02d.jpg, which will read samples like img_00.jpg, img_01.jpg, img_02.jpg, ...).
 * device-id of the opened video capturing device (i.e. a camera index). If there is a single camera connected, just pass 0.
* INPUT_MODE: 0 = Input Video & Status Screen, 1 = Status Screen, 2 = Input Video.
* PROCESSING_MODE: 0 = Passthrough, 1 = Rolling Average, 2 = Difference, 3 = Cumulative Deviation.
* OUTPUT_MODE: 0 = Output Video, 1 = Vectorscope, 2 = Both.
* COLOR_MODE: Color palette for Output Video. 0-11 OpenCV color palettes, 12 Grayscale.
* PATTERN_TYPE: Pattern for Schlieren Videography Pattern Generator. 1 = Chequerboard, 2 = Horizontal Stripes, 3 = Vertical Stripes.

## Keyboard Shortcuts
lower/UPPER case = apply to input/OUTPUT processing chain.
* a/A  Auto adjust offset and gain
* b/B  Blur
* c    Cycle Color Palettes
* d    Toggle Dark Frame mode (Rolling Average / Fixed)
* e/E  Cycle Equalizer modes (OFF, HIST, CLAHE)
* f/F  Cycle Filters defined in filters.py
* h    Show this help text
* i/I  Toggle image stabilizer
* l    Toggle input video looping
* m    Cycle Input Modes (BOTH, STATUS, IMAGE)
* M    Cycle Output Modes (IMAGE, VECTOR, BOTH)
* n/N  Denoise
* p    Cycle Processing Modes (OFF, AVG, DIFF, CUMDEV)
* q    Terminate Program
* r    Reset Cumulative Summing
* R    Reset Gains and Offsets
* s    Save configuration
* S    Load saved configuration
* v    Toggle video recording (requires scikit-video)
* V    Toggle image sequence recording
* ?    Cycle Schlieren pattern types
* <>   Decrease / Increase Schlieren pattern size
* x    Flip image around X axis
* y    Flip image around Y axis
* [/]  Decrease / Increase Input Gain
* {/}  Decrease / Increase Output Gain
* -/+  Decrease / Increase Input Filter Strength
* _/=  Decrease / Increase Output Filter Strength
* SPACE create Screenshot
* 1-9  Set No. of frames in Stack

Mark Dammer, Forres, Scotland 2017
