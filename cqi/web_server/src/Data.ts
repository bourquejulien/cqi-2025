import DataFetcher from "./services/DataFetcher.ts";
import {PlayerService} from "./services/PlayerService.ts";
import {GameService} from "./services/GameService.ts";

let dataFetcher: DataFetcher;
let gameService: GameService;
const playerService: PlayerService = new PlayerService();

export function setDataFetcher(fetcher: DataFetcher) {
    dataFetcher = fetcher;
    gameService = new GameService(dataFetcher);
}

export function getDataFetcher(): DataFetcher {
    return dataFetcher;
}

export function getPlayerService(): PlayerService {
    return playerService;
}

export function getGameService(): GameService {
    return gameService;
}
