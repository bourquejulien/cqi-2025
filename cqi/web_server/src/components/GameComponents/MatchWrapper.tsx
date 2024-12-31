import {MatchData} from "../../interfaces/SuccessData.ts";
import {Select, Stack, Title} from "@mantine/core";
import StepPane from "./StepPane.tsx";
import {getPlayerService} from "../../Data.ts";
import {useState} from "react";

function MatchWrapper({matches}: { matches: MatchData[] }) {
    const playerService = getPlayerService();
    const [selectedMatch, setSelectedMatch] = useState<MatchData>(matches[0]);

    return (
        <Stack align={"center"}>
            <Title order={2}>Détails de la partie</Title>
            <Select
                data={matches.map((match) => ({
                    value: match.offenseTeamId + match.defenseTeamId,
                    label: playerService.getPlayerNameOrDefault(match.offenseTeamId) + " vs " + playerService.getPlayerNameOrDefault(match.defenseTeamId)
                }))}
                placeholder="Sélectionner un match"
                value={selectedMatch.offenseTeamId + selectedMatch.defenseTeamId}
                onChange={(value) => {
                    const selectedMatch = matches.find((match) => match.offenseTeamId + match.defenseTeamId === value);
                    if (selectedMatch !== undefined) {
                        setSelectedMatch(selectedMatch);
                    }
                }}
            />
            <StepPane steps={selectedMatch.steps}/>
        </Stack>
    );
}

export default MatchWrapper;
