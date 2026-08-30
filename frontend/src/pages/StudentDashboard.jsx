import { useEffect, useState } from "react";
import api from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";
import TrustedCompanies from "../components/TrustedCompanies.jsx";

export default function StudentDashboard() {
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [applications, setApplications] = useState([]);
  const [query, setQuery] = useState("");
  const [message, setMessage] = useState("");

  const STATUS_BADGE = {
    applied: "bg-secondary",
    shortlisted: "bg-info text-dark",
    interview: "bg-warning text-dark",
    selected: "bg-success",
    rejected: "bg-danger",
  };

  async function loadPosts() {
    try {
      const res = await api.get("/students/posts", { params: { query } });
      setPosts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not load internships.");
    }
  }

  async function loadApplications() {
    try {
      const res = await api.get("/students/applications");
      setApplications(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not load applications.");
    }
  }

  useEffect(() => {
    loadPosts();
    loadApplications();
  }, []);

  async function apply(postId) {
    try {
      await api.post("/students/applications", { post_id: postId });
      setMessage("Application submitted.");
      loadApplications();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not apply.");
    }
  }

  return (
    <div>
      <h2 className="page-title">Welcome, {user.full_name}</h2>
      <p className="text-muted">Browse internships and track your applications.</p>
      {message && <div className="alert alert-info py-2">{message}</div>}

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="stat-card card">
            <div className="card-body">
              <div className="stat-num">{posts.length}</div>
              <div className="stat-label">Open internships</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card stat-2 card">
            <div className="card-body">
              <div className="stat-num">{applications.length}</div>
              <div className="stat-label">My applications</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card stat-3 card">
            <div className="card-body">
              <div className="stat-num">
                {applications.filter((a) => a.status === "selected").length}
              </div>
              <div className="stat-label">Selected</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row mb-4">
        <div className="col-md-4">
          <input
            className="form-control"
            placeholder="Search by title..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && loadPosts()}
          />
        </div>
        <div className="col-md-2">
          <button className="btn btn-outline-primary w-100" onClick={loadPosts}>
            Search
          </button>
        </div>
      </div>

      <div className="row">
        <div className="col-lg-7">
          <div className="section-head">
            <h5 className="mb-0 fw-bold">Open internships</h5>
          </div>
          {posts.length === 0 && (
            <div className="empty-state">No internships found. Try a different search.</div>
          )}
          {posts.map((p) => (
            <div className="card card-lift mb-3" key={p.id}>
              <div className="card-body">
                <div className="d-flex justify-content-between">
                  <h6 className="mb-1">{p.title}</h6>
                  <button className="btn btn-sm btn-primary" onClick={() => apply(p.id)}>
                    Apply
                  </button>
                </div>
                <div className="text-muted small mb-2">
                  {p.company_name} · {p.location} · {p.internship_type} · {p.duration} · {p.stipend}
                </div>
                <p className="small mb-2">{p.description}</p>
                <div>
                  {(p.skills ?? []).map((s) => (
                    <span className="badge skill-chip me-1" key={s}>
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="col-lg-5">
          <div className="section-head">
            <h5 className="mb-0 fw-bold">My applications</h5>
          </div>
          {applications.length === 0 && (
            <div className="empty-state">No applications yet — apply to your first internship.</div>
          )}
          <ul className="list-group">
            {applications.map((a) => (
              <li className="list-group-item d-flex justify-content-between" key={a.id}>
                <div>
                  <strong>{a.post_title}</strong> — {a.company_name}
                </div>
                <span
                  className={`badge ${STATUS_BADGE[a.status] ?? "bg-secondary"} align-self-center`}
                >
                  {a.status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <TrustedCompanies />
    </div>
  );
}
