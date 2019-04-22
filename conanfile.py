from conans import ConanFile, AutoToolsBuildEnvironment, tools
import glob
import os
import shutil


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

    def build_requirements(self):
        if self.settings.os == 'Windows':
            self.build_requires('msys2_installer/20161025@bincrafters/stable')

    def requirements(self):
        if self.options.png:
            self.requires.add('libpng/1.6.36@bincrafters/stable')
    
    def source(self):
        url = "https://cairographics.org/releases/cairo-{version}.tar.xz".format(version=self.version)
        tools.get(url)

    def build(self):
        if self.settings.os == "Windows":
            cfg = str(self.settings.build_type).lower()
            pixman_includedir = "pixman/pixman"
            pixman_libdir = "pixman/pixman/%s" % cfg
            os.makedirs(pixman_libdir)
            h_files = glob.glob('%s/include/pixman-1/*.h' % self.deps_cpp_info["pixman"].rootpath)
            for x in h_files:
                shutil.copy(x, pixman_includedir)
            lib_files = glob.glob('%s/lib/*.lib' % self.deps_cpp_info["pixman"].rootpath)
            for x in lib_files:
                shutil.copy(x, pixman_libdir)

            with tools.chdir(self.source_subfolder):
                features = "build/Makefile.win32.features"
                tools.replace_in_file(features, "CAIRO_HAS_PDF_SURFACE=1", "CAIRO_HAS_PDF_SURFACE=0")
                tools.replace_in_file(features, "CAIRO_HAS_PS_SURFACE=1", "CAIRO_HAS_PS_SURFACE=0")
                tools.replace_in_file(features, "CAIRO_HAS_SCRIPT_SURFACE=1", "CAIRO_HAS_SCRIPT_SURFACE=0")
                if self.options.png:
                    #TODO
                    pass
                else:
                    tools.replace_in_file(features, "CAIRO_HAS_PNG_FUNCTIONS=1", "CAIRO_HAS_PNG_FUNCTIONS=0")
                if self.options.svg:
                    #TODO
                    pass
                else:
                    tools.replace_in_file(features, "CAIRO_HAS_SVG_SURFACE=1", "CAIRO_HAS_SVG_SURFACE=0")

                with tools.vcvars(self.settings):
                    self.run("make -f Makefile.win32 CFG={cfg}".format(cfg=cfg))
        else:
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
                env_vars = env_build.vars
                pkg_config_paths = [os.path.join(self.deps_cpp_info["pixman"].rootpath, "lib", "pkgconfig")]
                if self.options.png:
                    pkg_config_paths.append(os.path.join(self.deps_cpp_info["libpng"].rootpath, "lib", "pkgconfig"))
                env_vars["PKG_CONFIG_PATH"] = ":".join(pkg_config_paths)
                env_build.configure(args=args, vars=env_vars)
                env_build.make()
                env_build.install()

    def package(self):
        if self.settings.os == "Windows":
            h_files = [
                "cairo-version.h",
                "src/cairo-features.h",
                "src/cairo.h",
                "src/cairo-deprecated.h",
                "src/cairo-win32.h",
            ]
            for x in h_files:
                self.copy(x, dst="include/cairo", src=self.source_subfolder, keep_path=False)
            self.copy("*.lib", dst="lib", src=self.source_subfolder, keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.libs = ["cairo"]
            else:
                self.cpp_info.libs = ["cairo-static"]
        self.cpp_info.libs = ["cairo"]

