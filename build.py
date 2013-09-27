#!/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import *
import os
import re
import sys
import shutil

def get_stdout(cmd, *args):
    ps      = Popen((cmd,) + args, stdout=PIPE)
    stdout  = ps.communicate()[0].strip()
    retcode = ps.returncode
    if retcode == 0:
        return stdout
    else:
        sys.exit(retcode)

def get_macports_path(name):
    return get_stdout('sh', '-c', '''PATH=/opt/local/bin type -P {name}'''.format(name = name))

def vsh(script):
    ps = Popen(["sh", "-ve"], stdin=PIPE)
    ps.communicate(script)
    if ps.returncode != 0:
        sys.exit(ps.retcode)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

prefix          = "/usr/local/wine/SharedSupport"
BUILDROOT       = os.path.join(prefix, "build")
BINDIR          = os.path.join(prefix, 'bin')
SBINDIR         = os.path.join(prefix, 'sbin')
DATADIR         = os.path.join(prefix, 'share')
INCDIR          = os.path.join(prefix, 'include')
LIBDIR          = os.path.join(prefix, 'lib')
LIBEXECDIR      = os.path.join(prefix, 'libexec')
SYSCONFDIR      = os.path.join(prefix, 'etc')

W_PREFIX        = '/usr/local/wine'
W_BINDIR        = os.path.join(W_PREFIX, 'bin')
W_DATADIR       = os.path.join(W_PREFIX, 'share')
W_INCDIR        = os.path.join(W_PREFIX, 'include')
W_LIBDIR        = os.path.join(W_PREFIX, 'lib')
W_LIBEXECDIR    = os.path.join(W_PREFIX, 'libexec')

DEPOSROOT       = "/usr/local/wine_depos"
REPOSROOT       = "/usr/local/src/repos"
TARSROOT        = "/usr/local/src/tarballs"

if os.path.exists(W_PREFIX):
    shutil.rmtree(W_PREFIX)
for f in [
    DEPOSROOT,
    BUILDROOT,
    BINDIR,
    INCDIR,
    W_BINDIR,
    W_DATADIR,
    W_INCDIR,
    W_LIBDIR,
    W_LIBEXECDIR,
]:
    if not os.path.exists(f):
        os.makedirs(f)

os.symlink(W_LIBDIR, LIBDIR)



_osx_ver    = get_stdout("sw_vers", "-productVersion")[0:4]
_dev_root   = get_stdout("xcode-select", "-print-path")
_sdk_root   = Popen(["sh", "-v"], stdin=PIPE, stdout=PIPE).communicate("""\
xcodebuild -version -sdk macosx{version} | sed -n '/^Path: /s///p'
""".format(version=_osx_ver))[0].strip()



### COMPILER SETTINGS ###
_mp_ccache  = get_macports_path("ccache")
_mp_gcc     = get_macports_path("gcc-apple-4.2")
_mp_gxx     = get_macports_path("g++-apple-4.2")
_mp_clang   = get_macports_path("clang-mp-3.3")
_mp_clangxx = get_macports_path("clang++-mp-3.3")

#CCACHE      = _mp_ccache
CCACHE      = '/usr/local/bin/ccache'
GCC         = os.path.basename(_mp_gcc)
GXX         = os.path.basename(_mp_gxx)
CLANG       = os.path.basename(_mp_clang)
CLANGXX     = os.path.basename(_mp_clangxx)
GIT         = "/usr/local/git/bin/git"

os.symlink(CCACHE, os.path.join(BINDIR, GCC))
os.symlink(CCACHE, os.path.join(BINDIR, GXX))
os.symlink(CCACHE, os.path.join(BINDIR, CLANG))
os.symlink(CCACHE, os.path.join(BINDIR, CLANGXX))

os.environ["CCACHE_PATH"]     = "/opt/local/bin"
os.environ["CCACHE_DIR"]      = os.path.expanduser("~/.ccache")


