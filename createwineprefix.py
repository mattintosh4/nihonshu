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

    def override(self, name, mode):
        message("overriding {name} to {mode}".format(**locals().copy()))
        subprocess.Popen([WINE, "regedit.exe", "-"],
                         stdin=subprocess.PIPE).communicate("""\
[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]
"{name}"="{mode}"
""".format(**locals().copy()))

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
    cabextract_cmd = os.path.normpath(os.path.join(WINE, "../../bin/cabextract"))
    cmd = [cabextract_cmd, "-q", "-L"]
    cmd.extend(args)
    message(" ".join(cmd))
    subprocess.check_call(cmd)


def winetricks(*args):
    winetricks_cmd = os.path.normpath(os.path.join(WINE, "../../bin/winetricks"))
    cmd = [winetricks_cmd]
    cmd.extend(args)
    message(" ".join(cmd))
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

    def items_append(archive, regist=False, override=False, mode=False):
        items.append(locals().copy())

    message('Install extra resources', 1)
    xpsp3  = os.path.expanduser('~/.cache/winetricks/xpsp3jp/WindowsXP-KB936929-SP3-x86-JPN.exe')
    w_temp = os.path.join(W_TEMP, 'xpsp3')
    items  = []
#    items_append("asms/10/msft/windows/gdiplus/gdiplus.dll", override="gdiplus", mode="builtin,native")
#    items_append("devmgr.dl_")
    items_append("dxmasf.dl_",      "dxmasf.dll")
    items_append("dxtmsft.dl_",     "dxtmsft.dll")
    items_append("dxtrans.dl_",     "dxtrans.dll")
    items_append("mciavi32.dl_",    override="mciavi32",    mode="native,builtin")
    items_append("mciseq.dl_",      override="mciseq",      mode="native,builtin")
    items_append("mciwave.dl_",     override="mciwave",     mode="native,builtin")
    items_append("mp4sdmod.dl_",    "mp4sdmod.dll")
    items_append("mp43dmod.dl_",    "mp43dmod.dll")
    items_append("mpg4dmod.dl_",    "mpg4dmod.dll")
    items_append("msacm32.dl_",     override="msacm32",     mode="native,builtin")
    items_append("msvfw32.dl_",     override="msvfw32",     mode="native,builtin")
    items_append("riched20.dl_",    override="riched20",    mode="builtin,native")
    items_append("shell32.dl_",     override="shell32",     mode="builtin,native")

    ## ax
    items_append("mpg2data.ax_",    "mpg2data.ax")
    items_append("mpg2splt.ax_",    "mpg2splt.ax")
    items_append("mpg4ds32.ax_",    "mpg4ds32.ax")
    items_append("wmv8ds32.ax_",    "wmv8ds32.ax")
    items_append("wmvds32.ax_",     "wmvds32.ax")

    ## ocx
    items_append("hhctrl.oc_",      override="hhctrl.ocx",  mode="builtin,native")

    ## cpl
    items_append("joy.cp_",         override="joy.cpl",     mode="builtin,native")
    items_append("odbccp32.cp_")
    items_append("timedate.cp_")

    ## odbc
    items_append("msjet40.dl_") # from odbcjt32.dll
    items_append("mswstr10.dl_",    "msjet40.dll") # from odbcjt32.dll

    items_append("odbc32gt.dl_")
    items_append("odbc32.dl_",      override="odbc32",      mode="native,builtin")
    items_append("odbcad32.ex_")
    items_append("odbcbcp.dl_")
    items_append("odbcconf.dl_",    "odbcconf.dll")
    items_append("odbcconf.ex_")
    items_append("odbccp32.dl_",    override="odbccp32",    mode="native,builtin")
    items_append("odbccr32.dl_")
    items_append("odbccu32.dl_",    override="odbccu32",    mode="native,builtin")
    items_append("odbcint.dl_")
    items_append("odbcji32.dl_")
    items_append("odbcjt32.dl_")
    items_append("odbcp32r.dl_")
    items_append("odbctrac.dl_")

    winetricks("glu32")

    for d in items:
        if d["override"]:
            wine.override(d["override"], d["mode"])
        cabextract("-d", w_temp, "-F", "i386/" + d["archive"], xpsp3)
        if d["archive"].endswith("_"):
            cabextract("-d", W_SYSTEM32, os.path.join(w_temp, "i386/" + d["archive"]))
        else:
            src = os.path.join(w_temp, "i386", d["archive"])
            dst = os.path.join(W_SYSTEM32,     d["archive"])
            if os.path.exists(dst): os.remove(dst)
            os.rename(src, dst)

    for d in items:
        if d["regist"]:
            wine.regsvr32(d["regist"])

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
#                load_xpsp3() # todo
                if opt != '--force-init':
                    break
        sys.exit(0)

#-------------------------------------------------------------------------------

if __name__ == 'createwineprefix':
    wine = Wine()
    main(sys.argv[1])
