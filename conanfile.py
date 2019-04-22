from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class CairoConan(ConanFile):
    name = "cairo"
    version = "1.16.0"
    license = ("LGPL-2.1", "MPL-1.1")
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Cairo here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "png": [True, False],
        "svg": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "png": False,
        "svg": False,
    }
    requires = (
        "pixman/0.38.0@bincrafters/stable"
    )
    source_subfolder = "cairo-{version}".format(version=version)

    def source(self):
        url = "https://cairographics.org/releases/cairo-{version}.tar.xz".format(version=self.version)
        tools.get(url)

    def build(self):
        with tools.chdir(self.source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build.pic = self.options.fPIC
            def yes_no(b):
                return "yes" if b else "no"
            args = [
                "--enable-shared={}".format(yes_no(self.options.shared)),
                "--enable-static={}".format(yes_no(not self.options.shared)),
                "--enable-png={}".format(yes_no(self.options.png)),
                "--enable-svg={}".format(yes_no(self.options.svg)),
            ]
            vars = env_build.vars
            vars["PKG_CONFIG_PIXMAN_0_38_0_PREFIX"] = self.deps_cpp_info["pixman"].rootpath
            vars["PKG_CONFIG_PATH"] = os.path.join(self.deps_cpp_info["pixman"].rootpath, "lib", "pkgconfig")
            print(vars)
            env_build.configure(args=args, vars=vars)
            env_build.make()
            env_build.install()

    def package(self):
        self.copy("*.h", dst="include", src="hello")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["cairo"]

