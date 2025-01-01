import {GameData} from "../../interfaces/GameData.ts";
import {Card, Text, Stack} from "@mantine/core";
import {getPlayerService} from "../../Data.ts";
import {formatDuration} from "../../Helpers.ts";

const errorTypeToMessage = {
    "simple": "Une erreur s'est produite",
    "detailed": "Erreur détaillée avec logs",
    "timeout": "Le temps imparti a été dépassé",
    "nodata": "Aucune information sur la partie n'est disponible"
}

function InfoBubble({title, value}: { title: string, value: string }) {
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

function InfoPane({gameData}: {gameData: GameData}) {
    const playerService = getPlayerService();

    return (
        <Stack>
            {gameData.winnerId !== undefined ?
                <InfoBubble title={"Gagnant"} value={playerService.getPlayerNameOrDefault(gameData.winnerId)}/> : null}
            <InfoBubble title={"Score de " + playerService.getPlayerNameOrDefault(gameData.team1Id)} value={gameData.team1Score.toString()}/>
            <InfoBubble title={"Score de " + playerService.getPlayerNameOrDefault(gameData.team2Id)} value={gameData.team2Score.toString()}/>
            <InfoBubble title={"Durée"} value={formatDuration(gameData.startTime, gameData.endTime)}/>
            <InfoBubble title={"Période"} value={`De ${gameData.startTime.toLocaleTimeString()} à ${gameData.endTime.toLocaleTimeString()}`}/>

            <ErrorDescriptionBubble gameData={gameData}/>
        </Stack>
    );
}

export default InfoPane;
