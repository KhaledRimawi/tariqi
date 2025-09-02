export const formatAbsoluteTime = (dateString) => {
  if (!dateString) return "";
  const d = new Date(dateString);
  if (isNaN(d)) return "";
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

export const formatTimeAgo = (dateString) => {
  if (!dateString) return "";

  const past = new Date(dateString);
  if (isNaN(past)) return "";

  const now = new Date();
  const diffSec = Math.floor((now - past) / 1000);
  const rtf = new Intl.RelativeTimeFormat("ar", { numeric: "auto" });

  if (diffSec < 60) return rtf.format(-diffSec, "second");
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return rtf.format(-diffMin, "minute");
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return rtf.format(-diffHr, "hour");
  const diffDay = Math.floor(diffHr / 24);
  return rtf.format(-diffDay, "day");
};

export const formatCheckpointTime = (dateString) => {
  if (!dateString) return { absolute: "", relative: "" };
  return {
    absolute: formatAbsoluteTime(dateString),
    relative: formatTimeAgo(dateString),
  };
};
