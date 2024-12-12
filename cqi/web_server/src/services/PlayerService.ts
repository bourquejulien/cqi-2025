export class PlayerService {
    mapping: Map<string, string> = new Map<string, string>();

    setMapping(mapping: { [key: string]: string }) {
        for (const key in mapping) {
            this.mapping.set(key, mapping[key]);
        }
    }

    getPlayerName(playerId: string): string | undefined {
        return this.mapping.get(playerId)
    }

    getPlayerNameOrDefault(playerId: string): string {
        return this.getPlayerName(playerId) ?? playerId;
    }
}
