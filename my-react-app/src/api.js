export async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    cache: "no-store",
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.toLowerCase().includes("application/json")) {
    const detail = response.headers.get("server") || "the backend";
    throw new Error(
      `The API returned a non-JSON response (${response.status} from ${detail}). ` +
        "Check the Flask backend terminal for the underlying error.",
    );
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.Error || `Request failed (${response.status}).`);
  }
  return data;
}
