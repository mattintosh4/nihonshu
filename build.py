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

def vsh(script):
    ps = Popen(["sh", "-ve"], stdin=PIPE)
    ps.communicate(script)
    if ps.returncode != 0:
        sys.exit(ps.retcode)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

#distname        = 'wine_nihonshu'
distname        = 'wine_nihonshu_dx9'

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
W_DOCDIR        = os.path.join(W_DATADIR, 'doc')
W_INCDIR        = os.path.join(W_PREFIX, 'include')
W_LIBDIR        = os.path.join(W_PREFIX, 'lib')
W_LIBEXECDIR    = os.path.join(W_PREFIX, 'libexec')

DEPOSROOT       = os.path.join(PROJECT_ROOT, 'depos')
SRCROOT         = os.path.join(PROJECT_ROOT, 'src')

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

#-------------------------------------------------------------------------------

import build_preset as my
my.PREFIX = prefix
my.main()

CCACHE  = my.CCACHE
GCC     = my.GCC
GXX     = my.GXX
CLANG   = my.CLANG
CLANGXX = my.CLANGXX

git_checkout = my.git_checkout
hg_update    = my.hg_update
p7zip        = my.p7zip

#-------------------------------------------------------------------------------

ncpu        = str(int(get_stdout("sysctl", "-n", "hw.ncpu")) + 1)
triple      = "i686-apple-darwin" + os.uname()[2]

configure_format = dict(prefix    = prefix,
                        triple    = triple,
                        jobs      = ncpu,
                        cc        = CLANG,
                        cxx       = CLANGXX,
                        gcc       = GCC,
                        gxx       = GXX,
                        archflags = my.archflags,
                        optflags  = my.optflags,
                        sdkroot   = my.sdkroot,
                        osxver    = my.osx_ver,
                        incdir    = INCDIR,
                        libdir    = LIBDIR)


check_call(["sh", "-c", "declare"])

#---------------#
# GNU Autotools #
#---------------#
class Autotools:
    global AUTOTOOLS_PATH
    AUTOTOOLS_PATH = "/opt/local/bin:/opt/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin"

    ### autogen ###
    def autogen(self, *args):
        vsh("""
PATH={path} \
NOCONFIGURE=1 \
./autogen.sh {autogen_args}
""".format(
        path         = AUTOTOOLS_PATH,
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
        path            = AUTOTOOLS_PATH,
        autoreconf_args = " ".join(args),
    ))

autotools  = Autotools()
autogen    = autotools.autogen
autoreconf = autotools.autoreconf


def copytree(name):
    src = os.path.join(SRCROOT,   name)
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

def patch(*args):
    for f in args:
        check_call(["patch", "-Np1"], stdin=open(f, "r"))


def message(*args):
    print "\033[33m*** %s ***\033[m" % " ".join(args)


def extract(src, dst):
    src = os.path.join(SRCROOT, src)
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

