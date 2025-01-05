export type GameMap = string[][];

export interface GameStep {
    score: number;
    visionRadius: number;
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
    maxMoveCount: number;
    matches: MatchData[];
}
