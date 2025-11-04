import client from "./client";

export async function fetchMembers(params) {
  const response = await client.get("/members/", { params });
  return response.data;
}

export async function createMember(payload) {
  const response = await client.post("/members/", payload);
  return response.data;
}

export async function updateMember(id, payload) {
  const response = await client.put(`/members/${id}`, payload);
  return response.data;
}

export async function deleteMember(id) {
  await client.delete(`/members/${id}`);
}
