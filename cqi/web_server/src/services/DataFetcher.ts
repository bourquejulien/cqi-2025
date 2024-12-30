import { GameResults, GameSuccess, GameFailure, GameData } from "../interfaces/GameData.ts";
import { Stats } from "../interfaces/Stats.ts";
import { Match } from "../interfaces/Match.ts";
import { LaunchData } from "../interfaces/LaunchData.ts";

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

function parseEncodedField<T>(data: string): T {
    const decodedString = new TextDecoder().decode(Uint8Array.from(atob(data), c => c.charCodeAt(0)));
    return JSON.parse(decodedString) as T;
}

function handleErrors<T>(response: Promise<Response>): FetcherResponse<T> {
    return response.then(async (response) => {
        if (!response.ok) {
            return {
                isSuccess: false,
                isGameEnded: (await response.text()).startsWith("Forbidden"),
                error: response.statusText
            } as ErrorResponse;
        }

        return { isSuccess: true, data: await response.json() } as OkResponse<T>
    }).catch((error) => {
        return { isSuccess: false, isGameEnded: false, error: error } as ErrorResponse;
    });
}

function handleGameDataError(gameData: GameData): GameFailure {
    let data = "";
    if ("errorData" in gameData) {
        data = gameData["errorData"] as unknown as string;
    }

    if (data.length == 0) {
        const failure = gameData as GameFailure;
        failure.isError = true;
        failure.errorData = {
            errorType: "nodata"
        };
        return failure;
    }

    const failure = gameData as GameFailure;
    failure.errorData = parseEncodedField(data);

    return failure;
}

function handleGameDataSuccess(gameData: GameData): GameData {
    let data = "";
    if ("gameData" in gameData) {
        data = gameData["gameData"] as unknown as string;
    }

    if (data.length == 0) {
        const failure = gameData as GameFailure;
        failure.isError = true;
        failure.errorData = {
            errorType: "nodata"
        };
        return failure;
    }

    const gameSuccess = gameData as GameSuccess;
    gameSuccess.gameData = parseEncodedField(data);

    return gameSuccess;
}

function handleGameData(gameData: GameData): GameData {
    gameData.startTime = new Date(gameData.startTime);
    gameData.endTime = new Date(gameData.endTime);

    console.log(gameData);

    if (gameData.isError) {
        return handleGameDataError(gameData);
    }
    return handleGameDataSuccess(gameData);
}

class DataFetcher {
    baseUrl: string;
    internalKey: string | undefined;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl + "/api";
        this.internalKey = localStorage.getItem("internalKey") ?? undefined;

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (window as any).setInternalKey = this.setInternalKey.bind(this);
    }

    private setInternalKey(internalKey: string) {
        this.internalKey = internalKey;
        localStorage.setItem("internalKey", internalKey);
    }

    private getHeaders(): Headers {
        const headers = new Headers();
        if (this.internalKey) {
            headers.append("Authorization", this.internalKey);
        }
        return headers;
    }

    private fetch<T>(url: string, init?: RequestInit): FetcherResponse<T> {
        return handleErrors(fetch(url, {
            method: "GET",
            headers: this.getHeaders(),
            ...init
        }));
    }

    async getGameData(id: string): FetcherResponse<GameData> {
        const url = new URL(`${this.baseUrl}/game/get`);
        url.searchParams.append("id", id);

        const response = await this.fetch<GameData>(url.toString());
        if (!response.isSuccess) {
            return response;
        }
        response.data = handleGameData(response.data);
        return response;
    }

    async getOngoingMatches(): FetcherResponse<Match[]> {
        const response = await this.fetch<Match[]>(`${this.baseUrl}/ongoing_matches`);
        if (response.isSuccess) {
            response.data.forEach((match) => {
                match.startTime = new Date(match.startTime);
            });
        }
        return response;
    }

    async getLaunchData(): FetcherResponse<LaunchData> {
        const response = await this.fetch<LaunchData>(`${this.baseUrl}/launch_data`);
        if (response.isSuccess) {
            response.data.endTime = new Date(response.data.endTime);
        }

        return response;
    }

    async getLeaderBoardData(limit: number, page: number): FetcherResponse<GameResults> {
        const url = new URL(`${this.baseUrl}/game/list`);
        url.searchParams.append("limit", String(limit));
        url.searchParams.append("page", String(page));

        const response = await this.fetch<GameResults>(url.toString());
        if (response.isSuccess) {
            response.data.results.forEach((game) => {
                game.startTime = new Date(game.startTime);
                game.endTime = new Date(game.endTime);
            });
        }
        return response;
    }

    async getStatsData(): FetcherResponse<Stats> {
        const response = await this.fetch<Stats>(`${this.baseUrl}/stats`);
        if (response.isSuccess) {
            response.data.endTime = new Date(response.data.endTime);
        }
        return response;
    }
}

export default DataFetcher;
