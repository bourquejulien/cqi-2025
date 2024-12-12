import {Grid, Title} from "@mantine/core";
import React, {useEffect, useState} from "react";
import LeaderBoard from "../components/Leaderboard/Leaderboard.tsx";
import {getDataFetcher} from "../Data.ts";
import {Stats} from "../interfaces/Stats.ts";
import {GameDataBase} from "../interfaces/GameData.ts";
import {LeftPane} from "../components/LeftPane/LeftPane.tsx";

function MainPage({setGameId, stats}: {
    setGameId: React.Dispatch<React.SetStateAction<string | undefined>>,
    stats: Stats
}) {
    const [currentPage, setCurrentPage] = useState(1);
    const [itemPerPage, setItemPerPage] = useState(10);
    const [gameData, setGameData] = useState<GameDataBase[]>([]);

    useEffect(() => {
        const updateData = async () => {
            const response = await getDataFetcher().getLeaderBoardData(itemPerPage, Math.max(0, currentPage - 1));
            if (response.isSuccess) {
                setGameData(response.data.results);
            }
        }
        updateData();
        const interval = setInterval(updateData, 30_000);
        return () => {
            clearInterval(interval);
        };
    }, [currentPage, itemPerPage]);

    return (
        <Grid style={{height: "70%"}} gutter={"xl"}>
            <Grid.Col span={3} offset={0}>
                <Title order={3} style={{textAlign: "center"}}>Match en cours</Title>
                <LeftPane/>
            </Grid.Col>
            <Grid.Col span={6} offset={1}>
                <Title order={1} style={{textAlign: "center"}}>Classement</Title>
                <LeaderBoard
                    leaderBoardData={{
                        paginationData: {
                            page: currentPage,
                            totalItemCount: stats.totalGames,
                            itemsPerPage: itemPerPage
                        }, gameData: gameData
                    }}
                    setCurrentPage={setCurrentPage}
                    setItemPerPage={setItemPerPage}
                    setGameId={setGameId}/>
            </Grid.Col>
            <Grid.Col span={3}>

            </Grid.Col>
        </Grid>
    )
}

export default MainPage;
