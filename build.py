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
    retcode == 0 or sys.exit(retcode)
    return stdout

def vsh(script):
    ps = Popen(["sh", "-ve"], stdin=PIPE)
    ps.communicate(script)
    retcode = ps.returncode
    retcode == 0 or sys.exit(retcode)

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print >> sys.stderr, '\033[32m' + 'created: %s' % path + '\033[m'


PROJECT_ROOT    = os.path.dirname(os.path.abspath(__file__))
DEPOSROOT       = os.path.join(PROJECT_ROOT, 'depos')
SRCROOT         = os.path.join(PROJECT_ROOT, 'src')

prefix          = "/usr/local/wine/SharedSupport"
PREFIX          = prefix
BUILDROOT       = os.path.join(PREFIX, 'build')

BINDIR          = os.path.join(PREFIX, 'bin')
SBINDIR         = os.path.join(PREFIX, 'sbin')
DATADIR         = os.path.join(PREFIX, 'share')
INCDIR          = os.path.join(PREFIX, 'include')
LIBDIR          = os.path.join(PREFIX, 'lib')
SYSCONFDIR      = os.path.join(PREFIX, 'etc')

W_PREFIX        = '/usr/local/wine'
W_BINDIR        = os.path.join(W_PREFIX,  'bin')
W_DATADIR       = os.path.join(W_PREFIX,  'share')
W_DOCDIR        = os.path.join(W_DATADIR, 'doc')
W_INCDIR        = os.path.join(W_PREFIX,  'include')
W_LIBDIR        = os.path.join(W_PREFIX,  'lib')
W_LIBEXECDIR    = os.path.join(W_PREFIX,  'libexec')


not os.path.exists(W_PREFIX) or shutil.rmtree(W_PREFIX)
for f in [
    DEPOSROOT,
    BUILDROOT,
    BINDIR,
    SBINDIR,
    DATADIR,
    INCDIR,
    SYSCONFDIR,
    W_BINDIR,
    W_DATADIR,
    W_INCDIR,
    W_LIBDIR,
    W_LIBEXECDIR,
]:
    makedirs(f)
os.symlink(W_LIBDIR, LIBDIR)

#-------------------------------------------------------------------------------

import build_preset as my
my.PREFIX = PREFIX
my.main()

CCACHE  = my.CCACHE
GCC     = my.GCC
GXX     = my.GXX
CLANG   = my.CLANG
CLANGXX = my.CLANGXX
P7ZIP   = my.P7ZIP
AUTOTOOLS_PATH = my.AUTOTOOLS_PATH

cabextract   = my.cabextract
git_checkout = my.git_checkout
hg_update    = my.hg_update
p7zip        = my.p7zip

#-------------------------------------------------------------------------------

ncpu        = str(int(get_stdout("sysctl", "-n", "hw.ncpu")) + 1)
triple      = "i686-apple-darwin" + os.uname()[2]

configure_format = dict(prefix    = prefix,
                        triple    = triple,
                        jobs      = ncpu,
                        cc        = os.environ['CC'],
                        cxx       = os.environ['CXX'],
                        gcc       = GCC,
                        gxx       = GXX,
                        archflags = my.archflags,
                        optflags  = my.optflags,
                        sdkroot   = my.sdkroot,
                        osxver    = my.osx_ver,
                        incdir    = INCDIR,
                        libdir    = LIBDIR)

check_call(['sh', '-c', 'declare'])

#-------------------------------------------------------------------------------

class Autotools:

    def autogen(self, *args):
        vsh("""
PATH={path} NOCONFIGURE=1 ./autogen.sh {args}
""".format(
        path = AUTOTOOLS_PATH,
        args = ' '.join(args),
    ))
    
    def autoreconf(self, *args):
        vsh("""
PATH={path} NOCONFIGURE=1 autoreconf -v -i {args}
""".format(
        path = AUTOTOOLS_PATH,
        args = ' '.join(args),
    ))

autotools  = Autotools()
autogen    = autotools.autogen
autoreconf = autotools.autoreconf

#-------------------------------------------------------------------------------

def reposcopy(name):
    src = os.path.join(PROJECT_ROOT, 'src', name)
    dst = os.path.join(BUILDROOT, name)

    shutil.copytree(src, dst, True)
    os.chdir(dst)


