import os
import sys
import subprocess

#-------------------------------------------------------------------------------

class Wine:

    def __init__(self):
        _prefix = os.path.join(WINE, '../..')
        _prefix = os.path.normpath(_prefix)
        self.plugindir = os.path.join(_prefix, 'share/wine/plugin')
        self.run('wineboot.exe', '-i')

    def run(self, *args, **kwargs):
        cmd = [WINE]
        cmd.extend(args)

        message(' '.join(cmd[1:]))

        if 'check' in kwargs and kwargs['check'] is False:
            subprocess.call(cmd)
        else:
            subprocess.check_call(cmd)

    def get_plugin_path(self, path):
        return os.path.join(self.plugindir, path)

    def regedit(self, path):
        self.run('regedit.exe', path)

    def regsvr32(self, *args):
        self.run('regsvr32.exe', *args)

    def rundll32(self, path, section = 'DefaultInstall'):
        self.run('rundll32.exe', 'setupapi.dll,InstallHinfSection', section, '128', path)

    def restart(self):
        self.run('wineboot.exe', '-r')

    def ver_win2k(self):
        self.regedit(wine.get_plugin_path('inf/win2k.reg'))

    def ver_winxp(self):
        self.regedit(wine.get_plugin_path('inf/winxp.reg'))


def message(string, mode = 0):
    if mode == 1:
        string = '\n*** %s ***\n' % string
    print >> sys.stderr, '\033[1;m' + string + '\033[m'


def fileCheck(*args):
    for f in args:
        if not os.path.exists(f): return False
    return True

#-------------------------------------------------------------------------------

def load_osx_inf():
    inf = wine.get_plugin_path('inf/osx-wine.inf')
    message('Registration files for Japanese', 1)
    wine.rundll32(inf)

#-------------------------------------------------------------------------------

def load_7z():
    inf = wine.get_plugin_path('inf/7z.inf')
    if not fileCheck(inf): return
    message('Registration files for 7-Zip', 1)
    wine.rundll32(inf)

#-------------------------------------------------------------------------------

def load_dx9():

    def load_dx9_feb2010():
        ### 2k mode ###
        message('Install DirectX 9 (1/3)', 1)
        wine.rundll32(inf)
        wine.ver_win2k()
        wine.run(src_dx9_feb2010, '/silent', check = False)
        wine.ver_winxp()
        wine.restart()

        ### XP mode ###
        message('Install DirectX 9 (2/3)', 1)
        wine.run(src_dx9_feb2010, '/silent', check = False)
        wine.restart()

    def load_dx9_jun2010():
        message('Install DirectX 9 (3/3)', 1)
        wine.run(src_dx9_jun2010, '/silent', check = False)
        wine.restart()

        registerdlls = [
            'amstream.dll'      ,
            'bdaplgin.ax'       ,
            'devenum.dll'       ,
            'diactfrm.dll'      ,
            'dinput8.dll'       ,
            'dinput.dll'        ,
            'dmband.dll'        ,
            'dmcompos.dll'      ,
            'dmime.dll'         ,
            'dmloader.dll'      ,
            'dmscript.dll'      ,
            'dmstyle.dll'       ,
            'dmsynth.dll'       ,
            'dmusic.dll'        ,
            'dplayx.dll'        ,
            'dpnet.dll'         ,
            'dpnhpast.dll'      ,
            'dpnhupnp.dll'      ,
            'dpvacm.dll'        ,
            'dpvoice.dll'       ,
            'dpvvox.dll'        ,
            'dsdmoprp.dll'      ,
            'dsdmo.dll'         ,
            'dswave.dll'        ,
            'dx7vb.dll'         ,
            'dx8vb.dll'         ,
            'dxdiagn.dll'       ,
            'encapi.dll'        ,
            'ipsink.ax'         ,
            'ksolay.ax'         ,
            'ksproxy.ax'        ,
            'kswdmcap.ax'       ,
            'l3codecx.ax'       ,
            'mpeg2data.ax'      ,
            'mpg2splt.ax'       ,
            'msdvbnp.ax'        ,
#            'msvidctl.dll'      , # Failed
            'mswebdvd.dll'      ,
            'psisdecd.dll'      ,
            'psisrndr.ax'       ,
            'qasf.dll'          ,
            'qcap.dll'          ,
            'qdvd.dll'          ,
            'qdv.dll'           ,
            'qedit.dll'         ,
            'quartz.dll'        ,
            'vbisurf.ax'        ,
            'wstdecod.dll'      ,
            'xactengine2_0.dll' ,
            'xactengine2_1.dll' ,
            'xactengine2_2.dll' ,
            'xactengine2_3.dll' ,
            'xactengine2_4.dll' ,
            'xactengine2_5.dll' ,
            'xactengine2_6.dll' ,
            'xactengine2_7.dll' ,
            'xactengine2_8.dll' ,
            'xactengine2_9.dll' ,
            'xactengine2_10.dll',
            'xactengine3_0.dll' ,
            'xactengine3_1.dll' ,
            'xactengine3_2.dll' ,
            'xactengine3_3.dll' ,
            'xactengine3_4.dll' ,
            'xactengine3_5.dll' ,
            'xactengine3_6.dll' ,
            'xactengine3_7.dll' ,
            'xaudio2_0.dll'     ,
            'xaudio2_1.dll'     ,
            'xaudio2_2.dll'     ,
            'xaudio2_3.dll'     ,
            'xaudio2_4.dll'     ,
            'xaudio2_5.dll'     ,
            'xaudio2_6.dll'     ,
            'xaudio2_7.dll'     ,
        ]
        wine.regsvr32(*registerdlls)

    #---------------------------------------------------------------------------

    inf             = wine.get_plugin_path('inf/dxredist.inf')
    src_dx9_feb2010 = wine.get_plugin_path('directx9/feb2010/dxsetup.exe')
    src_dx9_jun2010 = wine.get_plugin_path('directx9/jun2010/dxsetup.exe')

    if not fileCheck(
        inf,
        src_dx9_feb2010,
        src_dx9_jun2010,
    ): return

    load_dx9_feb2010()
    load_dx9_jun2010()

