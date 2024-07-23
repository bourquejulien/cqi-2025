unit kilo_pascal;

{$mode objfpc}{$H+}

interface

uses
  Classes, SysUtils, blcksock, sockets,
  strutils,
  Synautil;

type
  TPassMessage = procedure(AMsg: string) of object;

  TLightWeb = class(TThread)
  private
    _Port: word;
    _IsRunning: Boolean;
    procedure AttendConnection(ASocket: TTCPBlockSocket);
    function ComputeConvertion(mmhgValue: Double): Double;
  protected
    procedure Execute; override;
  public
    constructor Create(APort: word);
    procedure Stop();
    destructor Destroy; override;
  end;

implementation

constructor TLightWeb.Create(APort: word);
begin
  inherited Create(False);
  _Port := Aport;
  _IsRunning := true;
end;

procedure TLightWeb.Stop;
begin
  _IsRunning := false;
  WaitFor;
end;

procedure TLightWeb.Execute;
var
  ListenerSocket, ConnectionSocket: TTCPBlockSocket;

begin
  try
    ListenerSocket := TTCPBlockSocket.Create;
    ConnectionSocket := TTCPBlockSocket.Create;
    ListenerSocket.CreateSocket;
    ListenerSocket.setLinger(True, 10);
    ListenerSocket.bind('0.0.0.0', IntToStr(_Port));
    ListenerSocket.listen;

    repeat
      if ListenerSocket.canread(1000) then
      begin
        ConnectionSocket.Socket := ListenerSocket.accept;
        WriteLn('Attending Connection. Error code (0=Success): ', ConnectionSocket.lasterror);
        AttendConnection(ConnectionSocket);
        ConnectionSocket.CloseSocket;
      end;
    until not _IsRunning or Terminated;

  finally
    FreeAndNil(ListenerSocket);
    FreeAndNil(ConnectionSocket);
  end;
end;

procedure TLightWeb.AttendConnection(ASocket: TTCPBlockSocket);
type
	RequestType = (health, conversion, other);
var
  timeout: integer;
  s: string;
  address: string;
  returnCode: string;
  OutputDataString: string;
  valueToConvert: string;
  conversionResult: Double;
  rType: RequestType;
  paramPositionStart: Integer;
  paramPositionEnd: Integer;

begin
  timeout := 120000;

  try
    try
      address := ASocket.RecvString(timeout);
      WriteLn(address);

      if (ContainsText(address, '/health')) then
        rType := health
      else if (ContainsText(address, '/convert')) then
        rType := conversion
      else
        rType := other;
      

      //read request headers
      repeat
        s := ASocket.RecvString(Timeout);
      until s = '';

      OutputDataString := 'Invalid path';
      returnCode := '400';

      if (rType = health) then
        begin
          returnCode := '200';
          OutputDataString := 'healthy';
        end
      else if (rType = conversion) then
        begin
          returnCode := '200';
          
          paramPositionStart := Pos('?', address) + 2;
          paramPositionEnd := Pos('HTTP/1.1', address) - 1;
          valueToConvert := Copy(address, paramPositionStart , paramPositionEnd - paramPositionStart);

          conversionResult := ComputeConvertion(StrToFloat(valueToConvert));
          
          OutputDataString := FloatToStr(conversionResult);
        end;

      ASocket.SendString('HTTP/1.1 ' + returnCode + CRLF);
      OutputDataString := OutputDataString + CRLF;

      // Write the headers back to the client
      ASocket.SendString('Content-type: Text/plain' + CRLF);
      ASocket.SendString('Content-length: ' + IntToStr(Length(OutputDataString)) + CRLF);
      ASocket.SendString('Connection: close' + CRLF);
      ASocket.SendString('Date: ' + Rfc822DateTime(now) + CRLF);
      ASocket.SendString('Server: Lazarus Synapse' + CRLF);
      ASocket.SendString('' + CRLF);

      ASocket.SendString(OutputDataString);
    except
      on E: Exception do
      begin

      end;
    end;
  finally
  end;
end;

function TLightWeb.ComputeConvertion(mmhgValue: Double) : Double;
begin
  Result := mmhgValue / 7.501;
end;

destructor TLightWeb.Destroy();
begin
  inherited Destroy;
end;

end.
