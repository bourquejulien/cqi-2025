import "./App.css"

import "@mantine/core/styles.css";
import {createTheme, MantineProvider} from "@mantine/core";
import PageContainer from "./PageContainer.tsx";
import DataFetcher from "./services/DataFetcher.ts";
import {setDataFetcher} from "./Data.ts";

const theme = createTheme({
    colors: {
        "CQI": ["#84f08c", "#2a64f6", "rgba(42,100,246,0.87)", "#2AC9DE", "#1AC2D9", "#11B7CD", "#2a64f6", "#0E99AC", "#128797", "#147885"],
    },
    primaryColor: "CQI",
});

function App() {
    const baseServerUrl = process.env.NODE_ENV === "development" ? "http://localhost:8000" : "https://server.cqiprog.info";
    setDataFetcher(new DataFetcher(baseServerUrl));

    return (
        <MantineProvider theme={theme}>
            <PageContainer/>
        </MantineProvider>);
}

export default App
