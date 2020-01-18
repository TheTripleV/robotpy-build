from setuptools.command.build_py import build_py


class BuildPy(build_py):

    wrappers = []

    def run(self):

        print("BUILDPY run enter")

        # files need to be generated before building can occur
        # -> otherwise they're not included in the bdist
        self.run_command("build_gen")

        # Add the generated files to the package data
        for package, _, _, filenames in self.data_files:
            for wrapper in self.wrappers:
                if wrapper.package_name == package:
                    filenames.extend(wrapper.generated_files)
                    break

        print("BUILDPY run mid")

        build_py.run(self)

        print("BUILDPY run exit")
