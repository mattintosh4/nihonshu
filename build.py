#!/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import *
import os
import re
import sys
import shutil


INSTALL_ROOT    = '/usr/local/wine'
PROJECT_ROOT    = os.path.dirname(os.path.abspath(__file__))

DEPOSROOT       = os.path.join(PROJECT_ROOT, 'depos')
SRCROOT         = os.path.join(PROJECT_ROOT, 'src')
PATCHROOT       = os.path.join(PROJECT_ROOT, 'osx-wine-patch')
BUILDROOT       = os.path.join(os.path.expandvars('$TMPDIR'), 'build', 'wine')

W_PREFIX        = INSTALL_ROOT
W_BINDIR        = os.path.join(W_PREFIX,  'bin')
W_DATADIR       = os.path.join(W_PREFIX,  'share')
W_DOCDIR        = os.path.join(W_DATADIR, 'doc')
W_INCDIR        = os.path.join(W_PREFIX,  'include')
W_LIBDIR        = os.path.join(W_PREFIX,  'lib')
W_LIBEXECDIR    = os.path.join(W_PREFIX,  'libexec')

PREFIX          = os.path.join(W_PREFIX, 'SharedSupport')
BINDIR          = os.path.join(PREFIX,   'bin')
SBINDIR         = os.path.join(PREFIX,   'sbin')
DATADIR         = os.path.join(PREFIX,   'share')
DOCDIR          = os.path.join(DATADIR,  'doc')
INCDIR          = os.path.join(PREFIX,   'include')
LIBDIR          = os.path.join(PREFIX,   'lib')
SYSCONFDIR      = os.path.join(PREFIX,   'etc')


def message(strings, color = 'green'):
    color = {
        'red'   : 31,
        'green' : 32,
        'orange': 33,
    }[color]
    print >> sys.stdout, """\033[{color}m*** {strings} ***\033[m""".format(**locals().copy())


def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
        message('created: ' + path)


def rm(path):
    if not os.path.exists(path): return
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
    message('removed: ' + path, 'red')


def installFile(src, dst, mode = 0644):
    makedirs(os.path.dirname(dst))
    shutil.copy(src, dst)
    os.chmod(dst, mode)
    message('installed: %s -> %s' % (src, dst))


def installDoc(name, *args):
    docdir = os.path.join(W_DOCDIR, name)
    makedirs(docdir)
    for f in args:
        installFile(os.path.join(BUILDROOT, name, f),
                    os.path.join(docdir, os.path.basename(f)))

#-------------------------------------------------------------------------------

not os.path.exists(BUILDROOT) or rm(BUILDROOT)
not os.path.exists(W_PREFIX) or rm(W_PREFIX)

for f in [
    DEPOSROOT,
    BUILDROOT,

    W_BINDIR,
    W_DATADIR,
    W_INCDIR,
    W_LIBDIR,
    W_LIBEXECDIR,

    BINDIR,
    SBINDIR,
    DATADIR,
    DOCDIR,
    INCDIR,
    SYSCONFDIR,
]:
    makedirs(f)
os.symlink(W_LIBDIR, LIBDIR)


import build_preset as my
my.PREFIX = PREFIX
my.main()

GCC     = my.GCC
GXX     = my.GXX
CLANG   = my.CLANG
CLANGXX = my.CLANGXX
P7ZIP   = my.P7ZIP

get_stdout   = my.get_stdout
vsh          = my.vsh
cabextract   = my.cabextract
git_checkout = my.git_checkout
hg_update    = my.hg_update
p7zip        = my.p7zip

autotools      = my.Autotools()
autogen        = autotools.autogen
autoreconf     = autotools.autoreconf

#-------------------------------------------------------------------------------

