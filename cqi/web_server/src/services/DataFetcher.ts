import {GameData, GameResults} from "../interfaces/GameData.ts";
import {Stats} from "../interfaces/Stats.ts";
import {Match} from "../interfaces/Match.ts";
import {LaunchData} from "../interfaces/LaunchData.ts";

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
            return {
                isSuccess: false,
                isGameEnded: (await response.text()).startsWith("Forbidden"),
                error: response.statusText
            } as ErrorResponse;
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

    getOngoingMatches(): FetcherResponse<Match[]> {
        return handleErrors<Match[]>(fetch(`${this.baseUrl}/ongoing_matches`))
            .then((response) => {
                if (response.isSuccess) {
                    response.data.forEach((match) => {
                        match.startTime = new Date(match.startTime);
                    });
                }
                return response;
            });
    }

    getLaunchData(): FetcherResponse<LaunchData> {
        return handleErrors<LaunchData>(fetch(`${this.baseUrl}/launch_data`))
            .then((response) => {
                if (response.isSuccess) {
                    response.data.endTime = new Date(response.data.endTime);
                }
                return response;
            });
    }

    getLeaderBoardData(limit: number, page: number): FetcherResponse<GameResults> {
        const url = new URL(`${this.baseUrl}/game/list`);
        url.searchParams.append("limit", String(limit));
        url.searchParams.append("page", String(page));

        return handleErrors<GameResults>(fetch(url.toString()))
            .then((response) => {
                if (response.isSuccess) {
                    response.data.results.forEach((game) => {
                        game.startTime = new Date(game.startTime);
                        game.endTime = new Date(game.endTime);
                    });
                }
                return response;
            });
    }

    getStatsData(): FetcherResponse<Stats> {
        return handleErrors<Stats>(fetch(`${this.baseUrl}/stats`))
            .then((response) => {
                if (response.isSuccess) {
                    response.data.endTime = new Date(response.data.endTime);
                }
                return response;
            });
    }
}

export default DataFetcher;
