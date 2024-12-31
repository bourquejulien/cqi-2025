import {ErrorData} from "./ErrorData";
import { SuccessData } from "./SuccessData";

export interface GameDataBase {
    id: string;
    startTime: Date;
    endTime: Date;
    team1Id: string;
    team2Id: string;
    winnerId: string | undefined;
    isError: boolean;
    team1Score: number;
    team2Score: number;
}

export interface GameFailure<T extends ErrorData = ErrorData> extends GameDataBase {
    isError: true;
    errorData: T;
}

export interface GameSuccess extends GameDataBase {
    isError: false;
    gameData: SuccessData
}

export type GameData = GameFailure | GameSuccess;

export interface GameResults {
    totalGameCount: number;
    results: GameDataBase[];
}
