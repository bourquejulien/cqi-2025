import Header from "./components/Header/Header.tsx";
import GamePage from "./pages/GamePage.tsx";
import MainPage from "./pages/MainPage.tsx";
import {useEffect, useState} from "react";
import {Stack, Container} from "@mantine/core";
import {getDataFetcher} from "./Data.ts";
import {Stats} from "./interfaces/Stats.ts";
import {GameOverPage} from "./pages/GameOverPage.tsx";
import {LoadingPage} from "./pages/LoadingPage.tsx";

function Content({stats}: { stats: Stats | undefined }) {
    const [gameId, setGameId] = useState<string | undefined>(undefined)

    if (stats === undefined) {
        return <></>
    }

    if (gameId === undefined) {
        return <MainPage setGameId={setGameId} stats={stats}/>
    }

    return <GamePage gameId={gameId} setGameId={setGameId}/>
}

function PageContainer() {
    const [stats, setStats] = useState<Stats | undefined>(undefined);
    const [isOver, setIsOver] = useState<boolean>(false);

    useEffect(() => {
        const updateStats = async () => {
            const response = await getDataFetcher().getStatsData();

            if (response.isSuccess) {
                response.data.endTime = new Date(response.data.endTime);
                setStats(response.data);
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

    }, []);

    if (isOver) {
        return <GameOverPage/>
    }

    if (stats === undefined) {
        return <LoadingPage/>;
    }

    return (
        <Container fluid h="100vh" p={20}>
            <Stack
                bg="var(--mantine-color-body)"
                align="stretch"
                justify="stretch"
                h={"100%"}
                gap="3vh">
                <Header stats={stats}/>
                <Content stats={stats}></Content>
            </Stack>
        </Container>
    )
}

export default PageContainer;
