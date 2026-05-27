import axios from "axios";

const API_BASE_URL = "http://localhost:8000"; // will be replaced with env variable in production

export async function getEntries() {
  const response = await axios.get(`${API_BASE_URL}/entries?limit=10&skip=0`);
  return response.data;
}

export async function getWeeklyReport() {
  const response = await axios.get(`${API_BASE_URL}/entries/reports/weekly`);
  return response.data;
}

export async function getTagsSummary() {
  const response = await axios.get(`${API_BASE_URL}/entries/tags/summary`);
  return response.data;
}

export async function getCategoriesSummary() {
  const response = await axios.get(`${API_BASE_URL}/entries/categories/summary`);
  return response.data;
}

export async function createEntry(entry) {
  const response = await axios.post(`${API_BASE_URL}/entries`, entry);
  return response.data;
}

export async function updateEntry(entryId, entry) {
  const response = await axios.put(`${API_BASE_URL}/entries/${entryId}`, entry);
  return response.data;
}

export async function deleteEntry(entryId) {
  const response = await axios.delete(`${API_BASE_URL}/entries/${entryId}`);
  return response.data;
}