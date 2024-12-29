import {Container, Loader, Stack, Text} from "@mantine/core";
import { useEffect, useState } from "react";
import {useParams} from "react-router";
import { GameData } from "../interfaces/GameData";
import { getGameService } from "../Data";

function GamePage() {
    const {id} = useParams();
    const [gameData, setGameData] = useState<GameData | undefined>(undefined);

    useEffect(() => {
        if (id == undefined) {
            return;
        }

        getGameService().getGameData(id).then(game => {
            setGameData(game);
        });
    }, [id]);

    if (gameData == undefined) {
        return (
            <Stack
                align="center"
                justify="space-between">
                <h1 style={{fontSize: "5rem", textAlign: "center"}}>Chargement...</h1>
                <Loader color="CQI.0" size="xl"/>
            </Stack>
        );
    }

    return (
        <Container>
            <Text>{gameData.id}</Text>
        </Container>
    )
}

export default GamePage;
