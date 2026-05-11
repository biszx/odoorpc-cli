; Inno Setup script for odoorpc_cli
; Build with: "iscc /DMyAppVersion=1.2.3 odoorpc_cli.iss"

#define MyAppName "odoorpc_cli"
#define MyAppVersion "0.0.0"
#define MyAppPublisher "biszx"
#define MyAppURL "https://github.com/biszx/odoorpc_cli"
#define OutputBaseFilename "odoorpc-cli-setup"

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
Source: "..\..\dist\odoorpc_cli.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\odoorpc_cli.exe"

[Run]
Filename: "{app}\odoorpc_cli.exe"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
