#-*-coding:utf-8-*-
import datetime, sys, time, binascii, os, zipfile, getpass
import xml.etree.ElementTree as ET


def make_zipfile(ssid_name) :
    try:
        os.remove(ssid_name+".zip")
    except FileNotFoundError:
        pass


    _zip = zipfile.ZipFile(ssid_name+".zip", "w")
    for folder, subfolders, files in os.walk(ssid_name):
        for file in files:
            _zip.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), ssid_name), compress_type = zipfile.ZIP_DEFLATED)
    _zip.close()

def rm_tempdir(ssid_name) :
    if os.path.isdir(ssid_name) :
        try:
            os.remove(ssid_name+"/SmartConnect_wireless_for_windows.bat")
        except FileNotFoundError:
            pass
        try:
            os.remove(ssid_name+"/wlan_profile.xml")
        except FileNotFoundError:
            pass
        os.rmdir(ssid_name)  


def main(ssid_name, xml_path, ssid_psk_pw):

    rm_tempdir(ssid_name)
    os.mkdir(ssid_name)

    targetXML = open(xml_path, 'rt', encoding='UTF8')

    ns = "http://www.microsoft.com/networking/WLAN/profile/v1"
    ns_prefix = "{" + ns + "}"
    ET.register_namespace('', ns)

    tree = ET.parse(targetXML)
    root = tree.getroot()

    for child in root.iter() :
        if child.tag.find("}name") == -1:
            pass
        else :
            child.text = ssid_name

        if child.tag.find("}keyMaterial") == -1:
            pass
        else :
            child.text = ssid_psk_pw

    tree.write(ssid_name+"/wlan_profile.xml", encoding="utf-8", xml_declaration=True)

    f = open(ssid_name+"/SmartConnect_wireless_for_windows.bat", "w")
    f.write("@ECHO OFF\r\n")
    f.write("\r\n")
    f.write("chcp 65001\r\n")
    f.write("SETLOCAL ENABLEDELAYEDEXPANSION\r\n")
    f.write("\r\n")
    f.write(":: BatchGotAdmin\r\n")
    f.write(":-------------------------------------\r\n")
    f.write("REM  --> Check for permissions\r\n")
    f.write(">nul 2>&1 \"%SYSTEMROOT%\system32\cacls.exe\" \"%SYSTEMROOT%\system32\config\system\"\r\n")
    f.write("\r\n")
    f.write("REM --> If error flag set, we do not have admin.\r\n")
    f.write("if '%errorlevel%' NEQ '0' (\r\n")
    f.write("    echo Requesting administrative privileges...\r\n")
    f.write("    goto UACPrompt\r\n")
    f.write(") else ( goto gotAdmin )\r\n")
    f.write("\r\n")
    f.write(":UACPrompt\r\n")
    f.write("    echo Set UAC = CreateObject^(\"Shell.Application\"^) > \"%temp%\getadmin.vbs\"\r\n")
    f.write("    set params = %*:\"=\"\"\r\n")
    f.write("    echo UAC.ShellExecute \"cmd.exe\", \"/c %~s0 %params%\", \"\", \"runas\", 1 >> \"%temp%\getadmin.vbs\"\r\n")
    f.write("\r\n")
    f.write("    \"%temp%\getadmin.vbs\"\r\n")
    f.write("    del \"%temp%\getadmin.vbs\"\r\n")
    f.write("    exit /B\r\n")
    f.write("\r\n")
    f.write(":gotAdmin\r\n")
    f.write("    pushd \"%CD%\"\r\n")
    f.write("    CD /D \"%~dp0\"\r\n")
    f.write(":--------------------------------------\r\n")
    f.write("\r\n")
    f.write("netsh wlan add profile filename=wlan_profile.xml\r\n")
    f.write("netsh wlan show profiles\r\n")
    f.write("netsh wlan show profile name=%s\r\n"%(ssid_name))
    f.write("pause\r\n")
    f.close()

    make_zipfile(ssid_name)
    rm_tempdir(ssid_name)

    print("1. copy '%s.zip' file to windows\n2. unzip file\n3. execute SmartConnect_wireless_for_windows.bat" % (ssid_name))


if __name__ == "__main__": 
    if len(sys.argv) < 3 :
        print("ex) python %s ssid_name auth_type(WPA2PSK/WPA2ENT_PEAPMSCHAP)" % sys.argv[0])
        exit()
    ssid_name = sys.argv[1]

    auth_type = sys.argv[2].upper()
    if auth_type == "WPA2PSK" :
        xml_path = "profiler_psk.xml"
        ssid_psk_pw = getpass.getpass(prompt='PSK passphrase: ')
        if len(ssid_psk_pw) < 8 or len(ssid_psk_pw) > 64 :
            print("PSK passphrase enter 8-63 characters in length")
            exit()
    elif auth_type == "WPA2ENT_PEAPMSCHAP" :
        xml_path = "profiler_wpa2.xml"
        ssid_psk_pw = ""
    else :
        print("auth_type only support WPA2PSK or WPA2ENT_PEAPMSCHAP")
        exit()

    main(ssid_name, xml_path, ssid_psk_pw)
