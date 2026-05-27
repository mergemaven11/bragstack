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