### ENVIRONMENT ###
os.environ["SHELL"]             = '/bin/bash'
os.environ["TERM"]              = 'xterm'
os.environ["COMMAND_MODE"]      = 'unix2003'
os.environ["LANG"]              = 'C'
os.environ["gt_cv_locale_ja"]   = 'ja_JP.UTF-8'
os.environ["PATH"]              = ':'.join([BINDIR,
                                            os.path.dirname(GIT),
                                            '/usr/bin:/bin:/usr/sbin:/sbin',
                                          ])

ncpu        = str(int(get_stdout("sysctl", "-n", "hw.ncpu")) + 1)
arch_flags  = "-m32 -arch i386"
opt_flags   = "-O2 -march=core2 -mtune=core2"
triple      = "i686-apple-darwin" + os.uname()[2]

configure_format = dict(prefix    = prefix,
                        triple    = triple,
                        jobs      = ncpu,
                        cc        = CLANG,
                        cxx       = CLANGXX,
                        gcc       = GCC,
                        gxx       = GXX,
                        archflags = arch_flags,
                        optflags  = opt_flags,
                        sdkroot   = _sdk_root,
                        osxver    = _osx_ver,
                        incdir    = INCDIR,
                        libdir    = LIBDIR)

os.environ["MACOSX_DEPLOYMENT_TARGET"] = _osx_ver
os.environ["CC"]        = os.path.basename(GCC)
os.environ["CXX"]       = os.path.basename(GXX)
os.environ["CFLAGS"]    = "{archflags} {optflags}".format(**configure_format)
os.environ["CXXFLAGS"]  = os.getenv("CFLAGS")
os.environ["CPPFLAGS"]  = "-isysroot {sdkroot} -I{incdir}".format(**configure_format)
os.environ["LDFLAGS"]   = "\
-Wl,-search_paths_first,-headerpad_max_install_names \
-Wl,-syslibroot,{sdkroot} \
-Wl,-arch,i386 \
-L{libdir}".format(**configure_format)


def env_external_tools():
    search_target = (
        "aclocal",
        "autoconf",
        "autoheader",
        "autom4te",
        "automake",
        "autopoint",
        "autoreconf",
        "fontforge",
        "nasm",
        "yasm",
    )
    for f in search_target:
        os.environ[f.upper()] = get_macports_path(f)

    os.environ["HELP2MAN"]      = get_macports_path("help2man") # required from libtasn1
    os.environ["INSTALL"]       = get_macports_path("ginstall")
    os.environ["LIBTOOLIZE"]    = get_macports_path("glibtoolize")
    os.environ["M4"]            = get_macports_path("gm4")
    os.environ["MAKE"]          = get_macports_path("gmake")
    os.environ["ACLOCAL_PATH"]  = ":".join([os.path.join(prefix, "share", "aclocal"),
                                            os.path.join("/opt/local/share/aclocal")])
env_external_tools()

os.environ["PKG_CONFIG"]        = get_macports_path("pkg-config")
os.environ["PKG_CONFIG_LIBDIR"] = ":".join([os.path.join(prefix, "lib",   "pkgconfig"),
                                            os.path.join(prefix, "share", "pkgconfig"),
                                            "/usr/lib/pkgconfig"])

check_call(["sh", "-c", "declare"])

#---------------#
# GNU Autotools #
#---------------#
class Autotools:
    path = "/opt/local/bin:/opt/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin"

    ### autogen ###
    def autogen(self, *args):
        vsh("""
PATH={path} \
NOCONFIGURE=1 \
./autogen.sh {autogen_args}
""".format(
        path         = self.path,
        autogen_args = " ".join(args),
    ))
    
    ### autoreconf ###
    def autoreconf(self, install=True, force=False, *args):
        if install:
            args = ("-i",) + args
        if force:
            args = ("-f",) + args

        vsh("""
PATH={path} \
NOCONFIGURE=1 \
autoreconf -v {autoreconf_args}
""".format(
        path            = self.path,
        autoreconf_args = " ".join(args),
    ))

autotools  = Autotools()
autogen    = autotools.autogen
autoreconf = autotools.autoreconf


def copytree(name):
    src = os.path.join(REPOSROOT, name)
    dst = os.path.join(BUILDROOT, name)

    shutil.copytree(src, dst)
    os.chdir(dst)

