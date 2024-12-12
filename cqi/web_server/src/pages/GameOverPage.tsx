import {Container, Stack, Text} from "@mantine/core";

export function GameOverPage() {
    return (
        <Container fluid style={{
            backgroundColor: 'orange',
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }}>
            <Stack
                align="stretch"
                justify="space-around">
                <h1 style={{fontSize: "5rem", textAlign: "center"}}>C'est terminé</h1>
                <Text size={"1.5rem"}>
                    Veuillez vous assurer de remettre la dernière version de votre conteneur ansi que l'ensemble de
                    votre code.
                </Text>
            </Stack>
        </Container>
    )
}
