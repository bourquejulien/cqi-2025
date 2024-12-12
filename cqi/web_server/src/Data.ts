import DataFetcher from "./services/DataFetcher.ts";
import {PlayerService} from "./services/PlayerService.ts";

let dataFetcher: DataFetcher;
const playerService: PlayerService = new PlayerService();

export function setDataFetcher(fetcher: DataFetcher) {
    dataFetcher = fetcher;
}

export function getDataFetcher(): DataFetcher {
    return dataFetcher;
}

export function getPlayerService(): PlayerService {
    return playerService;
}
