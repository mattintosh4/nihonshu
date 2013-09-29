import os
import sys
from subprocess import *

PREFIX      = None
WINE        = None
PLUGINDIR   = None
TMPDIR      = os.path.expandvars('$TMPDIR')

#-------------------------------------------------------------------------------

def message(string):
    print >> sys.stderr, '\033[33m*** %s ***\033[m' % string

def wine(*args, **kwargs):
    cmd = [WINE]
    cmd.extend(args)
    if 'check' in kwargs and kwargs['check'] == False:
        call(cmd)
    else:
        check_call(cmd)

def regsvr32(*args):
    wine('regsvr32.exe', *args)

def rundll32(path, section='DefaultInstall'):
    if not os.path.exists(path):
        print >> sys.stderr, '%s not found' % path
        sys.exit(1)
    wine('rundll32.exe', 'setupapi.dll,InstallHinfSection', section, '128', path)

def cabextract(*args):
    cmd = ['cabextract', '-q', '-L']
    cmd.extend(args)
    check_call(cmd)

#-------------------------------------------------------------------------------

def load_inf():
    inf = os.path.join(PLUGINDIR, 'inf/osx-wine.inf')
    rundll32(inf)

def load_dx9():
    def load_dx9_feb2010():
        src = os.path.join(PLUGINDIR, 'directx9/feb2010/dxsetup.exe')
        if not os.path.exists(src): return
        inf = os.path.join(PLUGINDIR, 'inf/dxredist.inf')
        rundll32(inf)

        ### 2k mode ###
        message('Installing DirectX 9 (phase 1)')
        wine('regedit.exe', os.path.join(PLUGINDIR, 'inf/win2k.reg'))
        wine(src, '/silent', check=False)
        wine('regedit.exe', os.path.join(PLUGINDIR, 'inf/winxp.reg'))
        wine('wineboot.exe', '-r')

        ### XP mode ###
        message('Installing DirectX 9 (phase 2)')
        wine(src, '/silent', check=False)
        wine('wineboot.exe', '-r')

    def load_dx9_jun2010():
        src = os.path.join(PLUGINDIR, 'directx9/jun2010/dxsetup.exe')
        if not os.path.exists(src): return
        message('Installing DirectX 9 (phase 3)')
        wine(src, '/silent', check=False)
        wine('wineboot.exe', '-r')

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
        regsvr32(*registerdlls)

    load_dx9_feb2010()
    load_dx9_jun2010()

def load_vbrun():
    src = os.path.join(PLUGINDIR, 'vbrun60sp6/vbrun60sp6.exe')
    if not os.path.exists(src): return
    message('Installing Visual Basic 6.0 SP 6')
    wine(src, '/Q', check=False)

def load_vcrun():
    def load_vcrun60():
        src = os.path.join(PLUGINDIR, 'vcrun60/vcredist.exe')
        if not os.path.exists(src): return
        message('Installing Visual C++ 6.0')
        inf = os.path.join(PLUGINDIR, 'inf/vcredist.inf')
        rundll32(inf)
        wine(src, '/q', check=False)
        registerdlls = [
            'atl.dll'       ,
            'comcat.dll'    ,
            'mfc42.dll'     ,
            'oleaut32.dll'  ,
            'olepro32.dll'  ,
        ]
        regsvr32(*registerdlls)

    def load_vcrun2005():
        src = os.path.join(PLUGINDIR, 'vcrun2005/vcredist_x86.exe')
        if not os.path.exists(src): return
        message('Installing Visual C++ 2005')
        wine(src, '/q')

    def load_vcrun2008():
        src = os.path.join(PLUGINDIR, 'vcrun2008sp1/vcredist_x86.exe')
        if not os.path.exists(src): return
        message('Installing Visual C++ 2008 SP 1')
        wine(src, '/q')

    def load_vcrun2010():
        src = os.path.join(PLUGINDIR, 'vcrun2010sp1/vcredist_x86.exe')
        if not os.path.exists(src): return
        message('Installing Visual C++ 2010 SP 1')
        wine(src, '/q')

    load_vcrun60()
    load_vcrun2005()
    load_vcrun2008()
    load_vcrun2010()

#-------------------------------------------------------------------------------

def main():
    ### PHASE 1 ###
    wine('wineboot.exe', '--init')
    if sys.argv[1] == '--skip-init': sys.exit()

    ### PHASE 2 ###
    load_inf()
    if sys.argv[1] == '--suppress-init': sys.exit()

    ### PHASE 3 ###
    load_vcrun()
    load_vbrun()
    load_dx9()
    if sys.argv[1] == '--force-init': sys.exit()
