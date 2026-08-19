import axios from "axios";

function getDefaultApiBaseUrl() {
  if (window.location.hostname.endsWith(".app.github.dev")) {
    return "/api";
  }

  return (
    import.meta.env.VITE_API_BASE_URL ||
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000"
  );
}

const api = axios.create({
  baseURL: getDefaultApiBaseUrl(),
});

function getPublicBragPath(slug, suffix = "") {
  const normalizedSlug = slug?.trim();

  if (!normalizedSlug) {
    return `/public/brag${suffix}`;
  }

  return `/public/brag/${encodeURIComponent(normalizedSlug)}${suffix}`;
}

function getPacketParams(startDate, endDate, options = {}) {
  return {
    ...(startDate && endDate
      ? {
          start_date: startDate,
          end_date: endDate,
        }
      : {}),
    ...(options.careerArea ? { career_area: options.careerArea } : {}),
    ...(options.roleTitle ? { role_title: options.roleTitle } : {}),
    ...(options.organization ? { organization: options.organization } : {}),
    ...(options.targetRole ? { target_role: options.targetRole } : {}),
    ...(options.targetLevel ? { target_level: options.targetLevel } : {}),
    ...(options.targetOrganization
      ? { target_organization: options.targetOrganization }
      : {}),
    ...(options.selectedEntryIds?.length
      ? { selected_entry_ids: options.selectedEntryIds.join(",") }
      : {}),
    ...(options.includeEvidenceReferences
      ? { include_evidence_references: true }
      : {}),
    ...(options.credentialName ? { credential_name: options.credentialName } : {}),
    ...(options.issuingBody ? { issuing_body: options.issuingBody } : {}),
    ...(options.reviewType ? { review_type: options.reviewType } : {}),
    ...(options.requirementNotes ? { requirement_notes: options.requirementNotes } : {}),
    confidential: options.confidential !== false,
  };
}

function parseDownloadFilename(contentDisposition, fallback) {
  const match = contentDisposition?.match(/filename="?([^";]+)"?/i);
  return match?.[1] || fallback;
}

async function downloadPacketPdf(path, packet, fallbackFilename) {
  const period = packet?.period ?? {};
  const context = packet?.context ?? {};
  const subject = packet?.subject ?? {};
  const target = packet?.target ?? {};
  const interviewPreferences = packet?.interview_preferences ?? {};
  const credentialReview = packet?.credential_review ?? {};
  const params = getPacketParams(period.start_date, period.end_date, {
    careerArea: context.career_area,
    roleTitle: subject.role,
    organization: context.organization,
    targetRole: target.role,
    targetLevel: target.level,
    targetOrganization: target.organization,
    selectedEntryIds: interviewPreferences.selected_entry_ids,
    includeEvidenceReferences:
      interviewPreferences.include_evidence_references === true,
    credentialName: credentialReview.credential_name,
    issuingBody: credentialReview.issuing_body,
    reviewType: credentialReview.review_type,
    requirementNotes: credentialReview.requirement_notes,
    confidential: packet?.confidential !== false,
  });

  const response = await api.get(path, {
    params,
    responseType: "blob",
  });

  return {
    blob: response.data,
    filename: parseDownloadFilename(
      response.headers["content-disposition"],
      fallbackFilename
    ),
  };
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
  const response = await api.get(getPublicBragPath(slug, "/profile"));
  return response.data;
}

export async function getEntries(limit = 10, skip = 0) {
  const response = await api.get("/entries", {
    params: { limit, skip },
  });
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

export async function getPublicEntries(slug, limit = 6, skip = 0) {
  const response = await api.get(getPublicBragPath(slug), {
    params: { limit, skip },
  });
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

export async function getImpactReceipts() {
  const response = await api.get("/impact-receipts?limit=20&skip=0");
  return response.data;
}

export async function createImpactReceiptFromEntry(entryId, payload) {
  const response = await api.post(`/impact-receipts/from-entry/${entryId}`, payload);
  return response.data;
}

export async function updateImpactReceipt(receiptId, payload) {
  const response = await api.patch(`/impact-receipts/${receiptId}`, payload);
  return response.data;
}

export async function getWeeklyCareerReport() {
  const response = await api.get("/reports/weekly");
  return response.data;
}

export async function getAllTimeCareerReport() {
  const response = await api.get("/reports/all-time");
  return response.data;
}

export async function getCustomCareerReport(startDate, endDate) {
  const response = await api.get("/reports/custom", {
    params: {
      start_date: startDate,
      end_date: endDate,
    },
  });
  return response.data;
}

export async function getPerformancePacket(startDate, endDate, options = {}) {
  const path =
    options.packetType === "promotion"
      ? "/packets/promotion"
      : options.packetType === "interview"
        ? "/packets/interview"
        : options.packetType === "certification"
          ? "/packets/certification"
          : "/packets/performance-review";
  const response = await api.get(path, {
    params: getPacketParams(startDate, endDate, options),
  });
  return response.data;
}

export async function getPromotionPacket(startDate, endDate, options = {}) {
  const response = await api.get("/packets/promotion", {
    params: getPacketParams(startDate, endDate, options),
  });
  return response.data;
}

export async function getInterviewPacket(startDate, endDate, options = {}) {
  const response = await api.get("/packets/interview", {
    params: getPacketParams(startDate, endDate, options),
  });
  return response.data;
}

export async function getCertificationPacket(startDate, endDate, options = {}) {
  const response = await api.get("/packets/certification", {
    params: getPacketParams(startDate, endDate, options),
  });
  return response.data;
}

export async function downloadPerformancePacketPdf(packet) {
  return downloadPacketPdf(
    "/packets/performance-review.pdf",
    packet,
    "bragstack-performance-review.pdf"
  );
}

export async function downloadPromotionPacketPdf(packet) {
  return downloadPacketPdf(
    "/packets/promotion.pdf",
    packet,
    "bragstack-promotion-packet.pdf"
  );
}

export async function downloadInterviewPacketPdf(packet) {
  return downloadPacketPdf(
    "/packets/interview.pdf",
    packet,
    "bragstack-interview-packet.pdf"
  );
}

export async function downloadCertificationPacketPdf(packet) {
  return downloadPacketPdf(
    "/packets/certification.pdf",
    packet,
    "bragstack-certification-licensure-packet.pdf"
  );
}

export async function getPublicImpactReceipts(slug) {
  const response = await api.get(getPublicBragPath(slug, "/impact-receipts"));
  return response.data;
}
