import {useEffect, useRef} from 'react';
import {ScrollArea} from '@mantine/core';

function LogPane({logs}: {logs: string[]}) {
    const logEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        logEndRef.current?.scrollIntoView({behavior: 'smooth'});
    };

    useEffect(() => {
        scrollToBottom();
    }, []);

    return (
        <ScrollArea style={{height: '100%'}}>
            <div>
                {logs.map((log, index) => (
                    <div key={index}>{log}</div>
                ))}
                <div ref={logEndRef}/>
            </div>
        </ScrollArea>
    );
}

export default LogPane;
