import Header from "./components/Header/Header.tsx";
import GamePage from "./pages/GamePage.tsx";
import MainPage from "./pages/MainPage.tsx";
import {useState} from "react";
import {Stack, Container} from "@mantine/core";

function PageContainer() {
    const [gameId, setGameId] = useState<string | undefined>(undefined)

    return (
        <Container fluid h="100vh" p={20}
        >
            <Stack
                // h={3000}
                bg="var(--mantine-color-body)"
                align="stretch"
                justify="space-between"
                gap="md"
            >
                <Header/>
                {gameId == undefined ? <MainPage gameId={gameId} setGameId={setGameId}/> :
                    <GamePage gameId={gameId} setGameId={setGameId}/>}
            </Stack>
        </Container>

    )
}

export default PageContainer;