def reposcopy(name):
    src = os.path.join(PROJECT_ROOT, 'src', name)
    dst = os.path.join(BUILDROOT, name)

    shutil.copytree(src, dst)
    os.chdir(dst)

configure_pre_args = (
    "--prefix=" + prefix,
    "--build="  + triple,
    "--enable-shared",
    "--disable-dependency-tracking",
)
def configure(*args, **kwargs):
    vsh("""
readlink(){{ /opt/local/bin/greadlink "$@"; }}; export -f readlink
./configure {configure_pre_args} {configure_args}
""".format(
        configure_pre_args = " ".join(configure_pre_args),
        configure_args     = " ".join(args),
    ))


def make_install(check=False, archive=False, parallel=True):
    if parallel:
        make = "make --jobs=" + ncpu
    else:
        make = "make"

    if check:
        make_check = "make check"
    else:
        make_check = ":"

    vsh("""
readlink(){{ /opt/local/bin/greadlink "$@"; }}; export -f readlink
{make}
{make_check}
make install
""".format(
    make       = make,
    make_check = make_check,
))

    if archive != False:
        binMake(archive)


def make_uninstall():
    check_call(["make", "uninstall"])


def git_checkout(branch="master"):
    check_call(["git", "checkout", "-f", branch])


def patch(*args):
    for f in args:
        check_call(["patch", "-Np1"], stdin=open(f, "r"))


def message(*args):
    print "\033[33m*** %s ***\033[m" % " ".join(args)


def extract(src, dst):
    os.chdir(BUILDROOT)
    if os.path.splitext(src)[-1] == ".xz":
        xzcat = Popen(["xzcat", src], stdout=PIPE)
        check_call(["tar", "xf", "-"], stdin=xzcat.stdout)
    else:
        check_call(["tar", "xf", src])
    os.chdir(dst)

def binMake(name):
    vsh("""
tar czf {archive} \
--exclude=".git*" \
--exclude=".svn*" \
--exclude=".hg*" \
-C {workdir} {name}
""".format(
    workdir = BUILDROOT,
    name    = name,
    archive = os.path.join(DEPOSROOT, name + ".tar.gz"),
))

def binCheck(name):
    archive = os.path.join(DEPOSROOT, name + ".tar.gz")
    if os.path.exists(archive):
        vsh("""
tar xf {archive} -C {workdir}
cd {workdir}/{name}
make install
""".format(
        workdir = BUILDROOT,
        archive = archive,
        name    = name,
))
        return True
    else:
        return False

def p7z(*args):
    check_call(('/opt/local/bin/7z',) + args)





# ------------------------------------------------------------------------------
# Build section
# ------------------------------------------------------------------------------
def build_windows_tools():
    dst         = os.path.join(W_DATADIR, 'wine', 'plugin')
    dx9_feb2010 = os.path.join(PROJECT_ROOT, 'rsrc/directx9/directx_feb2010_redist.exe')
    dx9_jun2010 = os.path.join(PROJECT_ROOT, 'rsrc/directx9/directx_Jun2010_redist.exe')
    vbrun60sp6  = os.path.join(PROJECT_ROOT, 'rsrc/vbrun60sp6/VB6.0-KB290887-X86.exe')
    vcrun60     = os.path.join(PROJECT_ROOT, 'rsrc/vcrun60/VC6RedistSetup_jpn.exe')
    vcrun2005   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2005')
    vcrun2008   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2008sp1')
    vcrun2010   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2010sp1')

    for f in [
        dst,
        os.path.join(dst, 'inf'),
    ]:
        if not os.path.exists(f):
            os.makedirs(f)

    check_call(['/opt/local/bin/7z', 'x', '-o' + os.path.join(dst, 'directx9/feb2010'), dx9_feb2010])
    check_call(['/opt/local/bin/7z', 'x', '-o' + os.path.join(dst, 'directx9/jun2010'), dx9_jun2010, '-x!*200?*', '-x!Feb2010*'])
    check_call(['/opt/local/bin/7z', 'x', '-o' + os.path.join(dst, 'vbrun60sp6'), vbrun60sp6])
    check_call(['/opt/local/bin/7z', 'x', '-o' + os.path.join(dst, 'vcrun60'), vcrun60])
    shutil.copytree(vcrun2005, os.path.join(dst, 'vcrun2005'))
    shutil.copytree(vcrun2008, os.path.join(dst, 'vcrun2008sp1'))
    shutil.copytree(vcrun2010, os.path.join(dst, 'vcrun2010sp1'))

    for f in ['init_wine.py']:
        shutil.copy(os.path.join(PROJECT_ROOT, f),
                    os.path.join(W_BINDIR, f))


    for f in ['osx-wine.inf']:
        shutil.copy(os.path.join(PROJECT_ROOT, 'osx-wine-inf', f),
                    os.path.join(dst, 'inf', f))

    for f in [
        'dxredist.inf',
        'vcredist.inf',
        'win2k.reg',
        'winxp.reg',
    ]:
        shutil.copy(os.path.join(PROJECT_ROOT, 'inf', f),
                    os.path.join(dst, 'inf', f))

