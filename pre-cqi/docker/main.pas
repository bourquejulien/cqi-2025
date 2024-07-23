program main;
{$MODE OBJFPC}

uses
  cthreads,
  kilo_pascal,
  BaseUnix,
  SysUtils;

var
  _IsRunning: Boolean;

procedure HandleSig(aSignal: LongInt); cdecl;
begin
  _IsRunning := false;
end;
 
var
  web: TLightWeb;
begin
    _IsRunning := true;
    if FpSignal(SigInt, @HandleSig) = signalhandler(SIG_ERR) then begin
        Writeln('Failed to install SigInt: ', fpGetErrno);
        Halt(1);
    end;
    if FpSignal(SigTerm, @HandleSig) = signalhandler(SIG_ERR) then begin
        Writeln('Failed to install SigTerm: ', fpGetErrno);
        Halt(1);
    end;

    web := TLightWeb.Create(11000);
    web.start;
    WriteLn('Running pascal in pascal');

  repeat
    Sleep(250);
  until not _IsRunning;

  web.Stop;
  web.Free;
  writeln('Stopped');
end.