def rm(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            print >> sys.stderr, '\033[31m' + 'removed: %s' % path + '\033[m'
        else:
            os.remove(path)
            print >> sys.stderr, '\033[31m' + 'removed: %s' % path + '\033[m'

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print >> sys.stderr, '\033[32m' + 'created: %s' % path + '\033[m'

def installFile(src, dst):
    makedirs(os.path.dirname(dst))
    shutil.copy(src, dst)
    print >> sys.stderr, '\033[32m' + 'installed: %s -> %s' % (src, dst) + '\033[m'

# ------------------------------------------------------------------------------
# Build section
# ------------------------------------------------------------------------------

def install_core_resources():
    # INSTALL PROJECT LICENSE --------------------------------------------------
    f   = 'LICENSE'
    src = os.path.join(PROJECT_ROOT, f)
    dst = os.path.join(W_DATADIR, 'nihonshu', f)
    installFile(src, dst)

    # INSTALL MODULE -----------------------------------------------------------
    f   = 'init_wine.py'
    src = os.path.join(PROJECT_ROOT, f)
    dst = os.path.join(W_BINDIR, f)
    installFile(src, dst)

    # INSTALL INF --------------------------------------------------------------
    f   = 'osx-wine.inf'
    src = os.path.join(PROJECT_ROOT, 'osx-wine-inf', f)
    dst = os.path.join(W_DATADIR, 'wine/plugin/inf', f)
    installFile(src, dst)

def install_support_files():
    destroot    = os.path.join(W_DATADIR, 'wine/plugin')
    dx9_feb2010 = os.path.join(PROJECT_ROOT, 'rsrc/directx9/directx_feb2010_redist.exe')
    dx9_jun2010 = os.path.join(PROJECT_ROOT, 'rsrc/directx9/directx_Jun2010_redist.exe')
    vbrun60sp6  = os.path.join(PROJECT_ROOT, 'rsrc/vbrun60sp6/VB6.0-KB290887-X86.exe')
    vcrun60     = os.path.join(PROJECT_ROOT, 'rsrc/vcrun60/VC6RedistSetup_jpn.exe')
    vcrun2005   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2005')
    vcrun2008   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2008sp1')
    vcrun2010   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2010sp1')

    makedirs(destroot)

    # INSTALL RUNTIME ----------------------------------------------------------
    p7zip('x', '-o' + os.path.join(destroot, 'directx9/feb2010'), dx9_feb2010)
    p7zip('x', '-o' + os.path.join(destroot, 'directx9/jun2010'), dx9_jun2010, '-x!*200?*', '-x!Feb2010*')
    p7zip('x', '-o' + os.path.join(destroot, 'vbrun60sp6'), vbrun60sp6)
    p7zip('x', '-o' + os.path.join(destroot, 'vcrun60'), vcrun60)
    shutil.copytree(vcrun2005, os.path.join(destroot, 'vcrun2005'))
    shutil.copytree(vcrun2008, os.path.join(destroot, 'vcrun2008sp1'))
    shutil.copytree(vcrun2010, os.path.join(destroot, 'vcrun2010sp1'))

    # INSTALL INF --------------------------------------------------------------
    for f in [
        'inf/dxredist.inf',
        'inf/vcredist.inf',
        'inf/win2k.reg',
        'inf/winxp.reg',
    ]:
        src = os.path.join(PROJECT_ROOT, f)
        dst = os.path.join(destroot, 'inf')
        dst = os.path.join(dst, os.path.basename(f))
        installFile(src, dst)

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
# ----------------------------------------------------------------------------- gettext
def build_gettext():
    name = "gettext-0.18.3.1"
    message(name)
    if not binCheck(name):
        extract(name + ".tar.gz", "gettext-0.18.3.1")
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

    def build_libtasn1(name = 'libtasn1-3.3'):
        message(name)
        if binCheck(name): return
        extract(name + '.tar.gz', name)
        configure(
            '--disable-gtk-doc',
            '--disable-gtk-doc-html',
            '--disable-gtk-doc-pdf',
            '--disable-silent-rules',
            '--disable-static',
        )
        make_install(archive = name)

    def build_nettle(name = 'nettle-2.7.1'):
        message(name)
        if binCheck(name): return
        extract(name + '.tar.gz', name)
        configure(
            '--disable-documentation',
        )
        make_install(archive = name)

    # note: gnutls will fail depending on nettle version.
    def build_gnutls_core(name = 'gnutls'):
        message(name)
        if binCheck(name): return
        reposcopy(name)
        git_checkout(branch = 'gnutls_3_1_x')
        vsh("""PATH={path} make autoreconf""".format(path = AUTOTOOLS_PATH))
        configure(
            '--disable-doc',
            '--disable-gtk-doc',
            '--disable-gtk-doc-html',
            '--disable-gtk-doc-pdf',
            '--disable-nls',
            '--disable-silent-rules',
            '--disable-static',
            '--enable-threads=posix',
        )
        make_install(archive = name)

    build_libtasn1()
    build_nettle()
    build_gnutls_core()
# ----------------------------------------------------------------------------- gphoto2
def build_libgphoto2():

    def build_libexif():
        name = "libexif-0.6.21"
        message(name)
        if not binCheck(name):
            extract(name + '.tar.bz2', name)
            configure(
                "--disable-docs",
                "--disable-nls",
                "--with-doc-dir=" + os.path.join(prefix, 'share/doc', name),
            )
            make_install(archive=name)
    build_libexif()

    def build_popt():
        name = "popt-1.14"
        message(name)
        if not binCheck(name):
            extract(name + '.tar.gz', name)
            configure(
                "--disable-nls",
            )
            make_install(archive=name)
    build_popt()

    def build_gd():
        name = "libgd-2.1.0"
        message(name)
        if not binCheck(name):
            extract(name + '.tar.xz', name)
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
            "CFLAGS='%s -D_DARWIN_C_SOURCE'" % os.getenv('CFLAGS'),
        )
        make_install(archive=name)
# ----------------------------------------------------------------------------- gsm
def build_gsm():
    name = "gsm-1.0.13"
    message(name)
    extract(name + '.tar.gz', 'gsm-1.0-pl13')
    vsh("""
make {install_name} \
CC='{gcc} -ansi -pedantic' \
CCFLAGS='-c -O2 -DNeedFunctionPrototypes=1 -m32 -arch i386' \
LDFLAGS='{ldflags}' \
LIBGSM='{install_name}' \
AR='{gcc}' \
ARFLAGS='-dynamiclib -fPIC -v -arch i386 -install_name $(LIBGSM) -compatibility_version 1 -current_version 1.0.3 -o' \
RANLIB=':' \
RMFLAGS='-f'

install -m 0644 inc/gsm.h {prefix}/include
""".format(
        gcc          = GCC,
        install_name = os.path.join(prefix, "lib", "libgsm.dylib"),
        ldflags      = os.getenv('LDFLAGS'),
        prefix       = prefix,
    ))
