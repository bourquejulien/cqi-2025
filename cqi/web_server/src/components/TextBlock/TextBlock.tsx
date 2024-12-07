import {Box, Text} from "@mantine/core";

function TextBox({ text }: { text: string }) {
  return (
    <Box
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100px",
        backgroundColor: "var(--mantine-color-gray-0)",
        borderRadius: "8px",
        border: "1px solid var(--mantine-color-gray-3)",
      }}
    >
      <Text>{text}</Text>
    </Box>
  );
}

export default TextBox;
