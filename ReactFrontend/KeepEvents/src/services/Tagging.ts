export async function tagImageWithBlip(file: File): Promise<string[]> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("http://localhost:8001/image-to-tags", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("BLIP tagging failed");
  }

  const data = await res.json();
  return data.tags ?? [];
}
