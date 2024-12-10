import DataFetcher from "./services/DataFetcher.ts";

let dataFetcher: DataFetcher;

export function setDataFetcher(fetcher: DataFetcher) {
    dataFetcher = fetcher;
}

export function getDataFetcher(): DataFetcher {
    return dataFetcher;
}
