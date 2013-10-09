import os
import sys
import subprocess

PREFIX      = None
WINE        = None
PLUGINDIR   = None

#-------------------------------------------------------------------------------

def message(string):
    print >> sys.stderr, '\033[33m*** %s ***\033[m' % string

def wine(*args, **kwargs):
    cmd = [WINE]
    cmd.extend(args)
    if 'check' in kwargs and kwargs['check'] is False:
        subprocess.call(cmd)
    else:
        subprocess.check_call(cmd)

def wine_restart():
    wine('wineboot.exe', '-r')

def regsvr32(*args):
    wine('regsvr32.exe', *args)

def rundll32(inf, section = 'DefaultInstall'):
    wine('rundll32.exe', 'setupapi.dll,InstallHinfSection', section, '128', inf)

def cabextract(*args):
    cmd = ['cabextract', '-q', '-L']
    cmd.extend(args)
    subprocess.check_call(cmd)

#-------------------------------------------------------------------------------

def load_7z():
    inf = os.path.join(PLUGINDIR, 'inf/7z.inf')
    if not os.path.exists(inf): return
    rundll32(inf)

def load_osx_inf():
    inf = os.path.join(PLUGINDIR, 'inf/osx-wine.inf')
    rundll32(inf)

def load_dx9():

    def load_dx9_feb2010():
        ### 2k mode ###
        message('Installing DirectX 9 (1/3)')
        wine('regedit.exe', os.path.join(PLUGINDIR, 'inf/win2k.reg'))
        wine(src_dx9_feb2010, '/silent', check = False)
        wine('regedit.exe', os.path.join(PLUGINDIR, 'inf/winxp.reg'))
        wine_restart()

        ### XP mode ###
        message('Installing DirectX 9 (2/3)')
        wine(src_dx9_feb2010, '/silent', check = False)
        wine_restart()

    def load_dx9_jun2010():
        message('Installing DirectX 9 (3/3)')
        wine(src_dx9_jun2010, '/silent', check = False)
        wine_restart()

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

    #---------------------------------------------------------------------------

    inf             = os.path.join(PLUGINDIR, 'inf/dxredist.inf')
    src_dx9_feb2010 = os.path.join(PLUGINDIR, 'directx9/feb2010/dxsetup.exe')
    src_dx9_jun2010 = os.path.join(PLUGINDIR, 'directx9/jun2010/dxsetup.exe')

    for f in [
        inf,
        src_dx9_feb2010,
        src_dx9_jun2010,
    ]:
        if not os.path.exists(f): return

    rundll32(inf)
    load_dx9_feb2010()
    load_dx9_jun2010()

#-------------------------------------------------------------------------------

def load_vsrun():

    def load_vbrun6():
        message('Installing Visual Basic 6.0')
        wine(src_vbrun6, '/Q', check = False)
        wine_restart()

    def load_vcrun6():
        message('Installing Visual C++ 6.0')
        wine(src_vcrun6, '/Q', check = False)
        wine_restart()

    def load_vcrun2005():
        message('Installing Visual C++ 2005')
        wine(src_vcrun2005, '/q')
        wine_restart()

    def load_vcrun2008():
        message('Installing Visual C++ 2008 SP 1')
        wine(src_vcrun2008, '/q')
        wine_restart()

    def load_vcrun2010():
        message('Installing Visual C++ 2010 SP 1')
        wine(src_vcrun2010, '/q')
        wine_restart()

    #---------------------------------------------------------------------------

    inf           = os.path.join(PLUGINDIR, 'inf/vsredist.inf')
    src_vbrun6    = os.path.join(PLUGINDIR, 'vbrun6sp6/vbrun60.exe')
    src_vcrun6    = os.path.join(PLUGINDIR, 'vcrun6sp6/vcredist.exe')
    src_vcrun2005 = os.path.join(PLUGINDIR, 'vcrun2005sp1_jun2011/vcredist_x86.exe')
    src_vcrun2008 = os.path.join(PLUGINDIR, 'vcrun2008sp1_jun2011/vcredist_x86.exe')
    src_vcrun2010 = os.path.join(PLUGINDIR, 'vcrun2010sp1_aug2011/vcredist_x86.exe')

    for f in [
        inf,
        src_vbrun6,
        src_vcrun6,
        src_vcrun2005,
        src_vcrun2008,
        src_vcrun2010,
    ]:
        if not os.path.exists(f): return

    rundll32(inf)
    load_vbrun6()
    load_vcrun6()
    load_vcrun2005()
    load_vcrun2008()
    load_vcrun2010()

#-------------------------------------------------------------------------------

def main():

    ### PHASE 1 ###
    wine('wineboot.exe', '--init')
    if sys.argv[1] == '--skip-init': sys.exit()

    ### PHASE 2 ###
    load_osx_inf()
    if sys.argv[1] == '--suppress-init': sys.exit()

    ### PHASE 3 ###
    load_7z()
    load_vsrun()
    load_dx9()
    if sys.argv[1] == '--force-init': sys.exit()
