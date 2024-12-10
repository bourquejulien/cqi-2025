import {GameData, GameDataBase} from "../interfaces/GameData.ts";
import {Stats} from "../interfaces/Stats.ts";

export interface FetcherResponseBase {
    isSuccess: boolean;
}

export interface OkResponse<T> extends FetcherResponseBase {
    data: T;
}

export interface ErrorResponse extends FetcherResponseBase {
    error: string;
    isGameEnded: boolean;
}

export type FetcherResponse<T> = Promise<OkResponse<T>> | Promise<ErrorResponse>;

function handleErrors(response: Promise<Response>) {
    return response.then(async (response) => {
        if (!response.ok) {
            return {isSuccess: false, isGameEnded: response.statusText == "ended", error: response.statusText};
        }

        return {isSuccess: true, data: await response.json()}
    }).catch((error) => {
        return {isSuccess: false, isGameEnded: false, error: error};
    });
}

class DataFetcher {
    baseUrl: string;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl + "/api";
    }

    getGameData(id: string): FetcherResponse<GameData> {
        const url = new URL(`${this.baseUrl}/game/get`);
        url.searchParams.append("id", id);

        return handleErrors(fetch(url.toString()));
    }

    getLeaderBoardData(limit: number, page: number): FetcherResponse<GameDataBase[]> {
        const url = new URL(`${this.baseUrl}/game/list`);
        url.searchParams.append("limit", limit);
        url.searchParams.append("page", page);

        return handleErrors(fetch(url.toString()));
    }

    async getStatsData(): FetcherResponse<Stats> {
        return handleErrors(fetch(`${this.baseUrl}/stats`));
    }
}

export default DataFetcher;
