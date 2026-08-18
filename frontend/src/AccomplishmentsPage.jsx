import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";

import { getEntries } from "./api";
import "./AccomplishmentsPage.css";

const PAGE_SIZE = 10;

function AccomplishmentsPage() {
  const [entries, setEntries] = useState([]);
  const [page, setPage] = useState(1);
  const [totalEntries, setTotalEntries] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    let isMounted = true;

    async function loadPage() {
      setIsLoading(true);
      setError("");

      try {
        const data = await getEntries(PAGE_SIZE, (page - 1) * PAGE_SIZE);

        if (!isMounted) {
          return;
        }

        setEntries(data.entries ?? []);
        setTotalEntries(data.total_entries ?? 0);
      } catch (requestError) {
        if (requestError.response?.status === 401) {
          localStorage.removeItem("bragstack_token");
          window.location.assign("/login");
          return;
        }

        if (isMounted) {
          setError("BragStack could not load your accomplishments.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadPage();

    return () => {
      isMounted = false;
    };
  }, [page]);

  const totalPages = Math.max(1, Math.ceil(totalEntries / PAGE_SIZE));
  const startEntry = totalEntries === 0 ? 0 : (page - 1) * PAGE_SIZE + 1;
  const endEntry = Math.min(page * PAGE_SIZE, totalEntries);

  const visibleEntries = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    if (!query) {
      return entries;
    }

    return entries.filter((entry) => {
      const searchable = [
        entry.title,
        entry.category,
        entry.entry_type,
        entry.situation,
        entry.action,
        entry.impact,
        entry.lesson,
        ...(entry.tags ?? []),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return searchable.includes(query);
    });
  }, [entries, searchTerm]);

  const pageNumbers = useMemo(() => {
    const first = Math.max(1, page - 2);
    const last = Math.min(totalPages, first + 4);
    const adjustedFirst = Math.max(1, last - 4);

    return Array.from(
      { length: last - adjustedFirst + 1 },
      (_, index) => adjustedFirst + index
    );
  }, [page, totalPages]);

  function goToPage(nextPage) {
    const safePage = Math.min(Math.max(nextPage, 1), totalPages);
    setPage(safePage);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <main className="accomplishments-page">
      <header className="accomplishments-hero">
        <div>
          <p className="mini-label">Career Evidence Library</p>
          <h1>Your accomplishments</h1>
          <p>
            Browse the complete record of situations, actions, outcomes, skills,
            and public proof you have captured in BragStack.
          </p>
        </div>

        <a className="accomplishments-add" href="/app#entries">
          + Add accomplishment
        </a>
      </header>

      <section className="accomplishments-toolbar">
        <div className="accomplishments-search">
          <Search size={18} />
          <input
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Filter this page by skill, category, action, or impact..."
          />
        </div>

        <p>
          Showing <strong>{startEntry}–{endEntry}</strong> of{" "}
          <strong>{totalEntries}</strong> accomplishments
        </p>
      </section>

      {error && <div className="accomplishments-error">{error}</div>}

      {isLoading ? (
        <section className="accomplishments-empty">Loading accomplishments…</section>
      ) : visibleEntries.length === 0 ? (
        <section className="accomplishments-empty">
          <h2>No accomplishments found.</h2>
          <p>
            {searchTerm
              ? "Try a different search on this page."
              : "Add your first accomplishment from the Overview page."}
          </p>
        </section>
      ) : (
        <section className="accomplishments-list">
          {visibleEntries.map((entry) => (
            <article className="accomplishment-card" key={entry.id}>
              <div className="accomplishment-card-top">
                <div>
                  <p className="mini-label">
                    {entry.category} • {entry.entry_type} • {entry.entry_date}
                  </p>
                  <h2>{entry.title}</h2>
                </div>

                <span className={entry.is_public ? "proof-public" : "proof-private"}>
                  {entry.is_public ? "Public proof" : "Private proof"}
                </span>
              </div>

              <p className="accomplishment-bullet">{entry.resume_bullet}</p>

              <div className="accomplishment-proof-grid">
                <div>
                  <strong>Situation</strong>
                  <p>{entry.situation}</p>
                </div>
                <div>
                  <strong>Action</strong>
                  <p>{entry.action}</p>
                </div>
                <div>
                  <strong>Impact</strong>
                  <p>{entry.impact}</p>
                </div>
                {entry.lesson && (
                  <div>
                    <strong>Lesson</strong>
                    <p>{entry.lesson}</p>
                  </div>
                )}
              </div>

              <div className="accomplishment-tags">
                {entry.tags?.map((tag) => <span key={tag}>{tag}</span>)}
              </div>
            </article>
          ))}
        </section>
      )}

      {totalPages > 1 && (
        <nav className="pagination" aria-label="Accomplishments pages">
          <button
            type="button"
            onClick={() => goToPage(page - 1)}
            disabled={page === 1}
          >
            <ChevronLeft size={17} />
            Previous
          </button>

          <div className="pagination-pages">
            {pageNumbers.map((pageNumber) => (
              <button
                type="button"
                key={pageNumber}
                className={pageNumber === page ? "active" : ""}
                onClick={() => goToPage(pageNumber)}
              >
                {pageNumber}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={() => goToPage(page + 1)}
            disabled={page === totalPages}
          >
            Next
            <ChevronRight size={17} />
          </button>
        </nav>
      )}
    </main>
  );
}

export default AccomplishmentsPage;
