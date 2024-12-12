import {Pagination, Stack, Table, Text} from "@mantine/core";
import React from "react";
import {GameDataBase} from "../../interfaces/GameData.ts";

export interface PaginationData {
    page: number;
    itemsPerPage: number;
    totalItemCount: number;
}

export interface LeaderboardData {
    paginationData: PaginationData;
    gameData: GameDataBase[];
}

// @ts-expect-error TS6198
const LeaderBoard = ({leaderBoardData, setCurrentPage, setItemPerPage, setGameId}: {
    leaderBoardData: LeaderboardData,
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>,
    setItemPerPage: React.Dispatch<React.SetStateAction<number>>,
    setGameId: React.Dispatch<React.SetStateAction<string | undefined>>
}) => {
    const rows = leaderBoardData.gameData.map((game) => {
        const team1Score = game.isError ? "N/A" : game.team1Score;
        const team2Score = game.isError ? "N/A" : game.team2Score;

        const team1Color = game.isError ? "dark.9" : game.winnerId === game.team1Id ? "green.7" : "dark.9";
        const team2Color = game.isError ? "dark.9" : game.winnerId === game.team2Id ? "green.7" : "dark.9";

        return (
            <Table.Tr key={game.id}>
                <Table.Td><Text c={team1Color}>{game.team1Id}</Text></Table.Td>
                <Table.Td><Text c={team2Color}>{game.team2Id}</Text></Table.Td>
                <Table.Td>{team1Score}</Table.Td>
                <Table.Td>{team2Score}</Table.Td>
                <Table.Td>{game.isError ? "Yes" : "No"}</Table.Td>
            </Table.Tr>
        )
    });

    return (
        <Stack
            mih={300}
            bg="var(--mantine-color-body)"
            align="center"
            justify="flex-start"
            gap="lg"
        >
            <Table>
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th>Team 1</Table.Th>
                        <Table.Th>Team 2</Table.Th>
                        <Table.Th>Team 1 score</Table.Th>
                        <Table.Th>Team 2 score</Table.Th>
                        <Table.Th>Failed</Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>{rows}</Table.Tbody>
            </Table>

            <Pagination total={Math.ceil(leaderBoardData.paginationData.totalItemCount / leaderBoardData.paginationData.itemsPerPage)} value={leaderBoardData.paginationData.page} onChange={setCurrentPage}
                        mt="sm"/>
        </Stack>
    );
}

export default LeaderBoard;
