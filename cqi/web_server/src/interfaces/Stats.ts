export interface Stats {
    totalGames: number;
    endTime: Date;
    rankingInfo: RankingInfo;
}

export interface RankingInfo {
    updatePeriod: number;
    results: RankResult[];
}

export interface RankResult {
    teamId: string;
    totalGames: number;
    totalWins: number;
    totalDraws: number;
    totalLosses: number;
}
