; setup script for AdiosOilDatabase

;#define SKIP_MOST_FILES

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

[Setup]

;For test versions, append " Testing Version" to next 2 lines
AppName=ADIOS Oil Database
AppVerName=ADIOS Oil Database
AppVersion=2020
VersionInfoVersion = 1.0.0.0

AppPublisher=NOAA/ERD
AppPublisherURL=https://response.restoration.noaa.gov/
AppSupportURL=https://response.restoration.noaa.gov/
DefaultDirName={pf}\AdiosOilDatabase
DefaultGroupName=AdiosOilDatabase
UninstallDisplayIcon={app}\AdiosOilDatabase.exe
ChangesAssociations=yes

DisableWelcomePage=no
DisableDirPage=no
UsePreviousAppDir=yes
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no

LicenseFile=Terms and Conditions.rtf
WizardImageFile=InstallerFiles\WizModernImage-Logo.bmp 
WizardSmallImageFile=InstallerFiles\WizModernSmallImage-T2S.bmp

OutputBaseFilename=AdiosOilDatabaseInstaller

WizardImageStretch=no

; set MinVersion to say we only install on Windows 7 and higher
MinVersion = 6.1

[LangOptions]
DialogFontName=Verdana
DialogFontSize=10

[Languages]
Name: "en"; MessagesFile: "InstallerFiles\Default_NOAA.isl"

[MESSAGES]
; ************************************************************************
; Note: we are overriding the ENTIRE Default.isl file with Default_NOAA.isl
SetupAppTitle=ADIOS Oil Database Installer

; override the default message lines

;SetupWindowTitle=Setup - %1
;SetupWindowTitle=Setup - %1 Testing Version

;WelcomeLabel1=Welcome to the [name] Setup Wizard

;WelcomeLabel2=This will install [name/ver] on your computer.%n%nIt is recommended that you close all other applications before continuing.

;WizardSelectDir=Select Destination Location
WizardSelectDir=Select Program Installation Location

;SelectDirDesc=Where should [name] be installed?
;SelectDirDesc=Where should the [name] program files be installed?

;SelectDirLabel3=Setup will install [name] into the following folder.
;selectDirLabel3=The [name] program files will be installed into the following folder.%n(Later you will be asked where to install the user data files.)
selectDirLabel3=The [name] program files will be installed into the following folder. (Later you will be asked where to install the user data files.)

;FinishedLabel=Setup has finished installing [name] on your computer. The application may be launched by selecting the installed icons.
;FinishedLabel=Setup has finished installing [name] on your computer.

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked

[Dirs]
; grant modify privileges on the data dir to all in the users group (so non-admin users are OK)
Name: "{code:GetUserChosenDataDirectory}"; Permissions: users-modify
; create the two empty directories
; Name: "{code:GetUserChosenDataDirectory}\ImportFiles"
; Name: "{code:GetUserChosenDataDirectory}\ExportFiles"
; Name: "{code:GetUserChosenDataDirectory}\SitePlans"

[Files]
#ifndef SKIP_MOST_FILES
;; the regular install
;;;;;;;;;;;;;;;;;;;;
; the "Program Files" folder
Source: "C:\Users\michael.katz\Documents\_scratch\odb\adiosdb\*"; DestDir: "{app}\adiosdb"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\michael.katz\Documents\_scratch\odb\electron\*"; DestDir: "{app}\electron"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "C:\Users\michael.katz\Documents\_scratch\odb\oil_database\*"; DestDir: "{app}\oil_database"; Flags: ignoreversion recursesubdirs createallsubdirs
; files that vary depending on whether machine is 64-bit Windows
; Source: "SourceFiles\64bit\*"; DestDir: "{app}"; Check: IsWin64;
; Source: "SourceFiles\32bit\*"; DestDir: "{app}"; Check: "not IsWin64";
; the "user writable" folder
Source: "C:\Users\michael.katz\Documents\_scratch\odb\mongo_files\*"; DestDir: "{code:GetUserChosenDataDirectory}"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall
#else
; SKIP_MOST_FILES, just use a few files here, mostly we just want to go through the screens
;;;;;;;;;;;;;;;;;;;;
; Source: "SourceFiles\AppFolder\*.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Source: "SourceFiles\UserDataFolder\htmlreport*"; DestDir: "{code:GetUserChosenDataDirectory}"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

