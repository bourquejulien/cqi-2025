import {Container} from "@mantine/core";

// @ts-expect-error TS6198
function GamePage({ gameId, setGameId }: { gameId: string; setGameId: (id: string) => void }) {    return (
        <Container>

        </Container>
    )
}

export default GamePage;
