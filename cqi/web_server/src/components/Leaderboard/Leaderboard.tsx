import React from "react";
import classes from "./Leaderboard.module.css";
import {Pagination, Stack, Table, Text} from "@mantine/core";
import {GameDataBase} from "../../interfaces/GameData.ts";
import {getPlayerService} from "../../Data.ts";
import {useNavigate} from "react-router";
import {formatDuration} from "../../Helpers.ts";
import {FaExclamationTriangle} from "react-icons/fa";
import {FaCircleCheck} from "react-icons/fa6";
import {useMediaQuery} from "@mantine/hooks";

export interface PaginationData {
    page: number;
    itemsPerPage: number;
    totalItemCount: number;
}

export interface LeaderboardData {
    paginationData: PaginationData;
    gameData: GameDataBase[];
}

function ScalableText({isSmallPage, text, c}: { isSmallPage: boolean, text: string, c?: string }) {
    return (
        <Text size={isSmallPage ? "xs" : "md"} c={c}>{text}</Text>
    );
}

// @ts-expect-error TS6198
const LeaderBoard = ({leaderBoardData, setCurrentPage, setItemPerPage}: {
    leaderBoardData: LeaderboardData,
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>,
    setItemPerPage: React.Dispatch<React.SetStateAction<number>>,
}) => {
    const navigate = useNavigate();
    const playerService = getPlayerService();

    const isSmallPage = useMediaQuery("(max-width: 30rem)") ?? false;

    const rows = leaderBoardData.gameData.map((game) => {
        const team1Score = game.isError ? "N/A" : game.team1Score;
        const team2Score = game.isError ? "N/A" : game.team2Score;

        const team1Color = game.isError ? "dark.9" : game.winnerId === game.team1Id ? "green.8" : "dark.9";
        const team2Color = game.isError ? "dark.9" : game.winnerId === game.team2Id ? "green.8" : "dark.9";

        return (
            <Table.Tr className={classes.row} key={game.id} onClick={() => navigate(`game/${game.id}`)}>
                <Table.Td style={{textAlign: "center"}}>
                    <ScalableText c={team1Color} text={playerService.getPlayerNameOrDefault(game.team1Id)}
                                  isSmallPage={isSmallPage}/>
                </Table.Td>
                <Table.Td style={{textAlign: "center"}}>
                    <ScalableText c={team2Color} text={playerService.getPlayerNameOrDefault(game.team2Id)}
                                  isSmallPage={isSmallPage}/>
                </Table.Td>
                <Table.Td style={{textAlign: "center"}}>{team1Score}</Table.Td>
                <Table.Td style={{textAlign: "center"}}>{team2Score}</Table.Td>
                <Table.Td style={{textAlign: "center"}}>{game.isError ?
                    <FaExclamationTriangle color={"var(--mantine-color-red-8)"}/> :
                    <FaCircleCheck color={"var(--mantine-color-green-8)"}/>}</Table.Td>
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
            align="center"
            gap="lg"
        >
            <Table withColumnBorders>
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
