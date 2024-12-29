import { TeamLogs } from "./SuccessData";

export interface ErrorDataBase {
    errorType: "simple" | "detailed" | "timeout" | "nodata";
}

export interface SimpleError extends ErrorDataBase {
    errorType: "simple";
    message: string;
}

export interface DetailedError extends ErrorDataBase {
    errorType: "detailed";
    message: string;
    matches: {
        offenseTeamId: string;
        defenseTeamId: string;
        logs: TeamLogs
    }[];
}

export interface ErrorDataOther {
    errorType: "timeout" | "nodata";
}

export type ErrorData = SimpleError | DetailedError | ErrorDataOther;
