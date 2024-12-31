import {Select, Stack} from "@mantine/core";
import LogPane from "./LogPane.tsx";
import {useState} from "react";

export interface Logs {
    name: string;
    logs: string[];
}

function OutputLogWrapper({teamLogs}: {teamLogs: Logs[]}) {
    const [selectedLog, setSelectedLog] = useState<Logs>(teamLogs.length > 0 ? teamLogs[0] : {name: "", logs: []});

    return (
        <Stack>
            <Select
                data={teamLogs.map((log) => log.name)}
                placeholder="Sélectionner un conteneur"
                onChange={(value) => {
                    const selectedLog = teamLogs.find((log) => log.name === value);
                    if (selectedLog) {
                        setSelectedLog(selectedLog);
                    }
                }}
            />
            <LogPane logs={selectedLog.logs}/>
        </Stack>
    );
}

export default OutputLogWrapper;
