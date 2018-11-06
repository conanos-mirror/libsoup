from conans import ConanFile, CMake, tools, Meson
import os

class LibsoupConan(ConanFile):
    name = "libsoup"
    version = "2.62.3"
    description = "The libsoup is a HTTP client/server library for GNOME"
    url = "https://github.com/conanos/libsoup"
    homepage = "https://developer.gnome.org/libsoup/stable/"
    license = "LGPLv2Plus"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = ("libxml2/2.9.8@conanos/dev", "glib/2.58.0@conanos/dev",
                "glib-networking/2.58.0@conanos/dev","sqlite3/3.21.0@conanos/dev",
                "libffi/3.3-rc0@conanos/dev","gobject-introspection/1.58.0@conanos/dev",)

    source_subfolder = "source_subfolder"

    def source(self):
        maj_ver = '.'.join(self.version.split('.')[0:2])
        tarball_name = '{name}-{version}.tar'.format(name=self.name, version=self.version)
        archive_name = '%s.xz' % tarball_name
        url_ = 'http://ftp.gnome.org/pub/gnome/sources/libsoup/{0}/{1}'.format(maj_ver,archive_name)
        tools.download(url_, archive_name)
        
        if self.settings.os == 'Windows':
            self.run('7z x %s' % archive_name)
            self.run('7z x %s' % tarball_name)
            os.unlink(tarball_name)
        else:
            self.run('tar -xJf %s' % archive_name)
        os.rename('%s-%s' %( self.name, self.version), self.source_subfolder)
        os.unlink(archive_name)

    def build(self):
        with tools.chdir(self.source_subfolder):
            with tools.environment_append({
                'PKG_CONFIG_PATH' : "%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig:%s/lib/pkgconfig"
                %(self.deps_cpp_info["libxml2"].rootpath,
                self.deps_cpp_info["glib"].rootpath,
                self.deps_cpp_info["glib-networking"].rootpath,
                self.deps_cpp_info["sqlite3"].rootpath,
                self.deps_cpp_info["libffi"].rootpath,
                self.deps_cpp_info["gobject-introspection"].rootpath,),
                'LD_LIBRARY_PATH' : "%s/lib:%s/lib"%(self.deps_cpp_info["libffi"].rootpath,self.deps_cpp_info["sqlite3"].rootpath),
                'LDFLAGS' : "-L%s/lib/gio/modules"%(self.deps_cpp_info["glib-networking"].rootpath),
                'LIBS' : "-lgiognutls"
                }):

                #self.run("gtkdocize && intltoolize --automake --copy && autoreconf --force --install --verbose")
                _args = ["--prefix=%s/builddir"%(os.getcwd()), '--libdir=%s/builddir/lib'%(os.getcwd()) ,
                         "--enable-introspection", "--without-gnome", "--disable-vala", "-with-gssapi=no",
                         "--disable-more-warnings", "--disable-always-build-tests", "--disable-glibtest", 
                         "--disable-installed-tests"]

                if self.options.shared:
                    _args.extend(['--enable-shared=yes','--enable-static=no'])
                else:
                    _args.extend(['--enable-shared=no','--enable-static=yes'])
                
                self.run('./configure %s'%(' '.join(_args)))#space
                self.run('make -j4')
                self.run('make install')

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

