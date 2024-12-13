import {Container, Image, Loader, Stack} from "@mantine/core";

export function LoadingPage() {
    return (
        <Container fluid style={{
            backgroundColor: 'white',
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
        }}>
            <Stack
                h={"50%"}
                align="center"
                justify="space-around"
                      gap="md"
            >
                <Image src={"/logo.png"} alt="Logo"/>
                <Loader color="CQI.0" size="xl"/>
            </Stack>
        </Container>
    )
}
