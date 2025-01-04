import {Anchor, Container, Group, Stack, Text} from "@mantine/core";

export function GameOverPage() {
    return (
        <Container fluid style={{
            backgroundColor: "var(--mantine-color-CQI-0)",
            height: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center"
        }}>
            <Stack
                align="center"
                justify="space-around">
                <h1 style={{fontSize: "5rem", textAlign: "center"}}>C'est terminé</h1>
                <Text size={"1.5rem"}>
                    Veuillez vous assurer de remettre la dernière version de votre conteneur ansi que l'ensemble de
                    votre code.
                </Text>
                <Group wrap={"nowrap"}>
                    <Text size={"2rem"}>👉</Text>
                    <Anchor size={"1.5rem"} href={"http://remise.cqiprog.info"}>Formulaire de remise</Anchor>
                </Group>
            </Stack>
        </Container>
    )
}
