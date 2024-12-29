export type GameMap = number[][];

export interface GameStep {
    team1Score: number;
    team2Score: number;
    logs: string[];
    map: GameMap;
}

export interface TeamLogs {
    team1Logs: string[];
    team2Logs: string[];
}

export interface SuccessData {
    logs: TeamLogs;
    steps: GameStep[];
}
