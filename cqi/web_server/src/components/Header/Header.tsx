import {
    Grid,
    Image
} from '@mantine/core';
import TextBox from "../TextBlock/TextBlock.tsx";
import {Stats} from "../../interfaces/Stats.ts";
import {useEffect, useState} from "react";

function getCountdown(endingTime: Date): string {
    const gap = endingTime - new Date().getTime();

    if (gap < 0) {
        return "";
    }

    const days = Math.floor(gap / (1000 * 60 * 60 * 24));
    const hours = Math.floor((gap % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((gap % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((gap % (1000 * 60)) / 1000);

    return `${days}d ${hours}h ${minutes}m ${seconds}s`;
}

function Header({stats}: { stats: Stats | undefined }) {
    const [totalMatchPlayed, setTotalMatchPlayed] = useState(0);
    const [endingTime, setEndingTime] = useState(new Date());
    const [countdown, setCountdown] = useState("");

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
        <Grid gutter={{base: 5, xs: 'md', md: 'xl', xl: 50}}>
            <Grid.Col span={4}>
                <TextBox text={"Total match played:\n" + totalMatchPlayed}/>
            </Grid.Col>
            <Grid.Col span={4}>
                <Image src={"/logo.png"} alt="Logo" style={{height: '100%'}}/>
            </Grid.Col>

            <Grid.Col span={4}>
                <TextBox text={countdown}/>
            </Grid.Col>
        </Grid>
    );
}

export default Header;
