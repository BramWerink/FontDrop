; Inno Setup script voor FontDrop: per-gebruiker installatie, geen adminrechten.
; Pakt de PyInstaller-output (dist\FontDrop) in tot één installer-exe.
;
; Lokaal compileren (nadat je eerst `pyinstaller` hebt gedraaid, zie README):
;   ISCC installer.iss
; In CI wordt de versie meegegeven: ISCC installer.iss /DMyAppVersion=1.2.3

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0-dev"
#endif

#define MyAppName "FontDrop"
#define MyAppExeName "FontDrop.exe"
#define MyAppPublisher "FontDrop"

[Setup]
AppId={{2E0C9B7E-6A3D-4C9A-9E7B-5D6F7A3B1C44}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Per-gebruiker installeren in LocalAppData; geen adminrechten nodig of gevraagd.
DefaultDirName={localappdata}\Programs\{#MyAppName}
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=FontDrop-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Snelkoppeling op het bureaublad"; GroupDescription: "Extra snelkoppelingen:"; Flags: unchecked

[Files]
; Hele PyInstaller-map (exe + _internal) overnemen.
Source: "dist\FontDrop\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "FontDrop nu starten"; Flags: nowait postinstall skipifsilent
