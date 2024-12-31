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

function Map({map}: { map: string[][] }) {
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

    return (
        <svg width={width * 20} height={height * 20}>
            {map.map((col, colIndex) =>
                col.map((cell, rowIndex) => (
                    <rect
                        key={`${rowIndex}-${colIndex}`}
                        x={colIndex * 20}
                        y={rowIndex * 20}
                        width={20}
                        height={20}
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
