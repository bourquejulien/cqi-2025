import {Table, Text} from "@mantine/core";
import {Match} from "../../interfaces/Match.ts";
import {useEffect, useState} from "react";
import {getDataFetcher} from "../../Data.ts";


function getMinutesSince(date: Date): number {
    const now = new Date();
    return Math.floor((now.getTime() - date.getTime()) / 60000);
}

function getMatches() {
    return getDataFetcher().getOngoingMatches().then((response) => {
        if (response.isSuccess) {
            return response.data.map((match) => {
                return {
                    id: match.id,
                    team1Id: match.team1Id,
                    team2Id: match.team2Id,
                    startTime: new Date(match.startTime)
                } as Match;
            });
        }
        return [];
    });
}

export function LeftPane() {

    const [ongoingMatches, setOngoingMatches] = useState<Match[]>([]);

    useEffect(() => {
        getMatches().then((matches) => {
            setOngoingMatches(matches);
        });

        const interval = setInterval(() => {
            getMatches().then((matches) => {
                setOngoingMatches(matches);
            });
        }, 30_000);

        return () => clearInterval(interval)
    }, []);

    const rows = ongoingMatches.map((match) => {

        return (
            <Table.Tr key={match.id}>
                <Table.Td><Text>{match.team1Id}</Text></Table.Td>
                <Table.Td><Text>{match.team2Id}</Text></Table.Td>
                <Table.Td>{getMinutesSince(match.startTime)}</Table.Td>
            </Table.Tr>
        )
    });

    return (
        <Table>
            <Table.Thead>
                <Table.Tr>
                    <Table.Th>Équipe 1</Table.Th>
                    <Table.Th>Équipe 2</Table.Th>
                    <Table.Th>Durée</Table.Th>
                </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{rows}</Table.Tbody>
        </Table>
    )
}