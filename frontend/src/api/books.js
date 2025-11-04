import client from "./client";

export async function fetchBooks(params) {
  const response = await client.get("/books/", { params });
  return response.data;
}

export async function createBook(payload) {
  const response = await client.post("/books/", payload);
  return response.data;
}

export async function updateBook(id, payload) {
  const response = await client.put(`/books/${id}`, payload);
  return response.data;
}

export async function deleteBook(id) {
  await client.delete(`/books/${id}`);
}
