import {Box, Group, Pagination, ScrollArea, Stack, Text} from "@mantine/core";
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

const LeaderBoard = ({leaderBoardData, setCurrentPage, setItemPerPage}: {
    leaderBoardData: LeaderboardData,
    setCurrentPage: React.Dispatch<React.SetStateAction<number>>,
    setItemPerPage: React.Dispatch<React.SetStateAction<number>>
}) => {
    const totalPages = Math.ceil(leaderBoardData.paginationData.totalItemCount / leaderBoardData.paginationData.itemsPerPage);

    return (
        <Stack
            mih={300}
            bg="var(--mantine-color-body)"
            align="stretch"
            justify="flex-start"
            gap="lg"
        >
            <ScrollArea>
                <div>
                    {leaderBoardData.gameData.map((item) => (
                        <Group key={item.id} style={{padding: '10px 0'}}>
                            <Box style={{width: '20%'}}>
                                <Text>{item.team1Id}</Text>
                            </Box>
                            <Box style={{width: '20%'}}>
                                <Text>{item.team2Id}</Text>
                            </Box>
                        </Group>
                    ))}
                </div>
            </ScrollArea>

            <Pagination total={totalPages} value={leaderBoardData.paginationData.page} onChange={setCurrentPage}
                        mt="sm"/>
        </Stack>
    );
}

export default LeaderBoard;
