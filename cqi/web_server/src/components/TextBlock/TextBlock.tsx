import {Card, getGradient, Text, useMantineTheme} from "@mantine/core";

function TextBox({text}: { text: string }) {
    return (
        <Card
            shadow="sm"
            padding="lg"
            radius="md"
            h={"7rem"}
            withBorder

            style={{
                justifyContent: "center",
                alignItems: "center",
                backgroundImage: getGradient({from: 'CQI.0', to: 'CQI.4', deg: 0}, useMantineTheme())
            }}
        >
            <Text fw={800} size="xl">{text}</Text>
        </Card>
    );
}

export default TextBox;
