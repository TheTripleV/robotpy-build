import os
from os.path import abspath, exists, join
from setuptools import find_packages, setup as _setup
from setuptools_scm import get_version
import toml

from .command.build_dl import BuildDl
from .command.build_gen import BuildGen
from .command.build_ext import BuildExt

from .configs import RobotpyBuildConfig
from .pkgcfg_provider import PkgCfgProvider
from .platforms import get_platform
from .wrapper import Wrapper


class Setup:
    """
        Hacky wrapper around setuptools because it's easier than copy/pasting
        this stuff to a million setup.py files
    """

    def __init__(self):
        self.root = abspath(os.getcwd())
        self.wrappers = []

        with open(join(self.root, "pyproject.toml")) as fp:
            self.pyproject = toml.load(fp)

        self.project_dict = self.pyproject.get("tool", {}).get("robotpy-build", {})
        try:
            self.project = RobotpyBuildConfig(**self.project_dict)
        except Exception as e:
            raise ValueError(
                f"robotpy-build configuration in pyproject.toml is incorrect"
            ) from e

        self.platform = get_platform()

    @property
    def base_package(self):
        return self.project.base_package

    @property
    def git_dir(self):
        return join(self.root, ".git")

    def prepare(self):

        self.setup_kwargs = self.project_dict.get("metadata", {})
        self.setup_kwargs["zip_safe"] = False
        self.setup_kwargs["include_package_data"] = True
        self.setup_kwargs["requires_python"] = ">=3.6"

        # TODO: autogen packages don't exist at sdist time
        #       ... but we want them to be added to the wheel
        self.setup_kwargs["packages"] = find_packages()

        self.setup_kwargs["long_description"] = self._generate_long_description()

        self.setup_kwargs["version"] = get_version(
            write_to=join(self.base_package, "version.py"), fallback_version="master"
        )

        self.pkgcfg = PkgCfgProvider()

        self._collect_wrappers()

        self.setup_kwargs["cmdclass"] = {
            "build_dl": BuildDl,
            "build_gen": BuildGen,
            "build_ext": BuildExt,
        }
        for cls in self.setup_kwargs["cmdclass"].values():
            cls.wrappers = self.wrappers

    def _generate_long_description(self):
        readme_rst = join(self.root, "README.rst")
        if exists(readme_rst):
            with open(readme_rst) as fp:
                return fp.read()

    def _collect_wrappers(self):

        ext_modules = []

        for name, cfg in self.project.wrappers.items():
            w = Wrapper(name, cfg, self)
            self.wrappers.append(w)
            self.pkgcfg.add_pkg(w)

            if w.extension:
                ext_modules.append(w.extension)

        if ext_modules:
            self.setup_kwargs["ext_modules"] = ext_modules

    def run(self):
        # assemble all the pieces and make it work
        _setup(**self.setup_kwargs)


def setup():
    s = Setup()
    s.prepare()
    s.run()
