import {GameStep} from "../../interfaces/SuccessData.ts";
import {ActionIcon, Flex, Grid, Pagination, Stack, Text, Title, Tooltip} from "@mantine/core";
import Map from "./Map.tsx";
import {useEffect, useState} from "react";
import LogPane from "./LogPane.tsx";
import {FaDownload} from "react-icons/fa6";
import ReactDOMServer from 'react-dom/server';
import {downloadBlob, generateZip} from "../../Helpers.ts";

async function downloadMap(steps: GameStep[]) {
    const svgs: [string, string][] = steps
        .map((step) => ReactDOMServer.renderToStaticMarkup(<Map map={step.map}/>))
        .map((svg, i) => [`map_${i + 1}.svg`, svg]);

    const zipBlob = await generateZip(svgs);
    downloadBlob(zipBlob, "maps.zip");
}

function StepPane({steps}: { steps: GameStep[] }) {
    const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);

    useEffect(() => {
        setCurrentStepIndex(0)
    }, [steps.length]);

    if (steps.length === 0) {
        return <Text>Aucune donnée n'est disponible</Text>
    }

    return (
        <Stack w={"100%"} align={"center"} gap={"xl"}>
            <Grid align={"stretch"} w={"100%"}>
                <Grid.Col span={{base: 12, md: 8, lg: 8}}>
                    <Map map={steps[Math.min(currentStepIndex, steps.length - 1)].map}/>
                </Grid.Col>
                <Grid.Col span={{base: 12, md: 4, lg: 4}}>
                    <Title order={3}>Logs du serveur de partie</Title>
                    <LogPane logs={steps[Math.min(currentStepIndex, steps.length - 1)].logs}/>
                </Grid.Col>
            </Grid>
            <Flex align={"center"} justify={"center"} gap={"xl"}>
                <Tooltip label="Télécharger les cartes">
                    <ActionIcon
                        onClick={() => downloadMap(steps.slice())}
                        variant="gradient"
                        size="xl"
                        aria-label="Gradient action icon"
                        gradient={{from: 'CQI.1', to: 'CQI.3', deg: 90}}
                    >
                        <FaDownload/>
                    </ActionIcon>
                </Tooltip>
                <Pagination
                    total={steps.length}
                    value={currentStepIndex + 1}
                    onChange={(value) => setCurrentStepIndex(value - 1)}
                    mt="sm"/>
            </Flex>

        </Stack>
    );
}

export default StepPane;
