import {useEffect, useRef} from 'react';
import {Box, Card, Divider, Group, ScrollArea, Text} from '@mantine/core';

function LogPane({logs}: { logs: string[] }) {
    const viewport = useRef<HTMLDivElement>(null);
    const scrollToBottom = () =>
        viewport.current!.scrollTo({top: viewport.current!.scrollHeight, behavior: 'smooth'});

    useEffect(() => {
        scrollToBottom();
    }, [logs]);

    return (
        <Card shadow="sm" padding="lg" radius="md" withBorder h={"100%"} w={"100%"}>
            <ScrollArea style={{height: '100%'}} viewportRef={viewport}>
                {logs.map((log, index) => (
                    <Box key={index}>
                        <Group wrap={"nowrap"}>
                            <Text fw={700}>{index + 1}:</Text>
                            <Text>{log}</Text>
                        </Group>

                        <Divider variant={"dashed"} size={"sm"}/>
                    </Box>
                ))}
            </ScrollArea>
        </Card>
    );
}

export default LogPane;
