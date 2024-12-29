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

    getGameData(id: string): Promise<GameData | undefined> {
        const game = this.getFromHistory(id);
        if (game) {
            return Promise.resolve(game);
        }

        return this.dataFetcher.getGameData(id).then(game => {
            if (game.isSuccess) {
                this.addToHistory(game.data);
                return game.data;
            }

            console.error(game.error);
            return undefined;
        });
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
