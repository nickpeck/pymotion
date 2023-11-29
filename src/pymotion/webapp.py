import os
import cherrypy

from . motionsensor import MotionSensor

class PyMotionWeb:

    def __init__(self, motionsensor: MotionSensor):
        self.motionsensor = motionsensor

    @cherrypy.expose
    def index(self):
        return self._main_content()

    def _main_content(self):
        banner = 'The camera is running'
        action =  '<a href="/suspend">Suspend</a>'
        if not self.motionsensor.is_running:
            banner = 'The camera has been suspended'
            action = '<a href="/resume">Resume</a>'
        archived = self._get_archived_image_links()
        return f"""
            <div>
            <p style="color:red;">{banner}</p>
            <h1>Motion Sensor</h1>
            <p>{action}<p>
            <h2> Latest Images </h2>
            <img width=300 src="/static/ImageA.bmp"/>
            <img width=300 src="/static/ImageB.bmp"/>
            <h2> Archived Images </h2>
            <ul>
                {archived}
            <ul>
            </div>
        """

    def _get_archived_image_links(self):
        files = []
        for _dir in os.listdir(self.motionsensor.config.archiveDirectory):
            if not os.path.isdir(os.path.join(self.motionsensor.config.archiveDirectory, _dir)):
                continue
            for image in os.listdir(os.path.join(self.motionsensor.config.archiveDirectory, _dir)):
                files.append(f'<li><a href="/static/{_dir}/{image}" target="_blank"/>{_dir}/{image}</li>'.format(_dir, image))
        return "".join(files)

    @cherrypy.expose
    def suspend(self):
        self.motionsensor.suspend()
        return self._main_content()

    @cherrypy.expose
    def resume(self):
        self.motionsensor.resume()
        return self._main_content()