# ----------------------------------------------------------------------------- libffi
def build_libffi():
    name = "libffi"
    message("Building", name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout()
        configure()
        make_install(archive=name)
# ----------------------------------------------------------------------------- libjpeg
def build_libjpeg_turbo():
    name = "libjpeg-turbo"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        vsh("""
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
    ### libusb ###
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

    ### libusb-compat-0.1 ###
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
    name = "mpg123"
    message(name)
    if not binCheck(name):
        reposcopy(name)
        autoreconf()
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
patch -Np1 < {patch}
""".format(
        patch = os.path.join(PROJECT_ROOT, 'osx-wine-patch/readline.patch'),
    ))
        configure("--enable-multibyte", "--with-curses")
        make_install(archive=name)
# ----------------------------------------------------------------------------- sane-backends
# dependencies: jpeg, libusb-compat, net-snmp, tiff, zlib
#
def build_sane():

    def build_net_snmp(name = 'net-snmp'):
        message(name)
        if binCheck(name): return
        reposcopy(name)
        git_checkout()
        configure(
            '--with-defaults',
        )
        make_install(archive=name)

    def build_sane_core(name = 'sane-backends'):
        message(name)
        if binCheck(name): return
        reposcopy(name)
        git_checkout()
        configure(
            '--disable-latex',
            '--disable-maintainer-mode',
            '--disable-silent-rules',
            '--disable-translations',
            '--enable-libusb_1_0',
            '--enable-local-backends',
            '--with-docdir=' + os.path.join(prefix, 'share', 'doc', name),
            '--without-gphoto2',
            '--without-v4l',
        )
        make_install(archive=name)

    build_net_snmp()
    build_sane_core()
# ----------------------------------------------------------------------------- SDL
def build_SDL(name = 'SDL'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    hg_update('SDL-1.2')
    autogen()
    configure(
        '--enable-sse2',
    )
    make_install(archive = name)
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
for f in {patch}
do
    patch -Np1 < $f
done
""".format(
        patch = ' '.join([os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_autohidemenu.patch'),
                          os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_changelocale.patch'),
                          os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_deviceid.patch'),
                          os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_excludefonts.patch'),
                        ])
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
            extract(name + ".tar.gz", "cabextract-1.4")
            vsh("""./configure --prefix={prefix} --build={triple}""".format(prefix = W_PREFIX,
                                                                            triple = triple))
            make_install(archive=name)
    build_cabextract()

    name     = 'winetricks'
    message(name)
    reposcopy(name)
    vsh("""
for f in {patch}
do
    patch -Np1 < $f
done
""".format(
        patch = ' '.join([os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'winetricks_tkool.patch'),
                          os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'winetricks_helper_xpsp3jp.patch'),
                        ])
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
        vsh("""
./configure --prefix={prefix}
""".format(**configure_format))
        make_install(archive=name)
# ============================================================================ #
def finalize():
    os.chdir(W_PREFIX)

    for root, dirs, files in os.walk(W_LIBDIR):
        if root == os.path.join(W_LIBDIR, 'wine'): continue

        if root == W_LIBDIR:
            for d in dirs:
                d = os.path.join(root, d)
                if d.endswith((
                    'gio',
                    'glib-2.0',
                    'libffi-3.0.13',
                    'pkgconfig',
                )):
                    if os.path.exists(d):
                        rm(d)

        for f in files:
            f = os.path.join(root, f)
            if f.endswith((
                '.a',
                '.la',
                '.alias',
            )):
                if os.path.exists(f):
                    rm(f)

    rm(os.path.join(W_DATADIR, 'applications'))

    ### REBUILD SHARED SUPPORT DIR ###
    rm(prefix)
    os.makedirs(prefix)
    os.symlink('../lib', LIBDIR)

    def create_distfile(distname):
        vsh("""
tar cf - -C {workdir} {name} | /opt/local/bin/xz > {workdir}/{distname}.tar.xz
""".format(
        workdir  = os.path.dirname(W_PREFIX),
        name     = os.path.basename(W_PREFIX),
        distname = distname,
    ))

    install_core_resources()
    create_distfile('wine_nihonshu')
    install_support_files()
    create_distfile('wine_nihonshu_dx9')

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

print >> sys.stderr, 'done.'
