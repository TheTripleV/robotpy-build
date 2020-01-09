from distutils.util import get_platform as _get_platform
from dataclasses import dataclass


# wpilib platforms at https://github.com/wpilibsuite/native-utils/blob/master/src/main/java/edu/wpi/first/nativeutils/WPINativeUtilsExtension.java
@dataclass
class WPILibMavenPlatform:
    arch: str
    os: str = "linux"
    libprefix: str = "lib"

    #: runtime linkage
    libext: str = ".so"

    #: compile time linkage
    linkext: str = None

    def __post_init__(self):
        # linkext defaults to libext
        if self.linkext is None:
            self.linkext = self.libext


X86_64 = "x86-64"

# key is python platform, value is information about wpilib maven artifacts
_platforms = {
    # TODO: this isn't always true
    "linux-armv7l": WPILibMavenPlatform("athena"),
    "linux-x86_64": WPILibMavenPlatform(X86_64),
    # TODO: linuxraspbian
    "win32": WPILibMavenPlatform("x86", "windows", "", ".dll", ".lib"),
    "win-amd64": WPILibMavenPlatform(X86_64, "windows", "", ".dll", ".lib"),
    # TODO: need to filter this value
    "macosx-10.9-x86_64": WPILibMavenPlatform(X86_64, "osx", libext=".dylib"),
}


def get_platform() -> WPILibMavenPlatform:
    """
        Retrieve platform specific information
    """

    # TODO: _PYTHON_HOST_PLATFORM is used for cross builds,
    #       and is returned directly from get_platform. Might
    #       be useful to note for the future.

    pyplatform = _get_platform()
    try:
        return _platforms[pyplatform]
    except KeyError:
        raise KeyError(f"platform {pyplatform} is not supported by robotpy-build!")
