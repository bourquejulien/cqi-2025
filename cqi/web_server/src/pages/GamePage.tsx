import {Grid, Loader, Stack, Title} from "@mantine/core";
import {useEffect, useState} from "react";
import {useParams} from "react-router";
import {GameData, GameFailure, GameSuccess} from "../interfaces/GameData";
import {getGameService, getPlayerService} from "../Data";
import {DetailedError, ErrorDataOther, SimpleError} from "../interfaces/ErrorData.ts";
import InfoPane from "../components/GameComponents/InfoPane.tsx";
import OutputLogWrapper, {Logs} from "../components/GameComponents/OutputLogWrapper.tsx";
import MatchWrapper from "../components/GameComponents/MatchWrapper.tsx";

const playerService = getPlayerService();

function SimpleErrorLayout({gameFailure}: { gameFailure: GameFailure<SimpleError | ErrorDataOther> }) {
    return (
        <Grid>
            <InfoPane gameData={gameFailure}/>
        </Grid>
    );
}

function DetailedErrorLayout({gameFailure}: { gameFailure: GameFailure<DetailedError> }) {
    const logs: Logs[] = gameFailure.errorData.matches.map(match => {
        return [
            {
                name: playerService.getPlayerNameOrDefault(match.offenseTeamId) + " (O)",
                logs: match.logs.offense
            },
            {
                name: playerService.getPlayerNameOrDefault(match.defenseTeamId) + " (D)",
                logs: match.logs.defense
            }
        ]
    }).flat();

    return (
        <Grid>
            <InfoPane gameData={gameFailure}/>
            <OutputLogWrapper teamLogs={logs}/>
        </Grid>
    );
}

function SuccessLayout({gameSuccess}: { gameSuccess: GameSuccess }) {
    const logs: Logs[] = gameSuccess.gameData.matches.map(match => {
        return [
            {
                name: playerService.getPlayerNameOrDefault(match.offenseTeamId) + " (O)",
                logs: match.logs.offense
            },
            {
                name: playerService.getPlayerNameOrDefault(match.defenseTeamId) + " (D)",
                logs: match.logs.defense
            }
        ]
    }).flat();

    return (
        <Grid>
            <InfoPane gameData={gameSuccess}/>
            <OutputLogWrapper teamLogs={logs}/>
            <MatchWrapper matches={gameSuccess.gameData.matches}/>
        </Grid>
    );
}

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

    const Layout = () => {
        if (!gameData.isError) {
            return <SuccessLayout gameSuccess={gameData}/>
        }

        if (gameData.errorData.errorType === "detailed") {
            return <DetailedErrorLayout gameFailure={gameData as GameFailure<DetailedError>}/>
        }

        return <SimpleErrorLayout gameFailure={gameData as GameFailure<SimpleError | ErrorDataOther>}/>
    };


    return (
        <Stack
            align={"center"}
            justify={"space-evenly"}
            gap={"lg"}
        >
            <Title>{playerService.getPlayerNameOrDefault(gameData.team1Id)} VS {gameData.team2Id}</Title>
            <Layout/>
        </Stack>
    )
}

export default GamePage;
