import {GameStep} from "../../interfaces/SuccessData.ts";
import {Grid, Pagination, Stack, Text, Title} from "@mantine/core";
import Map from "./Map.tsx";
import {useEffect, useState} from "react";
import LogPane from "./LogPane.tsx";

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
            <Pagination
                total={steps.length}
                value={currentStepIndex + 1}
                onChange={(value) => setCurrentStepIndex(value - 1)}
                mt="sm"/>
        </Stack>
    );
}

export default StepPane;
