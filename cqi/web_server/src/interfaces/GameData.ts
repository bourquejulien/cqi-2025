import { ErrorData } from "./ErrorData";
import { SuccessData } from "./SuccessData";

export interface GameDataBase {
    id: string;
    startTime: Date;
    endTime: Date;
    team1Id: string;
    team2Id: string;
    winnerId: string | null;
    isError: boolean;
    team1Score: number;
    team2Score: number;
}

export interface GameFailure extends GameDataBase {
    isError: true;
    errorData: ErrorData;
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