def configure(*args):
    _args = [
        '--enable-shared',
        '--disable-dependency-tracking',
    ]
    _args.extend(args)

    vsh("""
readlink(){{ /opt/local/bin/greadlink "$@"; }}; export -f readlink
./configure --prefix={prefix} --build={triple} {args}
""".format(
        prefix = PREFIX,
        triple = triple,
        args   = ' '.join(_args),
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


def patch(*args):
    for f in args:
        check_call(["patch", "-Np1"], stdin=open(f, "r"))


def message(*args):
    print >> sys.stdout, '\033[33m' + '*** %s ***' % ' '.join(args) + '\033[m'


def extract(src, dst):
    src = os.path.join(SRCROOT, src)
    os.chdir(BUILDROOT)
    if os.path.splitext(src)[-1] == '.xz':
        src = Popen([P7ZIP, 'x', '-so', src], stdout = PIPE)
        check_call(['tar', 'xf', '-'], stdin = src.stdout)
    else:
        check_call(['tar', 'xf', src])
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


def installFile(src, dst):
    makedirs(os.path.dirname(dst))
    shutil.copy(src, dst)
    print >> sys.stderr, '\033[32m' + 'installed: %s -> %s' % (src, dst) + '\033[m'


def installDoc(name, *args):
    docdir = os.path.join(W_DOCDIR, name)
    makedirs(docdir)
    for f in args:
        src = f
        dst = os.path.join(docdir, os.path.basename(f))
        installFile(src, dst)


# ------------------------------------------------------------------------------
# Build section
# ------------------------------------------------------------------------------

def install_core_resources():
    # INSTALL PROJECT LICENSE --------------------------------------------------
    f   = 'LICENSE'
    src = os.path.join(PROJECT_ROOT, f)
    dst = os.path.join(W_DOCDIR, 'nihonshu', f)
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

def install_plugin():

    def install_plugin_7z():
        src = os.path.join(PROJECT_ROOT, 'rsrc/7z922.exe')
        dst = os.path.join(destroot, '7-Zip')
        p7zip('x', '-o' + dst, src, '-x!$*')

        src = os.path.join(PROJECT_ROOT, 'inf/7z.inf')
        dst = os.path.join(destroot,     'inf/7z.inf')
        installFile(src, dst)

    def install_plugin_vsrun6():
        src = os.path.join(PROJECT_ROOT, 'rsrc/vsrun6sp6/Vs6sp6.exe')

        # Visual Basic 6.0 SP 6 ------------------------------------------------
        dst     = os.path.join(destroot, 'vbrun6sp6')
        sub_src = 'vbrun60.cab'
        cabextract('-L', '-d', dst, '-F', sub_src, src)

        sub_src = os.path.join(dst, sub_src)
        cabextract('-L', '-d', dst, sub_src)
        os.remove(sub_src)

        # Visual C++ 6.0 SP 6 --------------------------------------------------
        dst     = os.path.join(destroot, 'vcrun6sp6')
        sub_src = 'vcredist.exe'
        cabextract('-L', '-d', dst, '-F', sub_src, src)

    destroot    = os.path.join(W_DATADIR, 'wine/plugin')
    dx9_feb2010 = os.path.join(PROJECT_ROOT, 'rsrc/directx9/directx_feb2010_redist.exe')
    dx9_jun2010 = os.path.join(PROJECT_ROOT, 'rsrc/directx9/directx_Jun2010_redist.exe')
    vcrun2005   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2005sp1_jun2011')
    vcrun2008   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2008sp1_jun2011')
    vcrun2010   = os.path.join(PROJECT_ROOT, 'rsrc/vcrun2010sp1_aug2011')

    makedirs(destroot)

    # INSTALL RUNTIME ----------------------------------------------------------
    p7zip('x', '-o' + os.path.join(destroot, 'directx9/feb2010'), dx9_feb2010)
    p7zip('x', '-o' + os.path.join(destroot, 'directx9/jun2010'), dx9_jun2010, '-x!*200?*', '-x!Feb2010*')
    shutil.copytree(vcrun2005, os.path.join(destroot, 'vcrun2005sp1_jun2011'))
    shutil.copytree(vcrun2008, os.path.join(destroot, 'vcrun2008sp1_jun2011'))
    shutil.copytree(vcrun2010, os.path.join(destroot, 'vcrun2010sp1_aug2011'))

    install_plugin_vsrun6()
    install_plugin_7z()

    # INSTALL INF --------------------------------------------------------------
    for f in [
        'inf/dxredist.inf',
        'inf/vsredist.inf',
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
def build_glib(name = 'glib'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout(branch = 'glib-2-38')
    autogen()
    configure(
        '--disable-fam',
        '--disable-selinux',
        '--disable-silent-rules',
        '--disable-xattr',
        '--with-threads=posix',
    )
    make_install(archive = name)
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
def build_libjpeg_turbo(name = 'libjpeg-turbo'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    vsh("""sed -i '' 's|$(datadir)/doc|&/libjpeg-turbo|' Makefile.am""")
    autoreconf()
    configure("--with-jpeg8")
    make_install(archive = name)
# ----------------------------------------------------------------------------- libpng
def build_libpng(name = 'libpng'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout('libpng16')
    autogen()
    configure()
    make_install(archive = name)
# ----------------------------------------------------------------------------- libusb
def build_libusb():

    def build_libusb_core(name = 'libusb'):
        message(name)
        if binCheck(name): return
        reposcopy(name)
        vsh("""sed -i '' '/^.\\/configure/,$d' autogen.sh""")
        autogen()
        configure()
        make_install(archive = name)

    def build_libusb_compat(name = 'libusb-compat-0.1'):
        message(name)
        if binCheck(name): return
        reposcopy(name)
        vsh("""sed -i '' '/^.\\/configure/,$d' autogen.sh""")
        autogen()
        configure()
        make_install(archive = name)

    build_libusb_core()
    build_libusb_compat()
# ----------------------------------------------------------------------------- libtiff
def build_libtiff(name = 'libtiff'):
    message(name)
    if not binCheck(name):
        reposcopy(name)
        git_checkout(branch = 'branch-3-9')
        configure(
            '--disable-jbig',
            '--disable-silent-rules',
            '--without-x',
        )
        make_install(archive = name)
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
        autoreconf('-f')
        configure()
        make_install(archive=name)
# ----------------------------------------------------------------------------- readline
def build_readline(name = 'readline'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    patch = os.path.join(PROJECT_ROOT, 'osx-wine-patch/readline.patch')
    vsh("""patch -Np1 < %s""" % patch)
    configure(
        '--enable-multibyte',
        '--with-curses',
    )
    make_install(archive = name)
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
def build_unixodbc(name = 'unixODBC'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    autoreconf('-f')
    configure()
    makedirs(os.path.join(prefix, 'etc'))
    make_install(archive = name)
# ----------------------------------------------------------------------------- wine
def build_wine(name = 'wine'):
    message(name)
    reposcopy(name)
    git_checkout()
#    git_checkout(branch = 'wine-1.7.3')

    vsh("""patch -Np1 < %s""" % os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_autohidemenu.patch'))
    vsh("""patch -Np1 < %s""" % os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_changelocale.patch'))
    vsh("""patch -Np1 < %s""" % os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_deviceid.patch'))
    vsh("""patch -Np1 < %s""" % os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'wine_excludefonts.patch'))

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
    src = os.path.join(W_BINDIR, 'wine')
    vsh("""install_name_tool -add_rpath /opt/X11/lib %s""" % src)

    ### RENAME EXECUTABLE ###
    src = os.path.join(W_BINDIR,     'wine')
    dst = os.path.join(W_LIBEXECDIR, 'wine')
    os.rename(src, dst)

    ### INSTALL WINE LOADER ###
    src = os.path.join(PROJECT_ROOT, 'wineloader.py')
    dst = os.path.join(W_BINDIR,     'wine')
    shutil.copy(src, dst)
    os.chmod(dst, 0755)

    installDoc(
        name,
        'ANNOUNCE',
        'AUTHORS',
        'COPYING.LIB',
        'LICENSE',
        'README',
    )
# ----------------------------------------------------------------------------- winetricks / cabextract
def build_winetricks():

    def build_cabextract(name = 'cabextract-1.4'):
        message(name)
        extract(name + '.tar.gz', 'cabextract-1.4')
        vsh("""
./configure --prefix={prefix} --build={triple} CC={cc}
""".format(
            prefix = W_PREFIX,
            triple = triple,
            cc     = CLANG,
        ))
        make_install(archive = name)
        installDoc(
            'cabextract',
            'AUTHORS',
            'COPYING',
            'README',
        )

    def build_winetricks_core(name = 'winetricks'):
        message(name)
        reposcopy(name)
        vsh("""patch -Np1 < %s""" % os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'winetricks_tkool.patch'))
        vsh("""patch -Np1 < %s""" % os.path.join(PROJECT_ROOT, 'osx-wine-patch', 'winetricks_helper_xpsp3jp.patch'))
        vsh("""make install PREFIX=%s""" % W_PREFIX)

        ### RENAME EXECUTABLE ###
        src = os.path.join(W_BINDIR,     'winetricks')
        dst = os.path.join(W_LIBEXECDIR, 'winetricks')
        os.rename(src, dst)

        ### INSTALL WINETRICKS LOADER ###
        src = os.path.join(PROJECT_ROOT, 'winetricksloader.py')
        dst = os.path.join(W_BINDIR,     'winetricks')
        shutil.copy(src, dst)
        os.chmod(dst, 0755)

        installDoc(
            name,
            'src/COPYING',
        )

    build_cabextract()
    build_winetricks_core()
# ----------------------------------------------------------------------------- xz
def build_xz(name = 'xz'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    autogen()
    configure(
        '--disable-nls',
        '--disable-silent-rules',
    )
    make_install(archive = name)
# ----------------------------------------------------------------------------- zlib
def build_zlib(name = 'zlib'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    vsh("""CC={clang} ./configure --prefix={prefix}""".format(
        clang  = CLANG,
        prefix = PREFIX,
    ))
    make_install(archive = name)
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
    makedirs(prefix)
    os.symlink('../lib', LIBDIR)

    def create_distfile(distname):
#        vsh("""
#tar cf - -C {workdir} {name} | /opt/local/bin/xz > {workdir}/{distname}.tar.xz
#""".format(
#        workdir  = os.path.dirname(W_PREFIX),
#        name     = os.path.basename(W_PREFIX),
#        distname = distname,
#    ))
        src = W_PREFIX
        dst = os.path.dirname(W_PREFIX)
        dst = os.path.join(dst, distname + '.exe')
        p7zip('a', '-sfx', dst, src)

    install_core_resources()
    create_distfile('wine_nihonshu_no-plugin')
    install_plugin()
    create_distfile('wine_nihonshu')

# ============================================================================ #
build_zlib()
build_gsm()
build_xz()
#build_orc()
build_gettext()
build_readline()
build_unixodbc()
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