; [UninstallDelete]
; Type: files; Name: "{app}\data.txt"

[Icons]
Name: "{app}\AdiosOilDatabase"; Filename: "{app}\electron\ADIOS Oil Database.exe";  WorkingDir: "{app}\electron"
; we install the start menu and desktop icons for all users
Name: "{commonprograms}\AdiosOilDatabase{code:GetTextUserAddedToAppFolder}"; Filename: "{app}\electron\ADIOS Oil Database.exe"; WorkingDir: "{app}\electron"
Name: "{commondesktop}\AdiosOilDatabase{code:GetTextUserAddedToAppFolder}"; Filename: "{app}\electron\ADIOS Oil Database.exe"; WorkingDir: "{app}\electron"; Tasks: desktopicon

[Run]
Filename: {app}\electron\ADIOS Oil Database.exe; Description: Launch ADIOS Oil Database; Flags: postinstall nowait skipifsilent unchecked

[Registry]
;  ************************************UPDATE THE .T2N EXTENSION BELOW EACH YEAR ************************************
; Root: HKCR; Subkey: ".TS8"; ValueType: string; ValueName: ""; ValueData: "Tier2Submit2018"; Flags: uninsdeletevalue
; Root: HKCR; Subkey: "Tier2Submit2018"; ValueType: string; ValueName: ""; ValueData: "Tier2Submit2018"; Flags: uninsdeletekey
; Root: HKCR; Subkey: "Tier2Submit2018\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\Tier2Submit2018.exe,0"
; Root: HKCR; Subkey: "Tier2Submit2018\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Tier2Submit2018.exe"" ""%1"""

[Code]
var
  Page2: TInputDirWizardPage;
  s: String;

////////////
// from web 
const
  CP_UTF8 = 65001;

function WideCharToMultiByte(CodePage: UINT; dwFlags: DWORD;
  lpWideCharStr: string; cchWideChar: Integer; 
  lpMultiByteStr: AnsiString; cchMultiByte: Integer; 
  lpDefaultCharFake: Integer; lpUsedDefaultCharFake: Integer): Integer;
  external 'WideCharToMultiByte@kernel32.dll stdcall';

function ConvertStringToUtf8(S: string): AnsiString;
var
  Len: Integer;
begin
  Len := WideCharToMultiByte(CP_UTF8, 0, S, Length(S), Result, 0, 0, 0);
  SetLength(Result, Len);
  WideCharToMultiByte(CP_UTF8, 0, S, Length(S), Result, Len, 0, 0);
end;

function SaveStringToUTF8FileWithoutBOM(FileName: string; S: string; const AppendFlag: Boolean): Boolean;
var
  Utf8: AnsiString;
begin
  Utf8 := ConvertStringToUtf8(S);
  Result := SaveStringToFile(FileName, Utf8, AppendFlag);
end;

////////////////
////////////////
// Jerry code

function MultiByteToWideChar(CodePage: UINT; dwFlags: DWORD;
  lpMultiByteStr: AnsiString; cchMultiByte: Integer; 
  lpWideCharStr: string; cchWideChar: Integer ): Integer;
  external 'MultiByteToWideChar@kernel32.dll stdcall';

function ConvertUtf8toString(S: AnsiString): string;
var
  Len: Integer;
begin
  Len := MultiByteToWideChar(CP_UTF8, 0, S, Length(S), Result, 0);
  SetLength(Result, Len);
  MultiByteToWideChar(CP_UTF8, 0, S, Length(S), Result, Len );
end;

////////////////////////   

function GetTextUserAddedToAppFolder(Param: String): String;
var
  usersAppDir: string;
  textUserAdded: string;
  expectedStartStr: string;
  i: integer;
  start: integer;
