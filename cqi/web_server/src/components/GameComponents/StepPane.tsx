import {GameStep} from "../../interfaces/SuccessData.ts";
import {Grid, Pagination, Stack, Text, Title} from "@mantine/core";
import Map from "./Map.tsx";
import {useEffect, useState} from "react";
import LogPane from "./LogPane.tsx";
import {useMediaQuery} from "@mantine/hooks";

function StepPane({steps}: { steps: GameStep[] }) {
    const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
    const [width, setWidth] = useState(window.innerWidth);
    const isSmall = useMediaQuery("(max-width: 50rem)");

    useEffect(() => {
        setCurrentStepIndex(0)
    }, [steps]);

    useEffect(() => {
        const handleResize = () => setWidth(window.innerWidth);
        window.addEventListener("resize", () => setWidth(window.innerWidth));
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    useEffect(() => {
        const bindingsKeyDown = (e: KeyboardEvent) => {
            if (e.key === "ArrowLeft") {
                setCurrentStepIndex((index) => Math.max(0, index - 1));
            } else if (e.key === "ArrowRight") {
                setCurrentStepIndex((index) => Math.min(steps.length - 1, index + 1));
            }
        };

        document.addEventListener("keydown", bindingsKeyDown);
        return () => {
            document.removeEventListener("keydown", bindingsKeyDown);
        };
    }, [steps]);

    if (steps.length === 0) {
        return <Text>Aucune donnée n'est disponible</Text>
    }

    return (
        <Stack w={"100%"} align={"center"} gap={"xl"}>
            <Grid justify={"space-evenly"} align={"stretch"} w={"inherit"}>
                <Grid.Col span={"content"}>
                    <Map maxWidth={width} step={steps[Math.min(currentStepIndex, steps.length - 1)]}/>
                </Grid.Col>
                <Grid.Col span={{base: 12, md: 4, lg: 4}}>
                    <Stack align={"center"} h={"100%"}>
                        <Title order={3}>Logs du serveur de partie</Title>
                        <LogPane logs={steps[Math.min(currentStepIndex, steps.length - 1)].logs}/>
                    </Stack>
                </Grid.Col>
            </Grid>
            <Pagination
                size={isSmall ? "sm" : "lg"}
                radius={"md"}
                total={steps.length}
                value={currentStepIndex + 1}
                onChange={(value) => setCurrentStepIndex(value - 1)}
                mt="sm"/>
        </Stack>
    );
}

export default StepPane;
