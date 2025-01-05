import {GameData} from "../../interfaces/GameData.ts";
import {Card, Text, Stack} from "@mantine/core";
import {getPlayerService} from "../../Data.ts";
import {formatDuration} from "../../Helpers.ts";
import {SuccessData} from "../../interfaces/SuccessData.ts";
import {useEffect, useState} from "react";

const errorTypeToMessage = {
    "simple": "Une erreur s'est produite",
    "detailed": "Erreur détaillée avec logs",
    "timeout": "Le temps imparti a été dépassé",
    "nodata": "Aucune information sur la partie n'est disponible"
}

function InfoBubble({title, value}: { title: string, value: string}) {
    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text size="lg">{title}</Text>
            <Text size="md" c="CQI.2">{value}</Text>
        </Card>
    )
}

function ErrorDescriptionBubble({gameData}: { gameData: GameData }) {
    if (!gameData.isError) {
        return <></>;
    }

    const errorDescription = "message" in gameData.errorData ? "Erreur lors du lancement de la partie" : "Erreur";
    const errorMessage = "message" in gameData.errorData ? gameData.errorData.message : errorTypeToMessage[gameData.errorData.errorType];

    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text size="lg" c={"red"}>{errorDescription}</Text>
            <Text size="md" c="CQI.2">{errorMessage}</Text>
        </Card>
    );
}

function getSuccessInfo(successData: SuccessData): [string, string][] {
    return [["Nombre de déplacements maximum", successData.maxMoveCount.toString()],]
}

function InfoPane({game}: {game: GameData}) {
    const playerService = getPlayerService();
    const [successData, setSuccessData] = useState<SuccessData | undefined>(undefined);

    useEffect(() => {
        if (game.isError) {
            return;
        }
        setSuccessData(game.gameData as SuccessData);
    }, [game]);

    return (
        <Stack>
            {game.winnerId !== undefined ?
                <InfoBubble title={"Gagnant"} value={playerService.getPlayerNameOrDefault(game.winnerId)}/> : null}
            <InfoBubble title={"Score de " + playerService.getPlayerNameOrDefault(game.team1Id)} value={game.team1Score.toString()}/>
            <InfoBubble title={"Score de " + playerService.getPlayerNameOrDefault(game.team2Id)} value={game.team2Score.toString()}/>
            <InfoBubble title={"Durée"} value={formatDuration(game.startTime, game.endTime)}/>
            <InfoBubble title={"Période"} value={`De ${game.startTime.toLocaleTimeString()} à ${game.endTime.toLocaleTimeString()}`}/>

            {successData !== undefined ? getSuccessInfo(successData).map(([title, value]) => (
                <InfoBubble key={title} title={title} value={value}/>
            )) : null}

            <ErrorDescriptionBubble gameData={game}/>
        </Stack>
    );
}

export default InfoPane;
