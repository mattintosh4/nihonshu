import os
import sys
import subprocess

PREFIX    = None
MP_PREFIX = '/opt/local'

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

def env_append(key, value, separator=' '):
  if key in os.environ:
    os.environ[key] += separator + value
  else:
    os.environ[key] = value

#-------------------------------------------------------------------------------

def set_sdk():
  global dev_dir, osx_ver, sdkroot

  dev_dir = get_stdout('xcode-select', '-print-path')
  osx_ver = get_stdout('sw_vers', '-productVersion')[0:4]
  sdkroot = subprocess.Popen(['sh', '-ev'], stdin  = subprocess.PIPE,
                                            stdout = subprocess.PIPE).communicate("""
xcodebuild -version -sdk macosx%s | sed -n '/^Path: /s///p'
""" % osx_ver)[0].strip()

  os.environ.update({
    'DEVELOPER_DIR'             : dev_dir,
    'MACOSX_DEPLOYMENT_TARGET'  : osx_ver,
    'SDKROOT'                   : sdkroot,
  })

#-------------------------------------------------------------------------------

GCC        = os.path.basename(mp_cmd('i686-apple-darwin10-gcc-apple-4.2.1'))
GXX        = os.path.basename(mp_cmd('i686-apple-darwin10-g++-apple-4.2.1'))
CLANG      = os.path.basename(mp_cmd('clang-mp-3.3'))
CLANGXX    = os.path.basename(mp_cmd('clang++-mp-3.3'))

CABEXTRACT = mp_cmd('cabextract')
GIT        = mp_cmd('git')
HG         = mp_cmd('hg')
P7ZIP      = mp_cmd('7z')

AUTOTOOLS_PATH = \
':'.join([
  os.path.join(MP_PREFIX, 'bin'),
  os.path.join(MP_PREFIX, 'sbin'),
  '/usr/bin:/bin:/usr/sbin:/sbin',
])

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

#-------------------------------------------------------------------------------

def set_compiler():
  
  global archflags
  global optflags
  
#  archflags = '-m32 -arch i386'
  optflags  = '-O3 -mtune=generic'

#  env_append('CFLAGS', archflags)
  env_append('CFLAGS', optflags)
  env_append('CFLAGS', '-isysroot %s' % sdkroot)

  env_append('CPPFLAGS', '-I' + os.path.join(PREFIX, 'include'))

  env_append('LDFLAGS', '-Wl,-search_paths_first,-headerpad_max_install_names')
  env_append('LDFLAGS', '-Wl,-syslibroot,%s' % sdkroot)
  env_append('LDFLAGS', '-Wl,-arch,i386')
  env_append('LDFLAGS', '-L' + os.path.join(PREFIX, 'lib'))

  os.environ['CC']          = GCC
  os.environ['CXX']         = GXX
  os.environ['CXXFLAGS']    = os.getenv('CFLAGS')
  os.environ['CCACHE_PATH'] = os.path.join(MP_PREFIX, 'bin')

#-------------------------------------------------------------------------------

def set_env():
  os.environ['PATH'] = \
':'.join("""
{mp_prefix}/libexec/ccache
{mp_prefix}/libexec/gnubin
{mp_prefix}/libexec/git-core
{prefix}/bin
/usr/bin
/bin
/usr/sbin
/sbin
""".format(
    mp_prefix = MP_PREFIX,
    prefix    = PREFIX,
  ).split())

  os.environ['SHELL']           = '/bin/bash'
  os.environ['TERM']            = 'xterm'
  os.environ['COMMAND_MODE']    = 'unix2003'
  os.environ['LANG']            = 'ja_JP.UTF-8'
  os.environ['gt_cv_locale_ja'] = 'ja_JP.UTF-8'

  os.environ['ACLOCAL']         = mp_cmd('aclocal')
  os.environ['AUTOCONF']        = mp_cmd('autoconf')
  os.environ['AUTOHEADER']      = mp_cmd('autoheader')
  os.environ['AUTOM4TE']        = mp_cmd('autom4te')
  os.environ['AUTOMAKE']        = mp_cmd('automake')
  os.environ['AUTOPOINT']       = mp_cmd('autopoint')
  os.environ['INSTALL']         = mp_cmd('ginstall')
  os.environ['LIBTOOLIZE']      = mp_cmd('glibtoolize')
  os.environ['M4']              = mp_cmd('gm4')
  os.environ['MAKE']            = mp_cmd('gmake')
  os.environ['PKG_CONFIG']      = mp_cmd('pkg-config')

  os.environ['FONTFORGE']       = mp_cmd('fontforge')
  os.environ['HELP2MAN']        = mp_cmd('help2man')
  os.environ['NASM']            = mp_cmd('nasm')
  os.environ['YASM']            = mp_cmd('yasm')

  os.environ['ACLOCAL_PATH'] = \
':'.join("""
{0}/share/aclocal
{1}/share/aclocal
""".format(MP_PREFIX, PREFIX).split())

  os.environ['PKG_CONFIG_LIBDIR'] = \
':'.join("""
{0}/lib/pkgconfig
{0}/share/pkgconfig
/usr/lib/pkgconfig
""".format(PREFIX).split())

#-------------------------------------------------------------------------------

def set_symlink():
  bindir = os.path.join(PREFIX, 'bin')
  os.path.exists(bindir) or os.makedirs(bindir)
  
  for f in [
    GIT,
  ]:
    src = f
    dst = os.path.join(bindir, os.path.basename(f))
    os.symlink(src, dst)

#-------------------------------------------------------------------------------

def main():
  set_sdk()
  set_env()
  set_compiler()
  set_symlink()