#-------------------------------------------------------------------------------

def load_vsrun():

    def load_vbrun6():
        message('Install VB 6.0 runtime', 1)
        wine.rundll32(inf)
        wine.run(src_vbrun6, '/Q', check = False)
        wine.restart()

    def load_vcrun6():
        message('Install VC 6.0 runtime', 1)
        wine.run(src_vcrun6, '/Q', check = False)
        wine.restart()

    def load_vcrun2005():
        message('Install VC 2005 runtime', 1)
        wine.run(src_vcrun2005, '/q')
        wine.restart()

    def load_vcrun2008():
        message('Install VC 2008 runtime', 1)
        wine.run(src_vcrun2008, '/q')
        wine.restart()

    def load_vcrun2010():
        message('Install VC 2010 runtime', 1)
        wine.run(src_vcrun2010, '/q')
        wine.restart()

    #---------------------------------------------------------------------------

    inf           = wine.get_plugin_path('inf/vsredist.inf')
    src_vbrun6    = wine.get_plugin_path('vbrun6sp6/vbrun60.exe')
    src_vcrun6    = wine.get_plugin_path('vcrun6sp6/vcredist.exe')
    src_vcrun2005 = wine.get_plugin_path('vcrun2005sp1_jun2011/vcredist_x86.exe')
    src_vcrun2008 = wine.get_plugin_path('vcrun2008sp1_jun2011/vcredist_x86.exe')
    src_vcrun2010 = wine.get_plugin_path('vcrun2010sp1_aug2011/vcredist_x86.exe')

    if not fileCheck(
        inf,
        src_vbrun6,
        src_vcrun6,
        src_vcrun2005,
        src_vcrun2008,
        src_vcrun2010,
    ): return

    load_vbrun6()
    load_vcrun6()
    load_vcrun2005()
    load_vcrun2008()
    load_vcrun2010()

#-------------------------------------------------------------------------------

if __name__ == 'init_wine':

    wine = Wine()

    ### PHASE 1 ###
    if sys.argv[1] == '--skip-init': sys.exit(0)

    ### PHASE 2 ###
    load_osx_inf()
    if sys.argv[1] == '--suppress-init': sys.exit(0)

    ### PHASE 3 ###
    load_7z()
    load_vsrun()
    load_dx9()
    if sys.argv[1] == '--force-init': sys.exit(0)
