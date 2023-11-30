# pymotion
A simple, lightweight motion sensor intended to be left running on a laptop or raspberry pi with a USB webcam.

You can extend the app by writing simple plugin scripts (for example, to send an SMS, or contact an API endpoint).

The sensor snaps two camera images at a specified interval and compares the difference between these in order to determine if motion is occuring.

The web ui is extremely simple, but sufficient given that I might often want to access quickly via a VPN/cellphone.

## Usage
For portability this is intended to be distributed via Docker image. To build:
~~~
docker build -t pymotion .
~~~
If you want to override any settings, create a file called pymotion.yaml (see pymotion.yaml.sample for example).

In the following, be sure to set --device to the device file representing your camera.

The directory archive/ can be any folder on the container host where you want to store your images.

The directory plugins/ is optional, but should contain your own plugin scripts, defining hook points for your custom actions (see plugins/sampleplugin.py for an example).

Expose the correct host web ports that you wish to view the admin UI on.
~~~
docker run \
--device /dev/video0 \
--mount type=bind,source=$(pwd)/pymotion.yaml,target=/usr/src/app/pymotion.yaml \
-v $(pwd)/archive:/usr/src/app/archive \
-v $(pwd)/plugins:/usr/src/app/plugins \ 
-p 127.0.0.1:8080:8080 \
pymotion
~~~

(*) A plugin will only be loaded, if there is an entry in your pymotion.yaml. e.g for plugins\sampleplugin.py

~~~
plugins:
    sampleplugin:
        ...define key/value pairs here, as required
~~~

(**) If you intent to use the sns or ses plugins, you will need to create an IAM Role and specify the appropriate environment variables for the IAM role in your run commmand:
~~~
-e AWS_ACCESS_KEY_ID=********** -e AWS_SECRET_ACCESS_KEY=********** -e AWS_DEFAULT_REGION=**********
~~~

The web UI can then be viewed at http://127.0.0.1:8080

## TODO
- publish docker image
