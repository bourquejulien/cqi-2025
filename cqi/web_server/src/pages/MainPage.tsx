import {Grid} from "@mantine/core";
import React from "react";
import LeaderBoard from "../components/Leaderboard/Leaderboard.tsx";

function MainPage({gameId, setGameId}: {
    gameId: string | undefined;
    setGameId: React.Dispatch<React.SetStateAction<string | undefined>>
}) {
    return (
        <Grid style={{height: "70%"}}>
            <Grid.Col span={3}>

            </Grid.Col>
            <Grid.Col span={6}>
                <LeaderBoard
                    leaderBoardData={{paginationData: {page: 0, totalItemCount: 0, itemsPerPage: 10}, gameData: []}}
                    setCurrentPage={() => {
                    }} setItemPerPage={() => {
                }}/>
            </Grid.Col>
            <Grid.Col span={3}>

            </Grid.Col>
        </Grid>
    )
}

export default MainPage;
