import {GameData, GameDataBase} from "../interfaces/GameData.ts";
import {Stats} from "../interfaces/Stats.ts";

export interface FetcherResponseBase {
    isSuccess: boolean;
}

export interface OkResponse<T> extends FetcherResponseBase {
    isSuccess: true;
    data: T;
}

export interface ErrorResponse extends FetcherResponseBase {
    isSuccess: false;
    error: string;
    isGameEnded: boolean;
}

export type FetcherResponse<T> = Promise<OkResponse<T> | ErrorResponse>;

function handleErrors<T>(response: Promise<Response>): FetcherResponse<T> {
    return response.then(async (response) => {
        if (!response.ok) {
            return {isSuccess: false, isGameEnded: response.statusText == "ended", error: response.statusText} as ErrorResponse;
        }

        return {isSuccess: true, data: await response.json()} as OkResponse<T>
    }).catch((error) => {
        return {isSuccess: false, isGameEnded: false, error: error} as ErrorResponse;
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
        url.searchParams.append("limit", String(limit));
        url.searchParams.append("page", String(page));

        return handleErrors(fetch(url.toString()));
    }

    getStatsData(): FetcherResponse<Stats> {
        return handleErrors(fetch(`${this.baseUrl}/stats`));
    }
}

export default DataFetcher;