class BuildCommands(object):

    def __init__(self):
        global ncpu
        global triple

        ncpu   = str(int(int(get_stdout('sysctl', '-n', 'hw.ncpu')) * 1.5))
        triple = 'i686-apple-darwin' + os.uname()[2]

    def reposcopy(self, name):
        src = os.path.join(PROJECT_ROOT, 'src', name)
        dst = os.path.join(BUILDROOT, name)
    
        shutil.copytree(src, dst, True)
        os.chdir(dst)

    def configure(self, *args, **kwargs):
        pre_args = (
            '--enable-shared',
            '--disable-dependency-tracking'
        )
        kwargs.setdefault('prefix', PREFIX)
        kwargs.setdefault('triple', triple)
        kwargs.setdefault('args',   ' '.join(pre_args + args))
        vsh(
"""
./configure --prefix={prefix} --build={triple} {args}
""".format(**kwargs))

    def make_install(self, **kwargs):
        kwargs.setdefault('archive',    False)
        kwargs.setdefault('check',      False)
        kwargs.setdefault('parallel',   True)
        kwargs.setdefault('make',       'make -j {0}'.format(ncpu))
        kwargs.setdefault('make_check', 'make check')
        kwargs.setdefault('make_args',  '')

        kwargs['parallel'] or kwargs.update(make       = 'make')
        kwargs['check']    or kwargs.update(make_check = ':')

        vsh('{make} {make_args} && {make_check} && make install'.format(**kwargs))

        if kwargs['archive'] is not False:
            binMake(kwargs['archive'])

    def patch(self, *args):
        for f in args:
            vsh('patch -Np1 < {0}'.format(f))

buildCommands = BuildCommands()
reposcopy     = buildCommands.reposcopy
configure     = buildCommands.configure
make_install  = buildCommands.make_install
patch         = buildCommands.patch


def extract(name, ext, dirname = ''):
    d = dict(
        dstroot = BUILDROOT,
        srcroot = SRCROOT,
        f       = name + ext,
        p7zip   = P7ZIP,
    )
    if ext.endswith('.xz'):
        cmd = """{p7zip} x -so {srcroot}/{f} | tar xf - -C {dstroot}""".format(**d)
    else:
        cmd = """tar xf {srcroot}/{f} -C {dstroot}""".format(**d)
    vsh(cmd)
    if dirname:
        os.chdir(os.path.join(BUILDROOT, dirname))
    else:
        os.chdir(os.path.join(BUILDROOT, name))
    print >> sys.stderr, os.getcwd()


def binMake(name):
    srcroot = BUILDROOT
    dstroot = DEPOSROOT
    vsh(
"""
tar czf {dstroot}/{name}.tar.gz \
--exclude=".git*" \
--exclude=".svn*" \
--exclude=".hg*"  \
-C {srcroot} {name}
""".format(**locals().copy()))


def binCheck(name):
    srcroot = DEPOSROOT
    dstroot = BUILDROOT
    if not os.path.exists(os.path.join(srcroot, name + '.tar.gz')): return False
    vsh(
"""
tar xf {srcroot}/{name}.tar.gz -C {dstroot}
cd {dstroot}/{name}
make install
""".format(**locals().copy()))
    return True


#-------------------------------------------------------------------------------

def install_core_resources():
    # note install project license
    f = 'LICENSE'
    installFile(os.path.join(PROJECT_ROOT, f),
                os.path.join(W_DOCDIR, 'nihonshu', f))

    # note: install python module
    f = 'createwineprefix.py'
    installFile(os.path.join(PROJECT_ROOT, f),
                os.path.join(W_BINDIR, f))

    # note: install inf
    f = 'osx-wine.inf'
    installFile(os.path.join(PROJECT_ROOT, 'osx-wine-inf', f),
                os.path.join(W_DATADIR, 'wine/plugin/inf', f))

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

#-------------------------------------------------------------------------------

# FREETYPE ---------------------------------------------------------------------

