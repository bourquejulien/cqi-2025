import {Grid} from "@mantine/core";
import React, {useEffect, useState} from "react";
import LeaderBoard, {LeaderboardData} from "../components/Leaderboard/Leaderboard.tsx";
import {getDataFetcher} from "../Data.ts";
import {Stats} from "../interfaces/Stats.ts";

// @ts-expect-error TS6198
function MainPage({setGameId, stats}: {
    setGameId: React.Dispatch<React.SetStateAction<string | undefined>>,
    stats: Stats
}) {
    const [currentPage, setCurrentPage] = useState(0);
    const [itemPerPage, setItemPerPage] = useState(10);
    const [gameData, setGameData] = useState<LeaderboardData>([]);

    useEffect(() => {
        const updateData = async () => {
            const response = await getDataFetcher().getLeaderBoardData(itemPerPage, currentPage);
            if (response.isSuccess) {
                setGameData(response.data);
            }
        }
        updateData();
        const interval = setInterval(updateData, 10_000);
        return () => {
            clearInterval(interval);
        };
    }, [currentPage, itemPerPage]);

    return (
        <Grid style={{height: "70%"}}>
            <Grid.Col span={3}>

            </Grid.Col>
            <Grid.Col span={6}>
                <LeaderBoard
                    leaderBoardData={{
                        paginationData: {
                            page: currentPage,
                            totalItemCount: stats.totalGames,
                            itemsPerPage: itemPerPage
                        }, gameData: gameData
                    }}
                    setCurrentPage={setCurrentPage}
                    setItemPerPage={setItemPerPage}/>
            </Grid.Col>
            <Grid.Col span={3}>

            </Grid.Col>
        </Grid>
    )
}

export default MainPage;
