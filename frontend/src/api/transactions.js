import client from "./client";

export async function fetchTransactions(params) {
  const response = await client.get("/transactions/", { params });
  return response.data;
}

export async function issueBook(payload) {
  const response = await client.post("/transactions/issue", payload);
  return response.data;
}

export async function returnBook(payload) {
  const response = await client.post("/transactions/return", payload);
  return response.data;
}
