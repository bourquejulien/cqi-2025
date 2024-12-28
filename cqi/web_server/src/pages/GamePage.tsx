import {Container, Text} from "@mantine/core";
import {useParams} from "react-router";

function GamePage() {
    const {id} = useParams();
    return (
        <Container>
            <Text>{id}</Text>
        </Container>
    )
}

export default GamePage;
