import './App.css'

import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import PageContainer from "./PageContainer.tsx";
import DataFetcher from "./services/DataFetcher.ts";
import {setDataFetcher} from "./Data.ts";

function App() {
    const baseServerUrl = process.env.NODE_ENV === "development" ? "http://localhost:8000" : "https://server.cqiprog.info";
    setDataFetcher(new DataFetcher(baseServerUrl));

    return (
    <MantineProvider>
        <PageContainer/>
    </MantineProvider>);
}

export default App
