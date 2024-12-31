import React from "react";

type ElementType = "unknown" | "background" | "wall" | "playerOffense" | "goal" | "visited";

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
    "3": {color: "#FFD700", type: "goal"}
}

function getColor(key: string): string {
    const data = ELEMENT_MAPPING[key];
    if (data === undefined) {
        return ELEMENT_MAPPING["-2"].color;
    }

    return data.color;
}

function computeTileSize(width: number, height: number): number {
    const size = height > 1.5 * width ? Math.ceil(1.5 * width) : width;

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

const Map = React.forwardRef<SVGSVGElement, { map: string[][] }>(({map}, ref) => {
    const width = map.length;
    if (width == 0) {
        return (
            <></>
        );
    }

    const height = map[0].length;
    if (height == 0) {
        return (
            <></>
        );
    }

    const tileSize = computeTileSize(width, height);

    return (
        <svg ref={ref} width={width * tileSize} height={height * tileSize} fill="none" xmlns="http://www.w3.org/2000/svg">
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
});

export default Map;
