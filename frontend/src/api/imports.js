import client from "./client";

export async function importBooks(payload) {
  const response = await client.post("/imports/books", payload);
  return response.data;
}
