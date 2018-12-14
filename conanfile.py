from conans import ConanFile, CMake, tools, Meson
from conanos.build import config_scheme
import os, shutil

class LibsoupConan(ConanFile):
    name = "libsoup"
    version = "2.65.1"
    description = "The libsoup is a HTTP client/server library for GNOME"
    url = "https://github.com/conanos/libsoup"
    homepage = "https://developer.gnome.org/libsoup/stable/"
    license = "LGPL-2+"
    exports = ["COPYING"]
    exports_sources = ["soup-session.c"]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    #requires = ("libxml2/2.9.8@conanos/dev", "glib/2.58.0@conanos/dev",
    #            "glib-networking/2.58.0@conanos/dev","sqlite3/3.21.0@conanos/dev",
    #            "libffi/3.3-rc0@conanos/dev","gobject-introspection/1.58.0@conanos/dev",)

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def requirements(self):
        self.requires.add("glib/2.58.1@conanos/stable")
        self.requires.add("libffi/3.299999@conanos/stable")
        self.requires.add("libpsl/0.20.2@conanos/stable")
        self.requires.add("sqlite3/3.21.0@conanos/stable")
        self.requires.add("libxml2/2.9.8@conanos/stable")

    def build_requirements(self):
        self.build_requires("zlib/1.2.11@conanos/stable")
        self.build_requires("libiconv/1.15@conanos/stable")

    def source(self):
        url_ = "https://github.com/GNOME/libsoup/archive/{version}.tar.gz".format(version=self.version)
        tools.get(url_)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        if self.settings.os == 'Windows':
            shutil.copy2(os.path.join(self.source_folder,"soup-session.c"), os.path.join(self.source_folder,self._source_subfolder,"libsoup","soup-session.c"))

    def build(self):
        pkg_config_paths=[ os.path.join(self.deps_cpp_info[i].rootpath, "lib", "pkgconfig") for i in ["glib","libffi","libpsl","zlib","sqlite3","libxml2"] ]
        prefix = os.path.join(self.build_folder, self._build_subfolder, "install")
        defs = {'prefix' : prefix, "gnome" : "false", "introspection":"false","gssapi":"false","vapi":"false","tests":"false"}
        if self.settings.os == "Linux":
            defs.update({'libdir':'lib'})
        
        binpath=[ os.path.join(self.deps_cpp_info[i].rootpath, "bin") for i in ["glib","libffi"] ]
        include = [ os.path.join(self.deps_cpp_info["libxml2"].rootpath, "include", "libxml2"),
                    os.path.join(self.deps_cpp_info["libiconv"].rootpath, "include")  ]
        meson = Meson(self)
        if self.settings.os == 'Windows':
            with tools.environment_append({
                "INCLUDE" : os.pathsep.join(include + [os.getenv('INCLUDE')]),
                'PATH' : os.pathsep.join(binpath + [os.getenv('PATH')]),
                }):
                meson.configure(defs=defs,source_dir=self._source_subfolder, build_dir=self._build_subfolder,pkg_config_paths=pkg_config_paths)
                meson.build()
                self.run('ninja -C {0} install'.format(meson.build_dir))

    def package(self):
        self.copy("*", dst=self.package_folder, src=os.path.join(self.build_folder,self._build_subfolder, "install"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

