import {Grid, Title} from "@mantine/core";
import {useEffect, useState} from "react";
import LeaderBoard from "../components/Leaderboard/Leaderboard.tsx";
import {getDataFetcher} from "../Data.ts";
import {Stats} from "../interfaces/Stats.ts";
import {GameDataBase} from "../interfaces/GameData.ts";
import {MatchPane} from "../components/Panes/MatchPane.tsx";
import {Match} from "../interfaces/Match.ts";
import Ranking from "../components/Panes/Ranking.tsx";

function MainPage({stats, setIsReady}: {
    stats: Stats
    setIsReady: (isReady: boolean) => void
}) {
    const [currentPage, setCurrentPage] = useState(1);
    const [itemPerPage, setItemPerPage] = useState(20);
    const [gameData, setGameData] = useState<GameDataBase[]>([]);
    const [ongoingMatches, setOngoingMatches] = useState<Match[]>([]);

    useEffect(() => {
        const updateData = async () => {
            const response = await getDataFetcher().getLeaderBoardData(itemPerPage, Math.max(0, currentPage - 1));
            const matches = await getDataFetcher().getOngoingMatches();

            if (response.isSuccess && matches.isSuccess) {
                setGameData(response.data.results);
                setOngoingMatches(matches.data);
            } else if (!response.isSuccess && !response.isGameEnded && gameData.length === 0) {
                setIsReady(false);
            }
        }

        updateData();
        const interval = setInterval(updateData, 20_000);
        return () => {
            clearInterval(interval);
        };
    }, [currentPage, itemPerPage, setIsReady]);

    return (
        <Grid gutter={"xl"}>
            <Grid.Col span={{base: 12, md: 6, lg: 3}}>
                <Title order={2} style={{textAlign: "center"}}>Parties en cours</Title>
                <MatchPane matches={ongoingMatches}/>
            </Grid.Col>
            <Grid.Col span={{base: 12, md: 6, lg: 6}}>
                <Title order={1} style={{textAlign: "center"}}>Résultats</Title>
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
            <Grid.Col span={{base: 12, md: 6, lg: 3}}>
                <Title order={2} style={{textAlign: "center"}}>Classement</Title>
                <Ranking rankingInfo={stats.rankingInfo}/>
            </Grid.Col>
        </Grid>
    )
}

export default MainPage;
