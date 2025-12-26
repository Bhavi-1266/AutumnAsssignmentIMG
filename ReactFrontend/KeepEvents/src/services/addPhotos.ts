
interface PhotoDraft {
    file: File;
    photoDesc: string;
    extractedTags: string[];
}

export default async function addMany(photos: PhotoDraft[], eventId: number) {
//form  data send
  const formData = new FormData();

  photos.forEach((photo) => {
    formData.append("photoFile", photo.file);

    formData.append("photoDesc", photo.photoDesc ?? "");

    formData.append("event", String(eventId));

    // tags are JSON-stringified
    formData.append(
      "extractedTags",
      JSON.stringify(photo.extractedTags ?? [])
    );
  });

  console.log(formData);
  const response = await fetch("/api/photos/bulk-create/", {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json();
    throw new Error(err?.error || "Bulk upload failed");
  }

  return response.json();
}
