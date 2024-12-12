import {Box, Text} from "@mantine/core";

function TextBox({text}: { text: string }) {
    return (
        <Box
            style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: "100px",
                backgroundColor: "var(--mantine-color-CQI-2)",
                borderRadius: "8px",
            }}
        >
            <Text fw={700} size="md">{text}</Text>
        </Box>
    );
}

export default TextBox;