build_windows_tools()

# ----------------------------------------------------------------------------- freetype
def build_freetype():
    name = "freetype"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout()
        autogen()
        configure("--with-old-mac-fonts")
        make_install(archive=name)
# ----------------------------------------------------------------------------- gc
def build_gc():
    name = "gc"
    message("Building", name)
    if not binCheck(name):
        reposcopy("/usr/local/src/repos/bdwgc")
        git_checkout()
        shutil.copytree("/usr/local/src/repos/libatomic_ops", "libatomic_ops")
        autoreconf()
        configure()
        make_install(parallel=False) # do not run parallel build
        binMake(name)
# ----------------------------------------------------------------------------- gettext
def build_gettext():
    name = "gettext-0.18.3.1"
    message(name)
    if not binCheck(name):
        extract(os.path.join("/usr/local/src/tarballs", name + ".tar.gz"), "gettext-0.18.3.1")
        configure(
            "--disable-csharp",
            "--disable-java",
            "--disable-native-java",
            "--disable-openmp",
            "--enable-threads=posix",
            "--with-included-gettext",
            "--with-included-glib",
            "--with-included-libcroro",
            "--with-included-libunistring",
            "--without-cvs",
            "--without-emacs",
            "--without-git",
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- glib
def build_glib():
    name = "glib"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout(branch="glib-2-36")
        autogen()
        configure(
            "--disable-fam",
            "--disable-selinux",
            "--disable-silent-rules",
            "--disable-xattr",
            "--with-threads=posix",
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- gmp
def build_gmp():
    name = "gmp-5.1"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        autoreconf()
        vsh("""
grep '^@set' .bootstrap > doc/version.texi
unset CFLAGS CXXFLAGS
./configure --prefix={prefix} ABI=32
""".format(**configure_format))
        make_install(check=True, archive=name)
# ----------------------------------------------------------------------------- gnutls
def build_gnutls():

    def build_libtasn1():
        name = "libtasn1"
        message(name)
        if not binCheck(name):
            reposcopy(name)
            git_checkout()
            open("ChangeLog", "w").close()
            autoreconf()
            configure(
                "--disable-silent-rules",
                "--disable-gtk-doc",
                "--disable-gtk-doc-html",
                "--disable-gtk-doc.pdf",
                "--disable-valgrind-tests",
            )
            make_install(parallel=False, archive=name)
    build_libtasn1()

    def build_nettle():
        name = "nettle"
        message(name)
        if not binCheck(name):
            reposcopy(name)
            autoreconf()
            configure("--disable-documentation")
            make_install(archive=name)
    build_nettle()

    def build_libidn():
        name = "libidn-1.28"
        message(name)
        if not binCheck(name):
            extract(os.path.join("/usr/local/src/tarballs", name + ".tar.gz"), name)
            configure()
            make_install(archive=name)
#    build_libidn()

    def build_p11kit():
        name = "p11-kit-0.20.1"
        message(name)
        if not binCheck(name):
            extract(os.path.join("/usr/local/src/tarballs", name + ".tar.gz"), name)
            configure(
                "--disable-coverage",
                "--disable-debug",
                "--disable-doc",
                "--disable-doc-html",
                "--disable-doc-pdf",
                "--disable-nls",
                "--disable-silent-rules",
                "--without-trust-paths",
            )
            make_install(archive=name)
#    build_p11kit()

    name = "gnutls"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout(branch="gnutls_3_1_x")
        open('ChangeLog', 'w').close()
        autoreconf(force=True)
        configure(
            "--disable-static",
            "--disable-doc",
            "--disable-gtk-doc",
            "--disable-gtk-doc-html",
            "--disable-gtk-doc-pdf",
            "--disable-guile",
            "--disable-nls",
            "--disable-silent-rules",
            "--disable-tests",
            "--enable-threads=posix",
            "--without-p11-kit",
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- guile
# dependenceis: readline, gettext, libtool, gmp
# note: llvm/clang installation failed
#
def build_guile():
    name = "guile"
    message("Building guile")
    if not binCheck(name):
        reposcopy(name)
        git_checkout(branch="branch_release-1-8")
#        git_checkout(branch="stable-2.0")
        autoreconf()
#        extract("/usr/local/src/tarballs/guile-2.0.9.tar.gz", "guile-2.0.9")
        configure(
            "--enable-regex",
            "--disable-error-on-warning",
            "--disable-static",
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- gphoto2
def build_libgphoto2():

    def build_libexif():
        name = "libexif-0.6.21"
        message(name)
        if not binCheck(name):
            extract("/usr/local/src/tarballs/libexif-0.6.21.tar.bz2", name)
            configure(
                "--disable-docs",
                "--disable-nls",
                "--with-doc-dir=" + os.path.join(prefix, "share", "doc", "name"),
            )
            make_install(archive=name)
    build_libexif()

    def build_popt():
        name = "popt-1.14"
        message(name)
        if not binCheck(name):
            extract(os.path.join("/usr/local/src/tarballs", name + ".tar.gz"), name)
            configure(
                "--disable-nls",
            )
            make_install(archive=name)
    build_popt()

    def build_gd():
        name = "libgd-2.1.0"
        message(name)
        if not binCheck(name):
            extract(os.path.join("/usr/local/src/tarballs", name + ".tar.xz"), name)
            configure()
            make_install(archive=name)
    build_gd()

    name = "libgphoto2"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        autoreconf("-s")
        configure(
            "--disable-nls",
            "--with-drivers=all",
            """CFLAGS='{cflags} -D_DARWIN_C_SOURCE'""".format(cflags = os.getenv("CFLAGS")),
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- gsm
def build_gsm():
    name = "gsm-1.0.13"
    message(name)
    configure_format["install_name"] = os.path.join(prefix, "lib", "libgsm.dylib")
    
    extract("/usr/local/src/tarballs/gsm-1.0.13.tar.gz", "gsm-1.0-pl13")
    vsh("""
make {install_name} \
CC='{gcc} -ansi -pedantic' \
CCFLAGS='-c -O2 -DNeedFunctionPrototypes=1 -m32 -arch i386' \
LDFLAGS='__LDFLAGS__' \
LIBGSM='{install_name}' \
AR='{gcc}' \
ARFLAGS='-dynamiclib -fPIC -v -arch i386 -install_name $(LIBGSM) -compatibility_version 1 -current_version 1.0.3 -o' \
RANLIB=':' \
RMFLAGS='-f'

install -m 0644 inc/gsm.h {prefix}/include
""".format(**configure_format).replace('__LDFLAGS__', os.getenv('LDFLAGS')))
# ----------------------------------------------------------------------------- libffi
def build_libffi():
    name = "libffi"
    message("Building", name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout()
        configure()
        make_install(archive=name)
# ----------------------------------------------------------------------------- libgpg-error
def build_libgpg_error():
    name = "libgpg-error"
    message("Building", name)
    if not binCheck(name):
        extract("/usr/local/src/tarballs/libgpg-error-1.12.tar.bz2", "libgpg-error-1.12")
        configure("--disable-static")
        make_install(archive=name)
# ----------------------------------------------------------------------------- libjpeg
def build_libjpeg_turbo():
    name = "libjpeg-turbo"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        Popen(["sh", "-v"], stdin=PIPE).communicate("""\
sed -i '' 's|$(datadir)/doc|&/libjpeg-turbo|' Makefile.am
""")
        autoreconf()
        configure("--with-jpeg8")
        make_install(archive=name)
# ----------------------------------------------------------------------------- libpng
def build_libpng():
    name = "libpng"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout("libpng16")
        autogen()
        configure()
        make_install(archive=name)
# ----------------------------------------------------------------------------- libusb
def build_libusb():
    name = "libusb"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        vsh("""
sed -i '' '/^.\\/configure/,$d' autogen.sh
""")
        autogen()
        configure()
        make_install(archive=name)

    def build_libusb_compat():
        name = "libusb-compat-0.1"
        message(name)
        if not binCheck(name):
            reposcopy(name)
            vsh("""
sed -i '' '/^.\\/configure/,$d' autogen.sh
""")
            autogen()
            configure()
            make_install(archive=name)
    build_libusb_compat()
# ----------------------------------------------------------------------------- libtiff
def build_libtiff():
    name = "libtiff"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        configure(
            "--disable-silent-rules",
            "--disable-jbig",
            "--without-x")
        make_install(archive=name)
# ----------------------------------------------------------------------------- Little-CMS
def build_lcms():
    name = "Little-CMS"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        configure()
        make_install(archive=name)
# ----------------------------------------------------------------------------- mpg123
def build_mpg123():
    name = "mpg123-1.15.4"
    message(name)
    if not binCheck(name):
        extract(os.path.join("/usr/local/src/tarballs", name + ".tar.bz2"), name)
        configure(
            "--with-default-audio=coreaudio",
            "--with-optimization=0",
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- orc
def build_orc():
    name = "orc"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        autoreconf(force=True)
        configure("--disable-static")
        make_install(archive=name)
# ----------------------------------------------------------------------------- readline
def build_readline():
    name = "readline"
    message("Building", name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout()
        vsh("""
patch -Np1 < {f}
""".format(
    f = os.path.join(PROJECT_ROOT, 'osx-wine-patch/readline.patch')
))
        configure("--enable-multibyte", "--with-curses")
        make_install(archive=name)
# ----------------------------------------------------------------------------- sane-backends
# dependencies: jpeg, libusb-compat, net-snmp, tiff, zlib
#
def build_sane():

    def build_net_snmp():
        name = "net-snmp"
        message(name)
        if not binCheck(name):
            reposcopy(name)
            git_checkout()
            configure("--with-defaults")
            make_install(archive=name)
    build_net_snmp()
    
    name = "sane-backends"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout()
        configure(
            "--disable-latex",
            "--disable-maintainer-mode",
            "--disable-silent-rules",
            "--disable-translations",
            "--enable-libusb_1_0",
            "--enable-local-backends",
            "--with-docdir=" + os.path.join(prefix, "share", "doc", name),
            "--without-gphoto2",
            "--without-v4l",
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- SDL
def build_SDL():
    name = "SDL"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        configure("--enable-sse2")
        make_install(archive=name)
# ----------------------------------------------------------------------------- unixODBC
def build_unixodbc():
    name = "unixODBC"
    message = (name)
    if not binCheck(name):
        reposcopy(name)
        autoreconf(force=True)
        configure()
        make_install(archive=name)
# ----------------------------------------------------------------------------- wine
def build_wine():
    name = "wine"
    message(name)
    reposcopy(name)
    git_checkout()

    ### PATCH ###
    vsh("""
patch -Np1 < {0}
patch -Np1 < {1}
patch -Np1 < {2}
patch -Np1 < {3}
""".format(os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_autohidemenu.patch'),
           os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_changelocale.patch'),
           os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_deviceid.patch'),
           os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_excludefonts.patch'),
    ))

    ### CONFIGURE / MAKE ###
    vsh("""
./configure \
--prefix={prefix} \
--build={triple} \
--without-capi \
--without-oss \
--without-v4l \
--with-x \
--x-inc=/opt/X11/include \
--x-lib=/opt/X11/lib \
CC="{cc}" CXX="{cxx}"
make -j {jobs}
make install
""".format(
        prefix  = W_PREFIX,
        triple  = triple,
        cc      = CLANG,
        cxx     = CLANGXX,
        jobs    = ncpu,
    ))

    ### ADD RPATH ###
    check_call(['install_name_tool', '-add_rpath', '/opt/X11/lib', os.path.join(W_BINDIR, 'wine')])

    ### RENAME EXECUTABLE ###
    os.rename(os.path.join(W_BINDIR,     'wine'),
              os.path.join(W_LIBEXECDIR, 'wine'))

    ### INSTALL WINELOADER ###
    shutil.copy2(os.path.join(PROJECT_ROOT, 'wineloader.py'),
                 os.path.join(W_BINDIR, 'wine'))
    os.chmod(os.path.join(W_BINDIR, 'wine'), 0755)
# ----------------------------------------------------------------------------- winetricks / cabextract
def build_winetricks():

    def build_cabextract():
        name = "cabextract-1.4"
        message(name)
        if not binCheck(name):
            extract(os.path.join("/usr/local/src/repos/tarballs", name + ".tar.gz"), "cabextract-1.4")
            vsh("""./configure --prefix={prefix} --build={triple}""".format(prefix = W_PREFIX,
                                                                            triple = triple))
            make_install(archive=name)
    build_cabextract()

    name     = 'winetricks'
    message(name)
    reposcopy(name)
    vsh("""
patch -Np1 < {0}
patch -Np1 < {1}
""".format(os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'winetricks_tkool.patch'),
           os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'winetricks_helper_xpsp3jp.patch'),
    ))

    exec_src = os.path.join('src', name)
    exec_dst = os.path.join(W_LIBEXECDIR, name)
    scpt_src = os.path.join(PROJECT_ROOT, 'winetricksloader.py')
    scpt_dst = os.path.join(W_BINDIR, name)

    shutil.copy2(exec_src, exec_dst)
    shutil.copy2(scpt_src, scpt_dst)
    os.chmod(exec_dst, 0755)
    os.chmod(scpt_dst, 0755)
# ----------------------------------------------------------------------------- xz
def build_xz():
    name = "xz"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout()
        autogen()
        configure(
            "--disable-nls",
            "--disable-silent-rules",
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- zlib
def build_zlib():
    name = "zlib"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout()
        vsh("./configure --prefix={prefix}".format(**configure_format))
        binMake(name)
# ============================================================================ #
def finalize():
    for f in [os.path.join(W_DATADIR, 'nihonshu')]:
        if not os.path.exists(f): os.makedirs(f)
        shutil.copy(os.path.join(PROJECT_ROOT, 'LICENSE'),
                    os.path.join(f,            'LICENSE'))

    vsh("""
(
    set +e
    find __W_LIBDIR__ -type f \\! -regex '__W_LIBDIR__/wine/.*' -a \\( -name '*.a' -o -name '*.la' \\) |
    while read f
    do
        rm -vf $f
    done
)
rm -f  __W_LIBDIR__/charset.alias
rm -rf __W_LIBDIR__/gio
rm -rf __W_LIBDIR__/glib-2.0
rm -rf __W_LIBDIR__/libffi-3.0.13
rm -rf __W_LIBDIR__/pkgconfig
""".replace('__W_LIBDIR__', W_LIBDIR))

    os.chdir(W_PREFIX)
    shutil.rmtree(prefix)
    os.makedirs(prefix)
    os.symlink(W_LIBDIR, LIBDIR)
    vsh("""
tar cf - -C {workdir} {name} | /opt/local/bin/xz > {workdir}/{name}_nihonshu.tar.xz
""".format(
        workdir = os.path.dirname(W_PREFIX),
        name    = os.path.basename(W_PREFIX),
    ))


# ============================================================================ #
build_zlib()
build_gsm()
build_xz()
#build_orc()
build_gettext()
build_readline()
build_gmp()
build_libffi()
build_glib()
build_libusb()
#build_guile()
build_gnutls()
build_libpng()
build_freetype()
build_libjpeg_turbo()
build_libtiff()
build_lcms()
build_libgphoto2()
build_sane()

build_SDL()
build_mpg123()

build_wine()
build_winetricks()

finalize()

print >> sys.stdout, 'done.'
