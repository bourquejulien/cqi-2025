import React from "react";
import classes from "./Leaderboard.module.css";
import {Pagination, Stack, Table, Text} from "@mantine/core";
import {GameDataBase} from "../../interfaces/GameData.ts";
import {getPlayerService} from "../../Data.ts";
import {useNavigate} from "react-router";

export interface PaginationData {
    page: number;
    itemsPerPage: number;
    totalItemCount: number;
}

export interface LeaderboardData {
    paginationData: PaginationData;
    gameData: GameDataBase[];
}

function formatDuration(startTime: Date, endTime: Date): string {
    const durationMs = endTime.getTime() - startTime.getTime();
    if (durationMs <= 0) {
        return "0s";
    }

    const duration = new Date(durationMs);
    const minutes = duration.getMinutes() > 0 ? `${duration.getMinutes()}m` : "";
    return minutes + `${duration.getSeconds()}s`;
}

// @ts-expect-error TS6198
const LeaderBoard = ({leaderBoardData, setCurrentPage, setItemPerPage}: {
    leaderBoardData: LeaderboardData,
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>,
    setItemPerPage: React.Dispatch<React.SetStateAction<number>>,
}) => {
    const navigate = useNavigate();
    const playerService = getPlayerService();

    const rows = leaderBoardData.gameData.map((game) => {
        const team1Score = game.isError ? "N/A" : game.team1Score;
        const team2Score = game.isError ? "N/A" : game.team2Score;

        const team1Color = game.isError ? "dark.9" : game.winnerId === game.team1Id ? "green.7" : "dark.9";
        const team2Color = game.isError ? "dark.9" : game.winnerId === game.team2Id ? "green.7" : "dark.9";

        return (
            <Table.Tr className={classes.row} key={game.id} onClick={()=>navigate(`match/${game.id}`)}>
                <Table.Td style={{textAlign: "center"}}><Text
                    c={team1Color}>{playerService.getPlayerNameOrDefault(game.team1Id)}</Text></Table.Td>
                <Table.Td style={{textAlign: "center"}}><Text
                    c={team2Color}>{playerService.getPlayerNameOrDefault(game.team2Id)}</Text></Table.Td>
                <Table.Td style={{textAlign: "center"}}>{team1Score}</Table.Td>
                <Table.Td style={{textAlign: "center"}}>{team2Score}</Table.Td>
                <Table.Td style={{textAlign: "center"}}>{game.isError ? "❌" : "✅"}</Table.Td>
                <Table.Td style={{
                    textAlign: "center",
                    textWrap: "nowrap"
                }}>{formatDuration(game.startTime, game.endTime)}</Table.Td>
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
            className={"gdfgdfgdf"}
        >
            <Table>
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th style={{textAlign: "center"}}>Équipe 1</Table.Th>
                        <Table.Th style={{textAlign: "center"}}>Équipe 2</Table.Th>
                        <Table.Th style={{textAlign: "center"}}>Score équipe 2</Table.Th>
                        <Table.Th style={{textAlign: "center"}}>Score équipe 2</Table.Th>
                        <Table.Th style={{textAlign: "center"}}>Succès</Table.Th>
                        <Table.Th style={{textAlign: "center"}}>Durée</Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>{rows}</Table.Tbody>
            </Table>

            <Pagination
                total={Math.ceil(leaderBoardData.paginationData.totalItemCount / leaderBoardData.paginationData.itemsPerPage)}
                value={leaderBoardData.paginationData.page} onChange={setCurrentPage}
                mt="sm"/>
        </Stack>
    );
}

export default LeaderBoard;
