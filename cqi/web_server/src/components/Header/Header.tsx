import {
    Grid,
    Image
} from '@mantine/core';
import TextBox from "../TextBlock/TextBlock.tsx";


function Header() {
    return (
        <Grid gutter={{base: 5, xs: 'md', md: 'xl', xl: 50}}>
            <Grid.Col span={4}>
                <TextBox text={"0"}/>
            </Grid.Col>
            <Grid.Col span={4}>
                <Image src={"/logo.png"} alt="Logo" style={{height: '100%'}}/>
            </Grid.Col>

            <Grid.Col span={4}>
                <TextBox text={"0"}/>
            </Grid.Col>
        </Grid>
    );
}

export default Header;