begin

  usersAppDir := ExpandConstant( '{app}' );
  //////////////////////////////////
  // note Result will be empty unless set

  // we anticipate the user only adds to what was suggested 
  // and don't try to handle text added before the directory. 
  // But we do try to get the last added text if they have nested directories 
  expectedStartStr := '\AdiosOilDatabase' // so that we don't have to repeat it below
  i := Pos( expectedStartStr, usersAppDir );
  if i > 0 then begin
    start := i + length( expectedStartStr );
    textUserAdded := Copy( usersAppDir, start, length( usersAppDir ) - start + 1 );
    /////////////////
    // deal with nested directories
    i := Pos( expectedStartStr, textUserAdded );
    while i > 0 do
      begin
        start := i + length( expectedStartStr );
        textUserAdded := Copy( textUserAdded, start, length( textUserAdded ) - start + 1 );
        i := Pos( expectedStartStr, textUserAdded );
      end;
    ///
    // if there is a directory in the added text, don't try to use the added text
    i := Pos( '\' , textUserAdded );
    if i = 0 then begin
      Result := textUserAdded;
    end;
  end;
end;

function GetDefaultDataDir(Param: String): String;
var
  // usersAppDir: string;
  usualDataDir: string;
  // filepath: string;
  // gotPath: Boolean;
  // fileContentsRaw: AnsiString;
  // fileContents: string;
  textUserAdded: string;
  // startTag: string;
  // endTag: string;
  // i: integer;
  // start: integer;
begin
  // if the {app} folder has a data directory text file we will use the path it contains
  // if the {app} folder DOES NOT have a data directory text file we will try to respect the part that the user added
  // usersAppDir := ExpandConstant('{app}');
  // filepath := ExpandConstant('{app}\data.txt');
  usualDataDir := ExpandConstant('{commondocs}\AdiosOilDatabase Data');
  // gotPath := LoadStringFromFile(filepath,fileContentsRaw);
  /// set the reult to the usual path
  // Result := usualDataDir; 
  //////////////////////////////////////////
  // if gotPath then begin
  //    Result := ConvertUtf8toString( fileContentsRaw );
  // end
  // else begin
    //////////////////////////////////
    // we expect usersAppDir to be <path>\Tier2Submit2019<textUserAdded>
    textUserAdded := GetTextUserAddedToAppFolder('');
    Result := usualDataDir + textUserAdded;
    ////////////////////////////////
  // end;
end;

function GetUserChosenDataDirectory(Param: String): String;
begin
  Result := Page2.Values[ 0 ];
End;

function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
begin
    Result := 'ADIOS Oil Database program files location:' + NewLine + Space + ExpandConstant('{app}')
          + NewLine + NewLine
          +	'ADIOS Oil Database user data location:' + NewLine
          + Space + Page2.Values[0] + NewLine
          + NewLine
          + MemoTasksInfo + NewLine;
end;

function writeDataFolderFile(): Boolean;
var
  filename: string;
  s: string;
begin
  filename := ExpandConstant('{app}\oil_database\mongo_config_dev.yml');
  s := 'net:' + Chr( 10 ) +
       '  port: 27017' + Chr( 10 ) +
       'storage:' + Chr( 10 ) +
       '  dbPath: ' + GetUserChosenDataDirectory( '' ) + Chr( 10 );
  Result := SaveStringToUTF8FileWithoutBOM(filename,s,False);
  // filename := ExpandConstant('{app}\html.txt');
  // Result := SaveStringToUTF8FileWithoutBOM(filename,'html',False);
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  WindowsVersion: string;
begin
  case CurStep of
    ssPostInstall:
      begin
        writeDataFolderFile();
      end;
  end;
end;

procedure InitializeWizard;
begin
  Page2 := CreateInputDirPage(wpSelectComponents,
    'Select User Data Files Location',
    '', // Where should the ADIOS Oil Database user data files be installed?

    'The ADIOS Oil Database user data files will be installed in the following folder.'+
    Chr(13)+Chr(10) +
    'Make sure you have write permission in this folder.'+
    Chr(13)+Chr(10)+Chr(13)+Chr(10) +
    'If you are an administrator installing for a non-admin user, make sure the end user has rights to create files in this folder.' +
    Chr(13)+Chr(10)+Chr(13)+Chr(10) +
    'Click Next if the location is correct. Click Browse to select a different folder.',
    False, 'New Folder');

  // Add item (with an empty caption)
  Page2.Add('');

  // Set initial value (optional)
  // we will set the value of the user data directory later
  //Page2.Values[0] := GetDir(s);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := true; // let the user go on
  // 
  if CurPageID = wpSelectDir then begin
    // if
    Page2.Values[0] := GetDefaultDataDir(Page2.Values[0]);
  end;
end;
