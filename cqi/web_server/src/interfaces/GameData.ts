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

export interface GameData extends GameDataBase {
    errorData: string;
    gameData: string;
}
