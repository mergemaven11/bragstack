import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

function getPublicBragPath(slug, suffix = "") {
  const normalizedSlug = slug?.trim();

  if (!normalizedSlug) {
    return `/public/brag${suffix}`;
  }

  return `/public/brag/${encodeURIComponent(normalizedSlug)}${suffix}`;
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("bragstack_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export async function registerUser(user) {
  const response = await api.post("/auth/register", user);
  return response.data;
}

export async function loginUser(credentials) {
  const formData = new URLSearchParams();

  formData.append("username", credentials.email);
  formData.append("password", credentials.password);

  const response = await api.post("/auth/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get("/auth/me");
  return response.data;
}

export async function updateCurrentUserProfile(profile) {
  const response = await api.patch("/auth/me/profile", profile);
  return response.data;
}

export async function getPublicProfile(slug) {
  const response = await api.get(
    getPublicBragPath(slug, "/profile")
  );

  return response.data;
}

export async function getEntries() {
  const response = await api.get("/entries?limit=10&skip=0");
  return response.data;
}

export async function getWeeklyReport() {
  const response = await api.get("/entries/reports/weekly");
  return response.data;
}

export async function getTagsSummary() {
  const response = await api.get("/entries/tags/summary");
  return response.data;
}

export async function getCategoriesSummary() {
  const response = await api.get("/entries/categories/summary");
  return response.data;
}

export async function createEntry(entry) {
  const response = await api.post("/entries", entry);
  return response.data;
}

export async function updateEntry(entryId, entry) {
  const response = await api.put(`/entries/${entryId}`, entry);
  return response.data;
}

export async function deleteEntry(entryId) {
  const response = await api.delete(`/entries/${entryId}`);
  return response.data;
}

export async function getPublicEntries(slug) {
  const response = await api.get(getPublicBragPath(slug));
  return response.data;
}

export async function getPublicWeeklyReport(slug) {
  const response = await api.get(getPublicBragPath(slug, "/reports/weekly"));
  return response.data;
}

export async function getPublicTagsSummary(slug) {
  const response = await api.get(getPublicBragPath(slug, "/tags/summary"));
  return response.data;
}

export async function getPublicCategoriesSummary(slug) {
  const response = await api.get(getPublicBragPath(slug, "/categories/summary"));
  return response.data;
}
