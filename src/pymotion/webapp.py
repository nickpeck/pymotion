import os
import cherrypy

from . motionsensor import MotionSensor, ARCHIVE_DIR

class PyMotionWeb:

    def __init__(self, motionsensor: MotionSensor):
        self.motionsensor = motionsensor

    @cherrypy.expose
    def index(self):
        return self._main_content()

    def static(self):
        pass

    static._cp_config={
        "tools.staticdir.on" : True,
        "tools.staticdir.dir": "/usr/src/app/archive"
    }

    def _main_content(self):
        banner = 'The camera is running'
        action =  '<a href="/suspend">Suspend</a>'
        if not self.motionsensor.is_running:
            banner = 'The camera has been suspended'
            action = '<a href="/resume">Resume</a>'
        archived = self._get_archived_image_links()
        return f"""
            <!DOCTYPE html>
            <html>
            <meta charset="UTF-8">
            <title>PyMotion</title>
            </meta
            <body>
            <div>
            <h1>Motion Sensor</h1>
            <p style="color:red;">{banner}</p>
            <p>{action}<p>
            <h2> Latest Images </h2>
            <img width=300 src="/static/ImageA.bmp"/>
            <img width=300 src="/static/ImageB.bmp"/>
            <h2> Archived Images </h2>
            <ul>
                {archived}
            <ul>
            </div>
            </body>
            </html>
        """

    def _get_archived_image_links(self):
        files = []
        for _dir in os.listdir("archive"):
            if not os.path.isdir(os.path.join(ARCHIVE_DIR, _dir)):
                continue
            for image in os.listdir(os.path.join(ARCHIVE_DIR, _dir)):
                files.append(f'<li><a href="/static/{_dir}/{image}" target="_blank"/>{_dir}/{image}</li>'.format(_dir, image))
        return "".join(files)

    @cherrypy.expose
    def suspend(self):
        self.motionsensor.suspend()
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def resume(self):
        self.motionsensor.resume()
        raise cherrypy.HTTPRedirect('/')
