import {GameStep} from "../../interfaces/SuccessData.ts";
import {Grid, Pagination, Stack, Text} from "@mantine/core";
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
        <Stack>
            <Grid>
                <Map map={steps[Math.min(currentStepIndex, steps.length - 1)].map}/>
                <LogPane logs={steps[Math.min(currentStepIndex, steps.length - 1)].logs}/>
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
