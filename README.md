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
* Pre- and Postprocessing chains with basic image enhancement functions.
* Vectorscope for the visualization of small changes in video stream.
* Built-in pattern generator for Schlieren Videography.
* Parameters can be set through command line options.
* Most Parameters can be changed on the fly via keyboard shortcuts.
* framestacker.py library can be re-used in other projects. It does not depend on OpenCV and only requires Numpy.

## Image enhancement and analysis functions
* Image integration (rolling average)
* Image difference to fixed reference (dark) frame or rolling average
* Cumulative deviation of stacked images
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
* [Scikit-Video](http://www.scikit-video.org) This library is needed as a workaround for a video recording bug in Linux OpenCV 2.4.  
On Debian / Ubuntu based systems the requirements can be installed with the following commands:  
sudo apt-get install python-numpy python-opencv  
sudo pip install sk-video

## Usage
Installation: Clone or download PyFSPro  
Run the program: python PyFSPro.py  
Press the 'h' key for a list of keyboard shortcuts in the terminal window.  

## Important command line arguments and parameters
Run 'python PyFSPro.py --help' for a full list of command line options.  
* INPUT_SOURCE
 * name of the opened video file (eg. video.avi) or image sequence (eg. img_%02d.jpg, which will read samples like img_00.jpg, img_01.jpg, img_02.jpg, ...).
 * device-id of the opened video capturing device (i.e. a camera index). If there is a single camera connected, just pass 0.
* INPUT_MODE: 0 = Input Video & Status Screen, 1 = Status Screen, 2 = Input Video.
* PROCESSING_MODE: 0 = Passthrough, 1 = Rolling Average, 2 = Difference, 3 = Cumulative Deviation.
* OUTPUT_MODE: 0 = Output Video, 1 = Vectorscope, 2 = Both.
* COLOR_MODE: Color palette for Output Video. 0-11 OpenCV color palettes, 12 Grayscale.
* PATTERN_MODE: Pattern for Schlieren Videography Pattern Generator. 1 = Chequerboard, 2 = Horizontal Stripes, 3 = Vertical Stripes.

## Keyboard Shortcuts
lower/UPPER case = apply to pre/POST processing pipeline.
* a/A  Auto adjust offset and gain
* b/B  Blur
* c    Cycle through Color Palette
* d    Toggle Dark Frame mode (Rolling Average / Fixed)
* e/E  Cycle through Equalizer modes (OFF, HIST, CLAHE)
* h    Show this help text
* i    Toggle image sequence recording
* l    Toggle input video looping
* m    Input Mode (BOTH, STATUS, IMAGE)
* M    Output Mode (IMAGE, VECTOR, BOTH)
* n/N  Denoise
* p    Processing Mode (OFF, AVG, DIFF, CUMDEV)
* q    Terminate Program
* r    Reset Cumulative Summing
* R    Reset Gains and Offsets
* s    Enable / change Schlieren pattern
* v    Toggle video recording
* <>   Decrease / Increase Schlieren pattern size
* x    Flip image around X axis
* y    Flip image around Y axis
* [/]  Decrease / Increase Input Gain
* {/}  Decrease / Increase Output Gain
* SPACE create Screenshot
* 1-9  Set No. of frames in Stack

Mark Dammer, Forres, Scotland 2017
