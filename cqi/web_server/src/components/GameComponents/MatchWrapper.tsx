import {GameStep, MatchData} from "../../interfaces/SuccessData.ts";
import {ActionIcon, Flex, Select, Stack, Title, Tooltip} from "@mantine/core";
import StepPane from "./StepPane.tsx";
import {getPlayerService} from "../../Data.ts";
import {useState} from "react";
import ReactDOMServer from "react-dom/server";
import Map from "./Map.tsx";
import {downloadBlob, generateZip} from "../../Helpers.ts";
import {FaDownload} from "react-icons/fa";

async function downloadMap(steps: GameStep[]) {
    const svgs: [string, string][] = await Promise.all(steps
        .map(async (step) => {
            await new Promise((resolve) => setTimeout(resolve, 5));
            return ReactDOMServer.renderToStaticMarkup(<Map fixedSize step={step}/>);
        })
        .map(async (svg, i) => [`map_${i + 1}.svg`, await svg]));

    const zipBlob = await generateZip(svgs);
    downloadBlob(zipBlob, "maps.zip");
}

function MapDownloadButton({steps}: { steps: GameStep[] }) {
    const [loading, setLoading] = useState<boolean>(false);

    const download = async (steps: GameStep[]) => {
        setLoading(true);
        await downloadMap(steps).catch(console.error);
        setLoading(false);
    }

    return (
        <Tooltip label="Télécharger les cartes">
            <ActionIcon
                loaderProps={{type: 'dots'}}
                loading={loading}
                onClick={async () => await download(steps.slice())}
                variant="gradient"
                size="xl"
                aria-label="Gradient action icon"
                gradient={{from: 'CQI.1', to: 'CQI.3', deg: 90}}
            >
                <FaDownload/>
            </ActionIcon>
        </Tooltip>
    );
}

function MatchWrapper({matches}: { matches: MatchData[] }) {
    const playerService = getPlayerService();
    const [selectedMatch, setSelectedMatch] = useState<MatchData>(matches[0]);

    return (
        <Stack align={"center"}>
            <Title order={2}>Détails de la partie</Title>

            <Flex align={"center"} justify={"center"} gap={"2rem"}>
                <Select
                    w={"20rem"}
                    data={matches.map((match) => ({
                        value: match.offenseTeamId + match.defenseTeamId,
                        label: playerService.getPlayerNameOrDefault(match.offenseTeamId) + " (O)" + " vs " + playerService.getPlayerNameOrDefault(match.defenseTeamId) + " (D)"
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
                <MapDownloadButton steps={selectedMatch.steps}/>
            </Flex>

            <StepPane steps={selectedMatch.steps}/>
        </Stack>
    );
}

export default MatchWrapper;