def build_freetype(name = 'freetype'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    autogen()
    configure(
        '--with-old-mac-fonts',
    )
    make_install(archive = name)

# GETTEXT ----------------------------------------------------------------------

def build_gettext(name = 'gettext-0.18.3.1'):
    message(name)
    if binCheck(name): return
    extract(name, '.tar.gz')
    configure(
        '--disable-csharp',
        '--disable-java',
        '--disable-native-java',
        '--disable-openmp',
        '--enable-threads=posix',
        '--with-included-gettext',
        '--with-included-glib',
        '--with-included-libcroro',
        '--with-included-libunistring',
        '--without-cvs',
        '--without-emacs',
        '--without-git',
    )
    make_install(archive = name)

# GLIB -------------------------------------------------------------------------

def build_glib(name = 'glib'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout('glib-2-38')
    autogen()
    configure(
        '--disable-fam',
        '--disable-selinux',
        '--disable-silent-rules',
        '--disable-xattr',
        '--with-threads=posix',
    )
    make_install(archive = name)

# GMP --------------------------------------------------------------------------

def build_gmp(name = 'gmp-5.1'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    hg_update()
    autoreconf()
    vsh(
"""
grep '^@set' .bootstrap > doc/version.texi
unset CFLAGS CXXFLAGS
./configure --prefix={prefix} ABI=32
""".format(
        prefix = PREFIX,
    ))
    make_install(check = True, archive = name)

# GNUTLS -----------------------------------------------------------------------

def build_libtasn1(name = 'libtasn1-3.3'):
    message(name)
    if binCheck(name): return
    extract(name, '.tar.gz')
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
    extract(name, '.tar.gz')
    configure(
        '--disable-documentation',
    )
    make_install(archive = name)

# note: gnutls will fail depending on nettle version.
def build_gnutls(name = 'gnutls'):
    build_libtasn1()
    build_nettle()

    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout(branch = 'gnutls_3_1_x')
    autotools.make(
        'autoreconf',
    )
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

# GSM --------------------------------------------------------------------------

def build_gsm(name = 'gsm-1.0.13'):
    message(name)
    extract(name, '.tar.gz', 'gsm-1.0-pl13')
    vsh(
"""
make {install_name} \
CC='{cc} -ansi -pedantic' \
CCFLAGS='-c {cflags} -DNeedFunctionPrototypes=1' \
LDFLAGS='{ldflags}' \
LIBGSM='{install_name}' \
AR='{cc}' \
ARFLAGS='-dynamiclib -fPIC -v -arch i386 -install_name $(LIBGSM) -compatibility_version 1 -current_version 1.0.3 -o' \
RANLIB=':' \
RMFLAGS='-f'

install -m 0644 inc/gsm.h {prefix}/include
""".format(
        prefix       = PREFIX,
        cc           = os.getenv('CC'),
        cflags       = os.getenv('CFLAGS'),
        ldflags      = os.getenv('LDFLAGS'),
        install_name = os.path.join(LIBDIR, 'libgsm.dylib'),
    ))

# LIBFFI -----------------------------------------------------------------------

def build_libffi(name = 'libffi'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    configure()
    make_install(archive = name)

# LIBGPHOTO2 -------------------------------------------------------------------

def build_libexif(name = 'libexif-0.6.21'):
    message(name)
    if binCheck(name): return
    extract(name, '.tar.bz2')
    configure(
        '--disable-docs',
        '--disable-nls',
        '--with-doc-dir=' + os.path.join(DOCDIR, name),
    )
    make_install(archive = name)

def build_popt(name = 'popt-1.14'):
    message(name)
    if binCheck(name): return
    extract(name, '.tar.gz')
    configure(
        '--disable-nls',
    )
    make_install(archive = name)

def build_gd(name = 'libgd-2.1.0'):
    message(name)
    if binCheck(name): return
    extract(name, '.tar.xz')
    configure(
        '--without-fontconfig',
        '--without-x',
        '--with-freetype=' + PREFIX,
        '--with-jpeg='     + PREFIX,
        '--with-png='      + PREFIX,
        '--with-tiff='     + PREFIX,
        '--with-zlib='     + PREFIX,
    )
    make_install(archive = name)

def build_libgphoto2(name = 'libgphoto2'):
    build_libexif()
    build_popt()
    build_gd()

    message(name)
    if binCheck(name): return
    reposcopy(name)
    autoreconf(
        '-s',
    )
    configure(
        '--disable-nls',
        '--with-drivers=all',
        'CFLAGS="{cflags} -D_DARWIN_C_SOURCE"'.format(cflags = os.getenv('CFLAGS')),
    )
    make_install(archive = name)

# LIBJPEG-TURBO ----------------------------------------------------------------

def build_libjpeg_turbo(name = 'libjpeg-turbo'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout('1.3.x')
    vsh(
"""
sed -i '' 's|$(datadir)/doc|&/libjpeg-turbo|' Makefile.am
""")
    autoreconf()
    configure(
        '--with-jpeg8',
    )
    make_install(archive = name)

# LIBPNG -----------------------------------------------------------------------

def build_libpng(name = 'libpng'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout('libpng16')
    autogen()
    configure()
    make_install(archive = name)

# LIBUSB -----------------------------------------------------------------------

def build_libusb(name = 'libusb'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    vsh(
"""
sed -i '' '/^.\\/configure/,$d' autogen.sh
""")
    autogen()
    configure()
    make_install(archive = name)
    build_libusb_compat()
    
def build_libusb_compat(name = 'libusb-compat-0.1'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    vsh(
"""
sed -i '' '/^.\\/configure/,$d' autogen.sh
""")
    autogen()
    configure()
    make_install(archive = name)

# LIBTIFF ----------------------------------------------------------------------

def build_libtiff(name = 'libtiff'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout('branch-3-9')
    configure(
        '--disable-jbig',
        '--disable-silent-rules',
        '--without-x',
    )
    make_install(archive = name)

# LITTLE-CMS -------------------------------------------------------------------

def build_lcms(name = 'Little-CMS'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    configure()
    make_install(archive = name)

# MPG123 -----------------------------------------------------------------------
# dependencies: SDL
#
def build_mpg123(name = 'mpg123'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    autoreconf()
    configure(
        '--with-default-audio=coreaudio',
        '--with-optimization=0',
    )
    make_install(archive = name)

# READLINE ---------------------------------------------------------------------

def build_readline(name = 'readline'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    patch(os.path.join(PROJECT_ROOT, 'osx-wine-patch/readline.patch'))
    configure(
        '--enable-multibyte',
        '--with-curses',
    )
    make_install(archive = name)

# SANE-BACKENDS ----------------------------------------------------------------
# dependencies: jpeg, libusb-compat, net-snmp, tiff, zlib
#
def build_net_snmp(name = 'net-snmp'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    configure(
        '--with-defaults',
    )
    make_install(archive=name)

def build_sane(name = 'sane-backends'):
    build_net_snmp()

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
        '--with-docdir=' + os.path.join(DOCDIR, name),
        '--without-v4l',
    )
    make_install(archive = name)

# SDL --------------------------------------------------------------------------

def build_SDL(name = 'SDL'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    hg_update('SDL-1.2')
    autogen()
    configure()
    make_install(archive = name)

# UNIXODBC ---------------------------------------------------------------------

def build_unixodbc(name = 'unixODBC'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    autoreconf(
        '-f',
    )
    configure()
    make_install(archive = name)

# WINE -------------------------------------------------------------------------

def build_wine(name = 'wine'):
    message(name)
    if binCheck(name) is False:
        reposcopy(name)
        git_checkout()
        for f in os.listdir(PATCHROOT):
            if f.startswith('wine_'):
                patch(os.path.join(PATCHROOT, f))
        configure(
            '--without-capi',
            '--without-oss',
            '--without-v4l',
            '--with-x',
            '--x-inc=/opt/X11/include',
            '--x-lib=/opt/X11/lib',
            'CC='  + CLANG,
            'CXX=' + CLANGXX,
            'CFLAGS="-arch i386 {0}"'.format(os.getenv('CFLAGS')),
            'CXXFLAGS="-arch i386 {0}"'.format(os.getenv('CXXFLAGS')),
            prefix = W_PREFIX,
        )
        make_install(archive = name)

    # note: add rpath
    vsh("""install_name_tool -add_rpath /opt/X11/lib {W_BINDIR}/wine""".format(**globals()))

    # note: rename executable
    os.rename(os.path.join(W_BINDIR,     'wine'),
              os.path.join(W_LIBEXECDIR, 'wine'))

    # note: install wine loader
    src = os.path.join(PROJECT_ROOT, 'wineloader.py.in')
    dst = os.path.join(W_BINDIR,     'wine')
    with open(src, 'r') as i:
        str = i.read()
        str = str.replace('___CAPTION___', 'Nihonshu - Customized Wine binary for OS X (Ja)')
        with open(dst, 'w') as o:
            o.write(str)
            os.chmod(dst, 0755)

    installDoc(
        name,
        'ANNOUNCE',
        'AUTHORS',
        'COPYING.LIB',
        'LICENSE',
        'README',
    )

# WINETRICKS / CABEXTRACT ------------------------------------------------------

def build_cabextract(name = 'cabextract-1.4'):
    message(name)
    extract(name, '.tar.gz')
    configure(prefix = W_PREFIX)
    make_install()
    installDoc(
        name,
        'AUTHORS',
        'COPYING',
        'README',
    )

def build_winetricks(name = 'winetricks'):
    build_cabextract()

    message(name)
    reposcopy(name)
    for f in os.listdir(PATCHROOT):
        if f.startswith('winetricks_'):
            patch(os.path.join(PATCHROOT, f))
    vsh("""make install PREFIX={W_PREFIX}""".format(**globals()))

    ### RENAME EXECUTABLE ###
    os.rename(os.path.join(W_BINDIR,     'winetricks'),
              os.path.join(W_LIBEXECDIR, 'winetricks'))

    ### INSTALL WINETRICKS LOADER ###
    installFile(os.path.join(PROJECT_ROOT, 'winetricksloader.py'),
                os.path.join(W_BINDIR,     'winetricks'), 0755)

    installDoc(
        name,
        'src/COPYING',
    )

# XZ ---------------------------------------------------------------------------

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

# ZLIB -------------------------------------------------------------------------

def build_zlib(name = 'zlib'):
    message(name)
    if binCheck(name): return
    reposcopy(name)
    git_checkout()
    vsh("""./configure --prefix={PREFIX}""".format(**globals()))
    make_install(archive = name)

#-------------------------------------------------------------------------------

def create_distfile():

    def create_distfile_clean():
        rm(os.path.join(W_DATADIR, 'applications'))
        for root, dirs, files in os.walk(W_LIBDIR):
            if root == os.path.join(W_LIBDIR, 'wine'): continue
            if root == W_LIBDIR:
                for d in dirs:
                    d = os.path.join(root, d)
                    if d.endswith((
                        'gettext',
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

    def create_distfile_core(distname):
        src = W_PREFIX
        dst = os.path.join(os.path.dirname(W_PREFIX), distname + '.exe')
        if os.path.exists(dst): rm(dst)
        p7zip('a', '-sfx', '-mx=9', dst, src)

    def create_distfile_rebuild_shared_libdir():
        rm(PREFIX)
        makedirs(PREFIX)
        os.symlink('../lib', LIBDIR)

    #---------------------------------------------------------------------------

    create_app = CreateApp()

    os.chdir(os.path.dirname(INSTALL_ROOT))
    create_distfile_clean()
    create_distfile_rebuild_shared_libdir()
    install_core_resources()
    create_app.nihonshu()

    ### no-plugin ##
    create_distfile_core('wine_nihonshu_no-plugin')

    ### plugin ##
    install_plugin()
    create_app.sevenzip()
    create_distfile_core('wine_nihonshu')

#-------------------------------------------------------------------------------

class CreateApp():

    def __init__(self):
        self.srcroot = os.path.join(PROJECT_ROOT, 'app')
        self.approot = os.path.join(W_PREFIX,     'app')
        makedirs(self.approot)

    def install_app(self, name, src):
        message(name)
        vsh(
"""
osacompile -x -o {dst} {src}
""".format(
        dst = os.path.join(self.approot, name),
        src = os.path.join(self.srcroot, src),
    ))

    def install_icon(self, name, src, suffix = 'Contents/Resources/droplet.icns'):
        installFile(os.path.join(self.srcroot, src),
                    os.path.join(self.approot, name, suffix))

    def install_plist(self, name, src, suffix = 'Contents/Info.plist'):
        installFile(os.path.join(self.srcroot, src),
                    os.path.join(self.approot, name, suffix))

    def nihonshu(self, name = 'Nihonshu.app'):
        self.install_app(  name, 'nihonshu.applescript')
        self.install_plist(name, 'nihonshu.info.plist.in')
        # todo
        os.remove(os.path.join(self.approot, name, 'Contents/Resources/droplet.icns'))

    def sevenzip(self, name = '7zFM.app'):
        self.install_app(  name, '7z.applescript')
        self.install_icon( name, '7z.icns')
        self.install_plist(name, '7z.info.plist.in')

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    os.system('declare')
    build_zlib()
    build_gsm()
    build_xz()
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
    create_distfile()
    os.system('echo done; afplay /System/Library/Sounds/Hero.aiff')
