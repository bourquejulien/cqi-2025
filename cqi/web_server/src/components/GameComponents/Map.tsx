type ElementType = "unknown" | "background" | "wall" | "playerOffense" | "goal" | "visited" | "largeVision";

interface ElementData {
    color: string;
    type: ElementType;
}

const ELEMENT_MAPPING: { [id: string]: ElementData } = {
    "-2": {color: "#DFDFDF", type: "unknown"},
    "-1": {color: "#FFFFFF", type: "visited"},
    "0": {color: "#FFFFFF", type: "background"},
    "1": {color: "#000000", type: "wall"},
    "2": {color: "#FF0000", type: "playerOffense"},
    "3": {color: "#FFD700", type: "goal"},
    "4": {color: "#4CBB17", type: "largeVision"}
}

function getColor(key: string): string {
    const data = ELEMENT_MAPPING[key];
    if (data === undefined) {
        return ELEMENT_MAPPING["-2"].color;
    }

    return data.color;
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

function Map({map, maxWidth, fixedSize}: { map: string[][], maxWidth?: number, fixedSize?: boolean }) {
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

    const tileSize = fixedSize ? 20 : floorTileSize(computeTileSize(mapWidth, mapHeight), mapWidth, maxWidth);

    return (
        <svg width={mapWidth * tileSize} height={mapHeight * tileSize} fill="none" xmlns="http://www.w3.org/2000/svg">
            {map.map((col, colIndex) =>
                col.map((cell, rowIndex) => (
                    <rect
                        key={`${rowIndex}-${colIndex}`}
                        x={colIndex * tileSize}
                        y={rowIndex * tileSize}
                        width={tileSize}
                        height={tileSize}
                        fill={getColor(cell)}
                        stroke="black"
                        strokeWidth={0.25}
                    />
                ))
            )}
        </svg>
    );
}

export default Map;
