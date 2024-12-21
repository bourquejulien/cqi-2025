import {Group, Stack, Table, Text} from "@mantine/core";
import {JSX} from "react";
import {getPlayerService} from "../../Data.ts";
import {RankingInfo, RankResult} from "../../interfaces/Stats.ts";

function compare(a: RankResult, b: RankResult): number {
    const result = (b.totalWins / Math.max(b.totalGames, 1)) - (a.totalWins / Math.max(a.totalGames, 1));

    if (result != 0) {
        return result;
    }

    return a.teamId.localeCompare(b.teamId);
}

function getRows(results: RankResult[]): JSX.Element[] {
    const playerService = getPlayerService();

    return results.slice().sort(compare).map((rankResult) => {
        return (
            <Table.Tr key={rankResult.teamId}>
                <Table.Td style={{textAlign: "center"}}><Text>{playerService.getPlayerNameOrDefault(rankResult.teamId)}</Text></Table.Td>
                <Table.Td style={{textAlign: "center"}}>
                    <Group wrap={"nowrap"}>
                        <Text c={"green.7"}>{rankResult.totalWins}</Text>
                        <Text>|</Text>
                        <Text c={"gray.7"}>{rankResult.totalDraws}</Text>
                        <Text>|</Text>
                        <Text c={"red.7"}>{rankResult.totalLosses}</Text>
                    </Group>
                </Table.Td>
            </Table.Tr>
        )
    });
}

function Ranking({rankingInfo}: { rankingInfo: RankingInfo }) {
    return (
        <Stack
            mih={300}
            bg="var(--mantine-color-body)"
            align="center"
            justify="flex-start"
            style={{textAlign: "center"}}
            gap="lg"
        >
            <Table>
                <Table.Thead>
                    <Table.Tr>
                        <Table.Th style={{textAlign: "center"}}>Équipe</Table.Th>
                        <Table.Th style={{textAlign: "center"}}>Résultats <br/> [ ✅ | 🟰 | ❌ ]</Table.Th>
                    </Table.Tr>
                </Table.Thead>
                <Table.Tbody>{getRows(rankingInfo.results)}</Table.Tbody>
            </Table>
        </Stack>
    );
}

export default Ranking;
