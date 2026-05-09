; Inno Setup script for odoocli
; Build with: "iscc /DMyAppVersion=1.2.3 odoocli.iss"

#define MyAppName "odoocli"
#define MyAppVersion "0.0.0"
#define MyAppPublisher "biszx"
#define MyAppURL "https://github.com/biszx/odoocli"
#define OutputBaseFilename MyAppName + "-" + MyAppVersion + "-setup"

[Setup]
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename={#OutputBaseFilename}
Compression=lzma
SolidCompression=yes

[Files]
Source: "{#SourcePath}\dist\odoo.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\odoo.exe"

[Run]
Filename: "{app}\odoo.exe"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
