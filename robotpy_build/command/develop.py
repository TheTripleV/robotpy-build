from os.path import abspath
from setuptools.command.develop import develop


class Develop(develop):
    def run(self):

        print("DEVELOP run mid")

        self.distribution.rpybuild_develop_path = abspath(self.egg_base)
        develop.run(self)

        print("DEVELOP run exit")

        # if not uninstall, perform fixups on OSX?
