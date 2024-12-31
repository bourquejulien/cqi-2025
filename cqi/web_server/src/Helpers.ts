export function formatDuration(startTime: Date, endTime: Date): string {
    const durationMs = endTime.getTime() - startTime.getTime();
    if (durationMs <= 0) {
        return "0s";
    }

    const duration = new Date(durationMs);
    const minutes = duration.getMinutes() > 0 ? `${duration.getMinutes()}m` : "";
    return minutes + `${duration.getSeconds()}s`;
}
