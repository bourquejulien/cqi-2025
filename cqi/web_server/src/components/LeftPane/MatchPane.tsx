import {Table, Text} from "@mantine/core";
import {Match} from "../../interfaces/Match.ts";
import {JSX, useEffect, useState} from "react";
import {getPlayerService} from "../../Data.ts";

function getSecondsSince(date: Date): number {
    const now = new Date();
    return Math.floor((now.getTime() - date.getTime()) / 1000);
}

function getRows(ongoingMatches: Match[]): JSX.Element[] {
    const playerService = getPlayerService();
    return ongoingMatches.map((match) => {

        return (
            <Table.Tr key={match.id}>
                <Table.Td><Text>{playerService.getPlayerNameOrDefault(match.team1Id)}</Text></Table.Td>
                <Table.Td><Text>{playerService.getPlayerNameOrDefault(match.team2Id)}</Text></Table.Td>
                <Table.Td>{getSecondsSince(match.startTime)}s</Table.Td>
            </Table.Tr>
        )
    });
}

export function MatchPane({matches}: { matches: Match[] }) {
    const [rows, setRows] = useState<JSX.Element[]>(getRows(matches));

    useEffect(() => {
        const interval = setInterval(() => {
            setRows(getRows(matches));
        }, 1000);

        return () => clearInterval(interval)
    }, [matches]);

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
