import DataFetcher from "./DataFetcher.ts";
import {GameData} from "../interfaces/GameData.ts";

const HISTORY_SIZE: number = 25;

export class GameService {
    private dataFetcher: DataFetcher;
    private history: GameData[];

    constructor(dataFetcher: DataFetcher) {
        this.dataFetcher = dataFetcher;
        this.history = [];
    }

    async getGameData(id: string | undefined): Promise<GameData | undefined> {
        if (id === undefined) {
            return Promise.resolve(undefined);
        }

        const game = this.getFromHistory(id);
        if (game !== undefined) {
            return Promise.resolve(game);
        }

        const gameData = await this.dataFetcher.getGameData(id);

        if (gameData.isSuccess) {
            this.addToHistory(gameData.data);
            return gameData.data;
        }

        console.error(gameData.error);
        return undefined;
    }

    getGameDataFromCache(id: string | undefined): GameData | undefined {
        if (id === undefined) {
            return undefined;
        }

        return this.getFromHistory(id);
    }

    private getFromHistory(id: string): GameData | undefined {
        return this.history.find(game => game.id === id);
    }

    private addToHistory(game: GameData) {
        this.history.push(game);

        if (this.history.length > HISTORY_SIZE) {
            this.history.shift();
        }
    }
}
