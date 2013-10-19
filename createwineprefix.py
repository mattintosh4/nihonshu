# -*- coding: utf-8 -*-

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
        global W_WINDOWS, W_FONTS, W_SYSTEM32, W_TEMP

        W_WINDOWS  = subprocess.Popen([WINE, "winepath.exe", "c:\\windows"],
                                       stdout=subprocess.PIPE,
                                       stderr=open(os.devnull, "w")).communicate()[0].strip()
        W_FONTS    = os.path.join(W_WINDOWS, "Fonts")
        W_SYSTEM32 = os.path.join(W_WINDOWS, "system32")
        W_TEMP     = os.path.join(W_WINDOWS, "temp")

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
"*{name}"="{mode}"
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
    message('日本語用 INF ファイルを登録しています', 1)
    wine.rundll32(inf)

#-------------------------------------------------------------------------------

def load_7z():
    inf = wine.get_plugin_path('inf/7z.inf')
    if not fileCheck(inf): return
    message('7-Zip 用 INF ファイルを登録しています', 1)
    wine.rundll32(inf)

#-------------------------------------------------------------------------------

def load_dx9():

    def load_dx9_feb2010():
        ### 2k mode ###
        message('DirectX 9 をインストールしています (1/3)', 1)
        wine.rundll32(inf)
        wine.ver_win2k()
        wine.run(src_dx9_feb2010, '/silent', check = False)
        wine.ver_winxp()
        wine.restart()

        ### XP mode ###
        message('DirectX 9 をインストールしています (2/3)', 1)
        wine.run(src_dx9_feb2010, '/silent', check = False)
        wine.restart()

    def load_dx9_jun2010():
        message('DirectX 9 をインストールしています (3/3)', 1)
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

    load_xpsp3() # todo

#-------------------------------------------------------------------------------

