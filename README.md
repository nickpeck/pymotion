# pymotion
A simple, lightweight motion sensor intended to be left running on a laptop or raspberry pi with a USB webcam.

The sensor snaps two camera images at a specified interval and compares the difference between these in order to determine if motion is occuring.

The web ui is extremely simple, but sufficient given that I might often want to access quickly via a VPN/cellphone.

## Usage
For portability this is intended to be distributed via Docker image. To build:
~~~
docker build -t pymotion .
~~~
If you want to override any settings, create a file called pymotion.yaml (see pymotion.yaml.sample for example).

In the following, be sure to set --device to the device file representing your camera.
The directory .archive/ can be any folder on the container host where you want to store your images.
Expose the correct host web ports that you wish to view the admin UI on.
~~~
docker run \
--device /dev/video0 \
--mount type=bind,source=$(pwd)/pymotion.yaml,target=/usr/src/app/pymotion.yaml \
-v $(pwd)/archive:/usr/src/app/archive \ 
-p 127.0.0.1:8080:8080 \
pymotion
~~~

The web UI can then be viewed at http://127.0.0.1:8080

## TODO
- publish docker image
- protect web ui via basic auth
- Add Some simple modules to broadcast an alert via SNS/SES etc...
