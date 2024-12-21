import {
    Grid,
    Image
} from '@mantine/core';
import TextBox from "../TextBlock/TextBlock.tsx";
import {Stats} from "../../interfaces/Stats.ts";
import {useEffect, useState} from "react";

function getCountdown(endingTime: Date): string {
    const gap = Math.max(0, endingTime.getTime() - new Date().getTime());

    const days = Math.floor(gap / (1000 * 60 * 60 * 24));
    const hours = Math.floor((gap % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((gap % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((gap % (1000 * 60)) / 1000);

    const format = `${hours}h ${minutes}m ${seconds}s`;
    return days > 0 ? `${days}j ${format}` : format;
}

function Header({stats}: { stats: Stats }) {
    const [totalMatchPlayed, setTotalMatchPlayed] = useState(stats.totalGames);
    const [endingTime, setEndingTime] = useState(stats.endTime);
    const [countdown, setCountdown] = useState(getCountdown(endingTime));

    useEffect(() => {
        const interval = setInterval(() => {
            setCountdown(getCountdown(endingTime));
        }, 1000);

        return () => clearInterval(interval);
    }, [endingTime]);

    useEffect(() => {
        setTotalMatchPlayed(stats?.totalGames ?? 0);
        setEndingTime(stats?.endTime ?? new Date());
    }, [stats]);

    return (
        <Grid align="center" gutter={{base: 5, xs: 'md', md: 'xl', xl: 50}}>
            <Grid.Col span={4}>
                <TextBox text={"Match joués:\n" + totalMatchPlayed}/>
            </Grid.Col>
            <Grid.Col span={4}>
                <Image src={"/logo_dark.png"} alt="Logo" w={"min(100%, 20rem)"} style={{margin: "auto"}}/>
            </Grid.Col>
            <Grid.Col span={4}>
                <TextBox text={countdown}/>
            </Grid.Col>
        </Grid>
    );
}

export default Header;
