import os
import sys
import subprocess

#-------------------------------------------------------------------------------

def get_stdout(*args):
  ps      = subprocess.Popen(args, stdout=subprocess.PIPE)
  stdout  = ps.communicate()[0].strip()
  retcode = ps.returncode
  if retcode != 0:
    print >> sys.stderr, 'error: %s' % ' '.join(args)
    sys.exit(retcode)
  return stdout

def mp_cmd(arg):
  cmd = '''
PATH={prefix}/bin type -P {name}
'''.format(
    prefix = MP_PREFIX,
    name   = arg,
  )
  f = get_stdout('sh', '-c', cmd)
  return f

#-------------------------------------------------------------------------------

def set_sdk():
    global dev_dir, osx_ver, sdkroot

    dev_dir = get_stdout('xcode-select', '-print-path')
    osx_ver = get_stdout('sw_vers', '-productVersion')[0:4]
    sdkroot = subprocess.Popen(['sh', '-ev'],
                               stdin  = subprocess.PIPE,
                               stdout = subprocess.PIPE).communicate(
"""
xcodebuild -version -sdk macosx{osx_ver} | sed -n '/^Path: /s///p'
""".format(**globals()))[0].strip()

    os.environ.update({
        'DEVELOPER_DIR'           : dev_dir,
        'MACOSX_DEPLOYMENT_TARGET': osx_ver,
        'SDKROOT'                 : sdkroot,
    })

#-------------------------------------------------------------------------------

class Autotools(object):

  def __init__(self):
    self.autotools_path =':'.join(
"""
{0}/libexec/gnubin
{0}/bin
{0}/sbin
/usr/bin
/bin
/usr/sbin
/sbin
""".format(MP_PREFIX).split())

  def run(self, args):
    vsh(
"""
PATH={path} NOCONFIGURE=1 {args}
""".format(
      path = self.autotools_path,
      args = ' '.join(args)
    ))

  def autogen(self, *args):
    cmd = ['./autogen.sh']
    cmd.extend(args)
    self.run(cmd)

  def autoreconf(self, *args):
    cmd = ['autoreconf', '-v', '-i']
    cmd.extend(args)
    self.run(cmd)

  def make(self, *args):
    cmd = ['make']
    cmd.extend(args)
    self.run(cmd)
  


def cabextract(*args):
    cmd = [CABEXTRACT]
    cmd.extend(args)
    subprocess.check_call(cmd)

def git_checkout(branch = 'master'):
    cmd = [GIT, 'checkout', '-f', branch]
    subprocess.check_call(cmd)

def hg_update(branch = 'default'):
    cmd = [HG, 'update', '-C', branch]
    subprocess.check_call(cmd)

def p7zip(*args):
    cmd = [P7ZIP]
    cmd.extend(args)
    subprocess.check_call(cmd)

def vsh(script):
    ps = subprocess.Popen(['sh', '-ve'], stdin = subprocess.PIPE)
    ps.communicate(script)
    retcode = ps.returncode
    if retcode != 0: sys.exit(retcode)

#-------------------------------------------------------------------------------

def set_compiler():

    def X(strings):
        return ' '.join(strings.format(**globals()).split())

    os.environ['CC']          = GCC
    os.environ['CXX']         = GXX
    os.environ['CCACHE_PATH'] = os.path.join(MP_PREFIX, 'bin')
    
    os.environ['CFLAGS']      = X("""
                                  -O3 -mtune=generic
                                  -isysroot {sdkroot}
                                  """)
    os.environ['CXXFLAGS']    = os.getenv('CFLAGS')
    os.environ['CPPFLAGS']    = X("""
                                  -I{PREFIX}/include
                                  """)
    os.environ['LDFLAGS']     = X("""
                                  -Wl,-headerpad_max_install_names
                                  -Wl,-syslibroot,{sdkroot}
                                  -Wl,-arch,i386
                                  -L{PREFIX}/lib
                                  """)

#-------------------------------------------------------------------------------

def set_env():
    os.environ['PATH'] = ':'.join(
"""
{MP_PREFIX}/libexec/ccache
{MP_PREFIX}/libexec/gnubin
{MP_PREFIX}/libexec/git-core
{PREFIX}/bin
/usr/bin
/bin
/usr/sbin
/sbin
""".format(**globals()).split())

    os.environ['SHELL']           = '/bin/bash'
    os.environ['TERM']            = 'xterm'
    os.environ['COMMAND_MODE']    = 'unix2003'
    os.environ['LANG']            = 'ja_JP.UTF-8'
    os.environ['gt_cv_locale_ja'] = 'ja_JP.UTF-8'

    os.environ['MAKE']            = mp_cmd('gmake')
    os.environ['FONTFORGE']       = mp_cmd('fontforge')
    os.environ['HELP2MAN']        = mp_cmd('help2man')
    os.environ['NASM']            = mp_cmd('nasm')
    os.environ['YASM']            = mp_cmd('yasm')

    os.environ['PKG_CONFIG']      = mp_cmd('pkg-config')
    os.environ['PKG_CONFIG_LIBDIR'] = ':'.join(
"""
{PREFIX}/lib/pkgconfig
{PREFIX}/share/pkgconfig
/usr/lib/pkgconfig
""".format(**globals()).split())

    os.environ['ACLOCAL_PATH'] = ':'.join(
"""
{MP_PREFIX}/share/aclocal
{PREFIX}/share/aclocal
""".format(**globals()).split())

#-------------------------------------------------------------------------------

PREFIX      = None
MP_PREFIX   = '/opt/local'

GCC         = os.path.basename(mp_cmd('i686-apple-darwin10-gcc-apple-4.2.1'))
GXX         = os.path.basename(mp_cmd('i686-apple-darwin10-g++-apple-4.2.1'))
CLANG       = os.path.basename(mp_cmd('clang-mp-3.3'))
CLANGXX     = os.path.basename(mp_cmd('clang++-mp-3.3'))

CABEXTRACT  = mp_cmd('cabextract')
GIT         = mp_cmd('git')
HG          = mp_cmd('hg')
P7ZIP       = mp_cmd('7z')

def main():
    set_sdk()
    set_env()
    set_compiler()