def load_vsrun():

    def load_vbrun6():
        message('Visual Basic 6.0 ランタイムをインストールしています', 1)
        wine.rundll32(inf)
        wine.run(src_vbrun6, '/Q', check = False)
        wine.restart()

    def load_vcrun6():
        message('Visual C++ 6.0 ランタイムをインストールしています', 1)
        wine.run(src_vcrun6, '/Q', check = False)
        cabextract('-d', W_SYSTEM32, '-F', 'mfc42u.dll', src_vcrun6)
        wine.regsvr32('mfc42u.dll')
        wine.restart()

    def load_vcrun2005():
        message('Visual C++ 2005 ランタイムをインストールしています', 1)
        wine.run(src_vcrun2005, '/q')
        wine.restart()

    def load_vcrun2008():
        message('Visual C++ 2008 ランタイムをインストールしています', 1)
        wine.run(src_vcrun2008, '/q')
        wine.restart()

    def load_vcrun2010():
        message('Visual C++ 2010 ランタイムをインストールしています', 1)
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

    xpsp3  = os.path.expanduser("~/.cache/winetricks/xpsp3jp/WindowsXP-KB936929-SP3-x86-JPN.exe")
    w_temp = os.path.join(W_TEMP, "xpsp3")
    items  = []

    def items_append(archive, regist=False, override=False, mode=False):
        items.append(locals().copy())

    def _dll_devel():
        items_append("ddrawex.dl_"  ,"ddrawex.dll"  ,"ddrawex"      ,"native")
        items_append("asms/10/msft/windows/gdiplus/gdiplus.dll"
                                    ,False          ,"gdiplus"      ,"builtin,native")
        items_append("mciavi32.dl_" ,False          ,"mciavi32"     ,"native")
        items_append("mciqtz32.dl_" ,False          ,"mciqtz32"     ,"native")
        items_append("mciseq.dl_"   ,False          ,"mciseq"       ,"native")
        items_append("mciwave.dl_"  ,False          ,"mciwave"      ,"native")
        items_append("msacm32.dl_"  ,False          ,"msacm32"      ,"native")
        items_append("msadp32.ac_"  ,False          ,"msadp32.acm"  ,"native")
        items_append("msaud32.ac_")
        items_append("msvfw32.dl_"  ,False          ,"msvfw32"      ,"native")
        items_append("riched20.dl_" ,False          ,"riched20"     ,"builtin,native")

        ## odbc
        items_append("msjet40.dl_"  ,"msjet40.dll") # from odbcjt32.dll
        items_append("mswstr10.dl_")                # from odbcji32.dll
        items_append("odbc32gt.dl_")
        items_append("odbc32.dl_"   ,False          ,"odbc32"       ,"native,builtin")
        items_append("odbcad32.ex_")
        items_append("odbcbcp.dl_")
        items_append("odbcconf.dl_" ,"odbcconf.dll")
        items_append("odbcconf.ex_")
        items_append("odbccp32.dl_" ,False          ,"odbccp32"     ,"native,builtin")
        items_append("odbccr32.dl_")
        items_append("odbccu32.dl_" ,False          ,"odbccu32"     ,"native,builtin")
        items_append("odbcint.dl_")
        items_append("odbcji32.dl_")
        items_append("odbcjt32.dl_")
        items_append("odbcp32r.dl_")
        items_append("odbctrac.dl_")
        items_append("odbccp32.cp_")

    def _dll_top_priority():
        items_append("mfc40u.dl_"   ,"mfc40u.dll")
        items_append("mfc42.dl_"    ,"mfc42.dll")
        items_append("mfc42u.dl_"   ,"mfc42u.dll")
        items_append("quartz.dl_"   ,"quartz.dll"   ,"quartz"       ,"native")
        sys.argv[1] in ["--devel"] and _dll_devel()

    def _dll_wmp():
        items_append("asferror.dl_")
        items_append("blackbox.dl_" ,"blackbox.dll")
        items_append("cewmdm.dl_"   ,"cewmdm.dll")
        items_append("drmstor.dl_"  ,"drmstor.dll")
        items_append("drmv2clt.dl_" ,"drmv2clt.dll")
        items_append("laprxy.dl_"   ,"laprxy.dll")
        items_append("logagent.ex_")
        items_append("mp4sdmod.dl_" ,"mp4sdmod.dll")
        items_append("mp43dmod.dl_" ,"mp43dmod.dll")
        items_append("mpg4dmod.dl_" ,"mpg4dmod.dll")
        items_append("msdmo.dl_")
        items_append("msnetobj.dl_" ,"msnetobj.dll")
        items_append("mspmsnsv.dl_" ,"mspmsnsv.dll")
        items_append("mspmsp.dl_"   ,"mspmsp.dll")
        items_append("msscp.dl_"    ,"msscp.dll")
        items_append("mswmdm.dl_"   ,"mswmdm.dll")
        items_append("qasf.dl_"     ,"qasf.dll")
        items_append("wmadmod.dl_"  ,"wmadmod.dll")
        items_append("wmadmoe.dl_"  ,"wmadmoe.dll")
        items_append("wmasf.dl_")
        items_append("wmdmlog.dl_"  ,"wmdmlog.dll")
        items_append("wmdmps.dl_"   ,"wmdmps.dll")
        items_append("wmerror.dl_")
        items_append("wmidx.dl_")
        items_append("wmnetmgr.dl_" ,"wmnetmgr.dll")
        items_append("wmpasf.dl_"   ,"wmpasf.dll")
        items_append("wmpcd.dl_"    ,"wmpcd.dll")
        items_append("wmpcore.dl_"  ,"wmpcore.dll")
        items_append("wmpdxm.dl_"   ,"wmpdxm.dll")
        items_append("wmploc.dl_")
        items_append("wmpshell.dl_" ,"wmpshell.dll")
        items_append("wmpui.dl_"    ,"wmpui.dll")
        items_append("wmp.dl_"      ,"wmp.dll")
        items_append("wmp.oc_"      ,"wmp.ocx")
        items_append("wmsdmod.dl_"  ,"wmsdmod.dll")
        items_append("wmsdmoe2.dl_" ,"wmsdmoe2.dll")
        items_append("wmspdmod.dl_" ,"wmspdmod.dll")
        items_append("wmspdmoe.dl_" ,"wmspdmoe.dll")
        items_append("wmvcore.dl_"  ,"wmvcore.dll"  ,"wmvcore"      ,"native,builtin")
        items_append("wmvdmod.dl_"  ,"wmvdmod.dll")
        items_append("wmvdmoe2.dl_" ,"wmvdmoe2.dll")
        items_append("l3codeca.ac_" ,"l3codeca.acm")

        #items_append("custsat.dl_")     # Program Files
        #items_append("mpvis.dl_")       # Program Files
        #items_append("npdrmv2.dl_")     # Program Files
        #items_append("npdrmv2.zi_")     # Program Files
        #items_append("wmpband.dl_")     # Program Files
        #items_append("wmplayer.ex_")    # program Files
        #items_append("wmpns.dl_")       # Program Files

    def _dll_standard():
        items_append("dxmasf.dl_"   ,"dxmasf.dll")
        items_append("dxtmsft.dl_"  ,"dxtmsft.dll")
        items_append("dxtrans.dl_"  ,"dxtrans.dll")
        items_append("shell32.dl_"  ,False          ,"shell32"      ,"builtin,native")
    
        ## ocx
        items_append("hhctrl.oc_"   ,False          ,"hhctrl.ocx"   ,"native")
    
        ## cpl
        items_append("joy.cp_"      ,False          ,"joy.cpl"      ,"builtin,native")
        items_append("timedate.cp_")
    
        ## ax
        items_append("dshowext.ax_")
        items_append("ip/vbicodec.ax_"  ,"vbicodec.ax")
        items_append("ip/wstpager.ax_"  ,"wstpager.ax")
        items_append("ip/wstrendr.ax_"  ,"wstrendr.ax")
        items_append("mpg2data.ax_" ,"mpg2data.ax")
        items_append("mpg2splt.ax_" ,"mpg2splt.ax")
        items_append("mpg4ds32.ax_" ,"mpg4ds32.ax")
        items_append("msadds32.ax_" ,"msadds32.ax")
        items_append("msdvbnp.ax_"  ,"msdvbnp.ax")
        items_append("msscds32.ax_" ,"msscds32.ax")
        items_append("psisrndr.ax_" ,"psisrndr.ax")
        items_append("vbisurf.ax_"  ,"vbisurf.ax")
        items_append("vidcap.ax_"   ,"vidcap.ax")
        items_append("wmv8ds32.ax_" ,"wmv8ds32.ax")
        items_append("wmvds32.ax_"  ,"wmvds32.ax")

    def _font():
        for f in [
            "ip/lsans.tt_",
            "ip/lsansd.tt_",
            "ip/lsansdi.tt_",
            "ip/lsansi.tt_",
            "kartika.tt_",
            "lang/simsun.tt_",
            "micross.tt_",
            "tunga.tt_",
            "vrinda.tt_",
        ]:
            cabextract("-d", W_FONTS, "-F", "i386/" + f, xpsp3)

    #---------------------------------------------------------------------------

    message("Windows XP Service Pack 3 から追加ファイルをインストールしています", 1)
    winetricks("glu32")
    if not os.path.exists(xpsp3): return
    _font()
    _dll_top_priority()
    _dll_standard()
    _dll_wmp()
    registerdlls = []
    for d in items:
        d["regist"]   and registerdlls.append(d["regist"])
        d["override"] and wine.override(d["override"], d["mode"])
        cabextract("-d", w_temp, "-F", "i386/" + d["archive"], xpsp3)
        if d["archive"].endswith("_"):
            cabextract("-d", W_SYSTEM32, os.path.join(w_temp, "i386/" + d["archive"]))
        else:
            src = os.path.join(w_temp, "i386", d["archive"])
            dst = os.path.join(W_SYSTEM32,     d["archive"])
            os.path.exists(dst) and os.remove(dst)
            os.rename(src, dst)
    wine.regsvr32(*registerdlls)
    shutil.rmtree(w_temp)

#-------------------------------------------------------------------------------

def main():
    while 1:
        if not sys.argv[1] in ["--skip-init"]:
            load_osx_inf()
            if not sys.argv[1] in ["--suppress-init"]:
                load_7z()
                load_vsrun()
                load_dx9()
                if not sys.argv[1] in ["--force-init", "--devel"]:
                    break
        sys.exit(0)

#-------------------------------------------------------------------------------

if __name__ == "createwineprefix":
    wine = Wine()
    main()
