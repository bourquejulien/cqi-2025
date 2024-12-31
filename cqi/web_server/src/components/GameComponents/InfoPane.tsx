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
            <Text size="md" c="dimmed">{value}</Text>
        </Card>
    )
}

function ErrorDescriptionBubble({gameData}: { gameData: GameData }) {
    if (!gameData.isError) {
        return <></>;
    }

    const errorMessage = "message" in gameData.errorData ? gameData.errorData.message : errorTypeToMessage[gameData.errorData.errorType];
    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text size="lg" c={"red"}>Erreur</Text>
            <Text size="md" c="dimmed">{errorMessage}</Text>
        </Card>
    );
}

function InfoPane({gameData}: {gameData: GameData}) {
    const playerService = getPlayerService();

    console.log(gameData.winnerId);

    return (
        <Stack>
            {gameData.winnerId !== undefined ?
                <InfoBubble title={"Gagnant"} value={playerService.getPlayerNameOrDefault(gameData.winnerId)}/> : null}
            <InfoBubble title={"Score: " + playerService.getPlayerNameOrDefault(gameData.team1Id)} value={gameData.team1Score.toString()}/>
            <InfoBubble title={"Score: " + playerService.getPlayerNameOrDefault(gameData.team2Id)} value={gameData.team2Score.toString()}/>
            <InfoBubble title={"Durée"} value={formatDuration(gameData.startTime, gameData.endTime)}/>
            <InfoBubble title={"Début - Fin"} value={gameData.startTime.toLocaleTimeString() + " - " + gameData.endTime.toLocaleTimeString()}/>

            <ErrorDescriptionBubble gameData={gameData}/>
        </Stack>
    );
}

export default InfoPane;
