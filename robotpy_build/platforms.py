from distutils.util import get_platform as _get_platform
from dataclasses import dataclass, field
from typing import List
import re


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

    #: static linkage
    staticext: str = ".a"

    defines: List[str] = field(default_factory=list)

    def __post_init__(self):
        # linkext defaults to libext
        if self.linkext is None:
            self.linkext = self.libext
        self.defines = [f"{d} 1" for d in self.defines]


X86_64 = "x86-64"
OSX = WPILibMavenPlatform(X86_64, "osx", libext=".dylib")

# key is python platform, value is information about wpilib maven artifacts
_platforms = {
    "linux-athena": WPILibMavenPlatform("athena", defines=["__FRC_ROBORIO__"]),
    "linux-raspbian": WPILibMavenPlatform("raspbian", defines=["__RASPBIAN__"]),
    "linux-x86_64": WPILibMavenPlatform(X86_64),
    "linux-aarch64": WPILibMavenPlatform("aarch64bionic"),
    "win32": WPILibMavenPlatform("x86", "windows", "", ".dll", ".lib", ".lib"),
    "win-amd64": WPILibMavenPlatform(X86_64, "windows", "", ".dll", ".lib", ".lib"),
}


def get_platform() -> WPILibMavenPlatform:
    """
    Retrieve platform specific information
    """

    # TODO: _PYTHON_HOST_PLATFORM is used for cross builds,
    #       and is returned directly from get_platform. Might
    #       be useful to note for the future.

    pyplatform = _get_platform()

    # Check for 64 bit x86 macOS (version agnostic)
    if re.fullmatch(r"macosx-.*-x86_64", pyplatform):
        return OSX

    if pyplatform == "linux-armv7l":
        try:
            import distro

            distro_id = distro.id()

            if distro_id == "nilrt":
                pyplatform = "linux-athena"
            elif distro_id == "raspbian":
                pyplatform = "linux-raspbian"

        except Exception:
            pass

    try:
        return _platforms[pyplatform]
    except KeyError:
        raise KeyError(f"platform {pyplatform} is not supported by robotpy-build!")


def get_platform_override_keys(platform: WPILibMavenPlatform):
    # Used in places where overrides exist
    return [
        f"arch_{platform.arch}",
        f"os_{platform.os}",
        f"platform_{platform.os}_{platform.arch}",
    ]
