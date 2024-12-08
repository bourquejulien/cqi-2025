import {GameData, GameDataBase} from "../interfaces/GameData.ts";
import {Stats} from "../interfaces/Stats.ts";

class DataFetcher {
    baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
    }

    async getGameData(): GameData {
        return fetch("https://api.example.com/gameData")
            .then((response) => response.json())
            .then((data) => {
                return data;
            });
    }

    async getLeaderBoardData(): GameDataBase[] {
        return fetch("https://api.example.com/leaderBoardData")
            .then((response) => response.json())
            .then((data) => {
                return data;
            });
    }

    async getStatsData(): Stats {
        return fetch("https://api.example.com/statsData")
            .then((response) => response.json())
            .then((data) => {
                return data;
            });
    }
}

export default DataFetcher;
