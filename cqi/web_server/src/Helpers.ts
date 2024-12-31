import {BlobWriter, TextReader, ZipWriter} from "@zip.js/zip.js";

export function formatDuration(startTime: Date, endTime: Date): string {
    const durationMs = endTime.getTime() - startTime.getTime();
    if (durationMs <= 0) {
        return "0s";
    }

    const duration = new Date(durationMs);
    const minutes = duration.getMinutes() > 0 ? `${duration.getMinutes()}m` : "";
    return minutes + `${duration.getSeconds()}s`;
}

export async function generateZip(data: [string, string][]) {
    const zipFileWriter = new BlobWriter();
    const zipWriter = new ZipWriter(zipFileWriter);

    for (const [filename, content] of data) {
        const reader = new TextReader(content);
        await zipWriter.add(filename, reader);
    }

    await zipWriter.close();
    return await zipFileWriter.getData();
}

export function downloadBlob(blob: Blob, filename: string) {
    const objectUrl = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = objectUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => URL.revokeObjectURL(objectUrl), 5000);
}
