import Header from "./components/Header/Header.tsx";
import GamePage from "./pages/GamePage.tsx";
import MainPage from "./pages/MainPage.tsx";
import {useEffect, useState} from "react";
import {Stack, Container} from "@mantine/core";
import {getDataFetcher, getPlayerService} from "./Data.ts";
import {Stats} from "./interfaces/Stats.ts";
import {GameOverPage} from "./pages/GameOverPage.tsx";
import {LoadingPage} from "./pages/LoadingPage.tsx";
import {Route, Routes, Navigate} from "react-router";

function Content({stats, setIsReady}: { stats: Stats | undefined, setIsReady: (isReady: boolean) => void }) {
    if (stats === undefined) {
        return <></>
    }

    return (
        <Routes>
            <Route index element={<MainPage stats={stats} setIsReady={setIsReady}/>}/>
            <Route path="board/:cpage" element={<MainPage stats={stats} setIsReady={setIsReady}/>}/>
            <Route path="game/:id" element={<GamePage/>}/>
            <Route path="*" element={<Navigate to="/" replace />}/>
        </Routes>
    )
}

function PageContainer() {
    const [isReady, setIsReady] = useState<boolean>(false);
    const [stats, setStats] = useState<Stats | undefined>(undefined);
    const [isOver, setIsOver] = useState<boolean>(false);

    useEffect(() => {
        const updateStats = async () => {
            const response = await getDataFetcher().getStatsData();
            if (response.isSuccess) {
                setStats(response.data);
                setIsOver(false);
            } else if (response.isGameEnded) {
                setIsOver(true);
            }
        }
        updateStats();
        const interval = setInterval(updateStats, 10_000);
        return () => {
            clearInterval(interval);
        };
    }, []);

    useEffect(() => {
        if (isReady) {
            return;
        }
        getDataFetcher().getLaunchData().then((response) => {
            if (response.isSuccess) {
                getPlayerService().setMapping(response.data.teamIdMapping);
                setIsReady(true);
            }
        });
    }, [stats]);

    if (isOver) {
        return <GameOverPage/>
    }

    if (!isReady || stats === undefined) {
        return <LoadingPage/>;
    }

    return (
        <Container fluid p={20}>
            <Stack
                bg="var(--mantine-color-body)"
                align="stretch"
                justify="stretch"
                h={"100%"}
                gap="3vh">
                <Header stats={stats}/>
                <Content stats={stats} setIsReady={setIsReady}></Content>
            </Stack>
        </Container>
    )
}

export default PageContainer;
