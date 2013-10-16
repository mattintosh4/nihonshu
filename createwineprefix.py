import os
import shutil
import subprocess
import sys

#-------------------------------------------------------------------------------

class Wine(object):

    def __init__(self):
        self.plugindir  = os.path.normpath(os.path.join(WINE, '../../share/wine/plugin'))
        self.run('wineboot.exe', '-i')
        self.set_windir()

    def set_windir(self):
        global W_WINDOWS, W_SYSTEM32, W_TEMP

        W_WINDOWS  = subprocess.Popen([WINE, 'winepath.exe', 'c:\\windows'],
                                       stdout=subprocess.PIPE,
                                       stderr=open(os.devnull, 'w')).communicate()[0].strip()
        W_SYSTEM32 = os.path.join(W_WINDOWS, 'system32')
        W_TEMP     = os.path.join(W_WINDOWS, 'temp')

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

    def restart(self):
        self.run('wineboot.exe', '-r')

    def rundll32(self, path, section = 'DefaultInstall'):
        self.run('rundll32.exe', 'setupapi.dll,InstallHinfSection', section, '128', path)

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

def cabextract(*args):
    cabextract_cmd = os.path.normpath(os.path.join(WINE, '../../bin/cabextract'))
    cmd = [cabextract_cmd, '-L']
    cmd.extend(args)
    ps = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    subprocess.Popen(['grep', 'extracting'], stdin=ps.stdout).communicate()[0]
    ps.stdout.close()

def winetricks(*args):
    winetricks_cmd = os.path.normpath(os.path.join(WINE, "../../bin/winetricks"))
    cmd = [winetricks_cmd]
    cmd.extend(args)
    subprocess.check_call(cmd)

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
        cabextract('-d', W_SYSTEM32, '-F' 'mfc42u.dll', src_vcrun6)
        wine.regsvr32('mfc42u.dll')
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

def load_xpsp3():
    xpsp3  = os.path.expanduser('~/.cache/wine/WindowsXP-KB936929-SP3-x86-JPN.exe')
    w_temp = os.path.join(W_TEMP, 'xpsp3')

    if not os.path.exists(xpsp3): return

    message('Install extra resources', 1)

    items = []
    items.append(["asms/10/msft/windows/gdiplus/gdiplus.dll", ""])
#    items.append(["devmgr.dl_",     ""])
    items.append(["dxmasf.dl_",     "dxmasf.dll"])
    items.append(["dxtmsft.dl_",    "dxtmsft.dll"])
    items.append(["dxtrans.dl_",    "dxtrans.dll"])
    items.append(["glu32.dl_",      ""])
    items.append(["mciavi32.dl_",   ""])
    items.append(["mciseq.dl_",     ""])
    items.append(["mciwave.dl_",    ""])
    items.append(["mp4sdmod.dl_",   "mp4sdmod.dll"])
    items.append(["mp43dmod.dl_",   "mp43dmod.dll"])
    items.append(["mpg4dmod.dl_",   "mpg4dmod.dll"])
    items.append(["msacm32.dl_",    ""])
    items.append(["msjet40.dl_",    ""]) # from odbcjt32.dll
    items.append(["msvfw32.dl_",    ""])
    items.append(["mswstr10.dl_",   "msjet40.dll"]) # from odbcjt32.dll
    items.append(["odbc32gt.dl_",   ""])
    items.append(["odbc32.dl_",     ""])
    items.append(["odbcad32.ex_",   ""])
    items.append(["odbcbcp.dl_",    ""])
    items.append(["odbcconf.dl_",   "odbcconf.dll"])
    items.append(["odbcconf.ex_",   ""])
    items.append(["odbccp32.dl_",   ""])
    items.append(["odbccr32.dl_",   ""])
    items.append(["odbccu32.dl_",   ""])
    items.append(["odbcint.dl_",    ""])
    items.append(["odbcji32.dl_",   ""])
    items.append(["odbcjt32.dl_",   ""])
    items.append(["odbcp32r.dl_",   ""])
    items.append(["odbctrac.dl_",   ""])
    items.append(["riched20.dl_",   ""])
    items.append(["shell32.dl_",    ""])

    ## ax
    items.append(["mpg2data.ax_",   "mpg2data.ax"])
    items.append(["mpg2splt.ax_",   "mpg2splt.ax"])
    items.append(["mpg4ds32.ax_",   "mpg4ds32.ax"])
    items.append(["wmv8ds32.ax_",   "wmv8ds32.ax"])
    items.append(["wmvds32.ax_",    "wmvds32.ax"])

    ## ocx
    items.append(["hhctrl.oc_",     "hhctrl.ocx"])

    ## cpl
#    items.append(["hdwwiz.cp_",     ""])
    items.append(["joy.cp_",        ""])
#    items.append(["mmsys.cp_",      ""])
    items.append(["odbccp32.cp_",   ""])
    items.append(["timedate.cp_",   ""])

    reg = """[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]
"gdiplus"    = "builtin,native"
"hhctrl.ocx" = "native,builtin"
"joy.cpl"    = "builtin,native"
"odbc32"     = "native,builtin"
"odbccp32"   = "native,builtin"
"odbccu32"   = "native,builtin"
"riched20"   = "builtin,native"
"shell32"    = "builtin,native"
"""
    subprocess.Popen([WINE, "regedit.exe", "-"], stdin=subprocess.PIPE).communicate(reg)

    for f in items:
        f = "i386/" + f[0]
        cabextract("-d", w_temp, "-F", f, xpsp3)
        if f.endswith("_"):
            cabextract("-d", W_SYSTEM32, os.path.join(w_temp, f))
        else:
            src = os.path.join(w_temp, f)
            dst = os.path.join(W_SYSTEM32, os.path.basename(f))
            if os.path.exists(dst): os.remove(dst)
            os.rename(src, dst)

    for f in items:
        f = f[1]
        if f: wine.regsvr32(f)

    shutil.rmtree(w_temp)

#-------------------------------------------------------------------------------

def main(opt):
    while 1:
        if opt != '--skip-init':
            load_osx_inf()
            if opt != '--suppress-init':
                load_7z()
                load_vsrun()
                load_dx9()
                load_xpsp3()
                if opt != '--force-init':
                    break
        sys.exit(0)

#-------------------------------------------------------------------------------

if __name__ == 'createwineprefix':
    wine = Wine()
    main(sys.argv[1])
