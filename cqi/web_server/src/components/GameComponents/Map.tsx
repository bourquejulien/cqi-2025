import {GameMap, GameStep} from "../../interfaces/SuccessData.ts";

type ElementType = "unknown" | "background" | "wall" | "playerOffense" | "goal" | "visited" | "largeVision" | "timebomb" | "timebombSecondRound" | "timebombThirdRound";

interface ElementData {
    color: string;
    type: ElementType;
}

interface Position {
    x: number;
    y: number;
}

const HIDDEN_BACKGROUND_COLOR = "#e5e5e5";
const ELEMENT_MAPPING: { [id: string]: ElementData } = {
    "-2": {color: "#DFDFDF", type: "unknown"},
    "-1": {color: "#FFFFFF", type: "visited"},
    "0": {color: "#FFFFFF", type: "background"},
    "1": {color: "#000000", type: "wall"},
    "2": {color: "#FF0000", type: "playerOffense"},
    "3": {color: "#FFD700", type: "goal"},
    "4": {color: "#4CBB17", type: "largeVision"},
    "5": {color: "#0099CC", type: "timebomb"},
    "6": {color: "#006699", type: "timebombSecondRound"},
    "7": {color: "#003366", type: "timebombThirdRound"}
}

function getColor(key: string, isVisible: boolean): string {
    const data = ELEMENT_MAPPING[key];

    if (data !== undefined && data.type !== "background") {
        return data.color;
    }

    return isVisible ? ELEMENT_MAPPING["0"].color : HIDDEN_BACKGROUND_COLOR;
}

function getPlayerPosition(map: GameMap): Position | undefined {
    for (let x = 0; x < map.length; x++) {
        for (let y = 0; y < map[x].length; y++) {
            if (map[x][y].toString() === "2") {
                return {x, y};
            }
        }
    }

    return undefined
}

function isVisible(from: Position | undefined, to: Position | undefined, visionRadius: number): boolean {
    if (from === undefined || to === undefined) {
        return false;
    }
    return Math.abs(from.x - to.x) <= visionRadius && Math.abs(from.y - to.y) <= visionRadius;
}

function computeTileSize(mapWidth: number, mapHeight: number): number {
    const size = mapHeight > 1.5 * mapWidth ? Math.ceil(1.5 * mapWidth) : mapWidth;

    const MIN_TILE_SIZE = 5;
    const MAX_TILE_SIZE = 20;
    const MIN_SIZE = 30;
    const MAX_SIZE = 100;

    if (size <= MIN_SIZE) {
        return MAX_TILE_SIZE;
    }

    if (size > MAX_SIZE) {
        return MIN_TILE_SIZE;
    }

    return MAX_TILE_SIZE - Math.ceil(((MAX_TILE_SIZE - MIN_TILE_SIZE) / (MAX_SIZE - MIN_SIZE)) * (size - MIN_SIZE));
}

function floorTileSize(tileSize: number, mapWidth: number, maxWidth?: number): number {
    if (maxWidth === undefined || mapWidth * tileSize <= maxWidth) {
        return tileSize;
    }

    return Math.floor(maxWidth / mapWidth);
}

function Map({step, maxWidth, fixedSize}: { step: GameStep, maxWidth?: number, fixedSize?: boolean }) {
    const {map, score} = step;
    const mapWidth = map.length;
    if (mapWidth == 0) {
        return (
            <></>
        );
    }

    const mapHeight = map[0].length;
    if (mapHeight == 0) {
        return (
            <></>
        );
    }

    const playerPosition = getPlayerPosition(map);
    const tileSize = fixedSize ? 20 : floorTileSize(computeTileSize(mapWidth, mapHeight), mapWidth, maxWidth);

    return (
        <svg width={mapWidth * tileSize} height={mapHeight * tileSize} fill="none" xmlns="http://www.w3.org/2000/svg">
            {map.map((col, xPos) =>
                col.map((cell, yPos) => (
                    <rect
                        key={`${yPos}-${xPos}`}
                        x={xPos * tileSize}
                        y={yPos * tileSize}
                        width={tileSize}
                        height={tileSize}
                        fill={getColor(cell.toString(), isVisible(playerPosition, {x: xPos, y: yPos}, step.visionRadius))}
                        stroke="black"
                        strokeWidth={0.25}
                    />
                ))
            )}
            <text fontSize={25} x="0" y="25" fill="black">{score}</text>
        </svg>
    );
}

export default Map;
