export type GameMap = number[][];

export interface GameStep {
    score: number;
    logs: string[];
    map: GameMap;
}

export interface TeamLogs {
    offense: string[];
    defense: string[];
}

export interface MatchData {
    offenseTeamId: string;
    defenseTeamId: string;
    logs: TeamLogs;
    steps: GameStep[];
}

export interface SuccessData {
    matches: MatchData[];
}
