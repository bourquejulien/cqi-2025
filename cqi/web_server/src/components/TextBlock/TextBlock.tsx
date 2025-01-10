import {Card, getGradient, Text, useMantineTheme} from "@mantine/core";
import {useMediaQuery} from "@mantine/hooks";

function TextBox({text}: { text: string }) {
    const isSmall = useMediaQuery("(max-width: 50rem)");
      
    return (
        <Card
            shadow="sm"
            padding={isSmall ? "5px" : "xl"}
            radius="md"
            h={"7rem"}
            withBorder
            style={{
                justifyContent: "center",
                alignItems: "center",
                backgroundImage: getGradient({from: "CQI.0", to: "CQI.4", deg: 0}, useMantineTheme())
            }}
        >
            <Text fw={700} size={isSmall ? "md" : "xl"}>{text}</Text>
        </Card>
    );
}

export default TextBox;
