import {Grid, Title} from "@mantine/core";
import {useEffect, useState} from "react";
import LeaderBoard from "../components/Leaderboard/Leaderboard.tsx";
import {getDataFetcher} from "../Data.ts";
import {Stats} from "../interfaces/Stats.ts";
import {GameDataBase} from "../interfaces/GameData.ts";
import {MatchPane} from "../components/Panes/MatchPane.tsx";
import Ranking from "../components/Panes/Ranking.tsx";
import {useNavigate, useParams} from "react-router";

function safeParseInt(value: string | undefined): number {
    const minValue = 0;

    if (value === undefined) {
        return minValue;
    }

    const result = parseInt(value);
    if (isNaN(result) || result < minValue) {
        return minValue;
    }

    return Math.floor(result);
}

function MainPage({stats, setIsReady}: {
    stats: Stats
    setIsReady: (isReady: boolean) => void
}) {
    const {cpage} = useParams();
    const navigate = useNavigate();

    const [currentPage, setCurrentPage] = useState(0);
    const [itemPerPage, setItemPerPage] = useState(20);
    const [gameData, setGameData] = useState<GameDataBase[]>([]);

    useEffect(() => {
        const updateData = async () => {
            const response = await getDataFetcher().getLeaderBoardData(itemPerPage, Math.max(0, currentPage));

            if (response.isSuccess) {
                setGameData(response.data.results);
            } else if (!response.isServerDown && !response.isGameEnded) {
                navigate("/");
            } else if (!response.isSuccess && response.isServerDown && gameData.length === 0) {
                setIsReady(false);
            }
        }

        updateData();
        const interval = setInterval(updateData, 10_000);
        return () => {
            clearInterval(interval);
        };
    }, [currentPage, itemPerPage, setIsReady]);

    useEffect(() => {
        setCurrentPage(safeParseInt(cpage));
    }, [cpage]);

    return (
        <Grid gutter={"xl"}>
            <Grid.Col span={{base: 12, md: 6, lg: 3}}>
                <Title order={1} style={{textAlign: "center"}}>Parties en cours</Title>
                <MatchPane matches={stats.ongoingMatches}/>
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
                    setCurrentPage={(page) => navigate(`/board/${page}`)}
                    setItemPerPage={setItemPerPage}/>
            </Grid.Col>
            <Grid.Col span={{base: 12, md: 6, lg: 3}}>
                <Title order={1} style={{textAlign: "center"}}>Classement</Title>
                <Ranking rankingInfo={stats.rankingInfo}/>
            </Grid.Col>
        </Grid>
    )
}

export default MainPage;
