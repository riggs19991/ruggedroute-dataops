; Inno Setup script for RuggedRoute HQ (Windows). Built by .github/workflows/hq-release.yml.
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef SourceDir
  #define SourceDir "..\..\build\windows\x64\runner\Release"
#endif
#ifndef OutputDir
  #define OutputDir "..\..\build\installer"
#endif

[Setup]
AppId={{7B1C2E4A-5C0F-4E7B-9C9A-HQRUGGEDROUTE}
AppName=RuggedRoute HQ
AppVersion={#AppVersion}
AppPublisher=Addictive Media Productions LLC
DefaultDirName={autopf}\RuggedRoute HQ
DefaultGroupName=RuggedRoute HQ
UninstallDisplayIcon={app}\RuggedRouteHQ.exe
OutputDir={#OutputDir}
OutputBaseFilename=RuggedRouteHQ-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
CloseApplications=yes
RestartApplications=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RuggedRoute HQ"; Filename: "{app}\RuggedRouteHQ.exe"
Name: "{autodesktop}\RuggedRoute HQ"; Filename: "{app}\RuggedRouteHQ.exe"

[Run]
Filename: "{app}\RuggedRouteHQ.exe"; Description: "Open RuggedRoute HQ"; Flags: nowait postinstall skipifsilent
