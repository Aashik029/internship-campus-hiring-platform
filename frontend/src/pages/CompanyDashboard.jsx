import { useEffect, useState } from "react";
import api from "../api/client.js";
import { useAuth } from "../context/AuthContext.jsx";
import TrustedCompanies from "../components/TrustedCompanies.jsx";

const emptyForm = {
  title: "",
  description: "",
  location: "",
  internship_type: "",
  duration: "",
  stipend: "",
  skills: "",
};

export default function CompanyDashboard() {
  const { user } = useAuth();
  const [form, setForm] = useState(emptyForm);
  const [posts, setPosts] = useState([]);
  const [message, setMessage] = useState("");
  const [applicants, setApplicants] = useState({});
  const [posting, setPosting] = useState(false);
  const [updatingId, setUpdatingId] = useState(null);

  async function loadPosts() {
    try {
      const res = await api.get("/companies/posts");
      setPosts(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not load internships.");
    }
  }

  async function toggleOpen(post) {
    try {
      await api.patch(`/companies/posts/${post.id}`, { is_open: !post.is_open });
      setMessage(post.is_open ? "Internship closed." : "Internship reopened.");
      loadPosts();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not update internship.");
    }
  }

  async function loadApplicants(postId) {
    if (applicants[postId] !== undefined) {
      setApplicants((prev) => {
        const next = { ...prev };
        delete next[postId];
        return next;
      });
      return;
    }

    setApplicants((prev) => ({ ...prev, [postId]: "loading" }));
    try {
      const res = await api.get(`/companies/posts/${postId}/applicants`);
      setApplicants((prev) => ({ ...prev, [postId]: res.data }));
    } catch (err) {
      setApplicants((prev) => {
        const next = { ...prev };
        delete next[postId];
        return next;
      });
      setMessage(err.response?.data?.detail || "Could not load applicants.");
    }
  }

  useEffect(() => {
    loadPosts();
  }, []);

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value });
  }

  async function createPost(e) {
    e.preventDefault();
    if (posting) return;
    const payload = {
      ...form,
      skills: form.skills
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    };
    setPosting(true);
    try {
      await api.post("/companies/posts", payload);
      setForm(emptyForm);
      setMessage("Internship posted successfully.");
      loadPosts();
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not post the internship.");
    } finally {
      setPosting(false);
    }
  }

  async function updateStatus(postId, applicationId, status) {
    if (updatingId !== null) return;
    setUpdatingId(applicationId);
    try {
      const res = await api.patch(`/companies/applications/${applicationId}/status`, { status });
      // Merge the updated status locally — avoids a second round trip.
      setApplicants((prev) => {
        const list = prev[postId];
        if (!Array.isArray(list)) return prev;
        return {
          ...prev,
          [postId]: list.map((a) => (a.id === applicationId ? { ...a, status: res.data.status } : a)),
        };
      });
      setMessage("Applicant status updated.");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not update status.");
    } finally {
      setUpdatingId(null);
    }
  }

  return (
    <div>
      <h2 className="page-title">Welcome, {user.full_name}</h2>
      <p className="text-muted">Post internships and manage applicants.</p>
      {message && <div className="alert alert-info py-2">{message}</div>}

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="stat-card card">
            <div className="card-body">
              <div className="stat-num">{posts.length}</div>
              <div className="stat-label">Total postings</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card stat-2 card">
            <div className="card-body">
              <div className="stat-num">{posts.filter((p) => p.is_open).length}</div>
              <div className="stat-label">Open now</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="stat-card stat-3 card">
            <div className="card-body">
              <div className="stat-num">
                {Object.values(applicants).reduce(
                  (n, v) => n + (Array.isArray(v) ? v.length : 0),
                  0,
                )}
              </div>
              <div className="stat-label">Applicants loaded</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-lg-4">
          <div className="card shadow-sm mb-4">
            <div className="auth-band">
              <h4>Post an internship</h4>
              <p>Reach students with the right skills.</p>
            </div>
            <div className="card-body">
              <form onSubmit={createPost}>
                <div className="mb-2">
                  <input
                    className="form-control"
                    placeholder="Title"
                    value={form.title}
                    onChange={update("title")}
                    required
                  />
                </div>
                <div className="mb-2">
                  <textarea
                    className="form-control"
                    rows="3"
                    placeholder="Description"
                    value={form.description}
                    onChange={update("description")}
                    required
                  />
                </div>
                <div className="mb-2">
                  <input
                    className="form-control"
                    placeholder="Location"
                    value={form.location}
                    onChange={update("location")}
                  />
                </div>
                <div className="mb-2">
                  <input
                    className="form-control"
                    placeholder="Type (e.g. Remote, On-site)"
                    value={form.internship_type}
                    onChange={update("internship_type")}
                  />
                </div>
                <div className="mb-2">
                  <input
                    className="form-control"
                    placeholder="Duration (e.g. 3 months)"
                    value={form.duration}
                    onChange={update("duration")}
                  />
                </div>
                <div className="mb-2">
                  <input
                    className="form-control"
                    placeholder="Stipend (e.g. Rs. 15,000/mo)"
                    value={form.stipend}
                    onChange={update("stipend")}
                  />
                </div>
                <div className="mb-3">
                  <input
                    className="form-control"
                    placeholder="Skills (comma separated)"
                    value={form.skills}
                    onChange={update("skills")}
                  />
                </div>
                <button className="btn btn-primary w-100" disabled={posting}>
                  {posting ? "Posting…" : "Post internship"}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <div className="section-head">
            <h5 className="mb-0 fw-bold">My internships</h5>
          </div>
          {posts.length === 0 && (
            <div className="empty-state">
              No internships posted yet — use the form to publish your first role.
            </div>
          )}
          {posts.map((p) => (
            <div className="card card-lift mb-3" key={p.id}>
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <h6 className="mb-0">
                    {p.title}{" "}
                    <span className={`badge ${p.is_open ? "bg-success" : "bg-secondary"}`}>
                      {p.is_open ? "Open" : "Closed"}
                    </span>
                  </h6>
                  <div className="d-flex gap-2">
                    <button className="btn btn-sm btn-outline-secondary" onClick={() => loadApplicants(p.id)}>
                      View applicants
                    </button>
                    <button
                      className={`btn btn-sm ${p.is_open ? "btn-outline-danger" : "btn-outline-success"}`}
                      onClick={() => toggleOpen(p)}
                    >
                      {p.is_open ? "Close" : "Reopen"}
                    </button>
                  </div>
                </div>
                <p className="small text-muted mb-2">
                  {p.location} · {p.internship_type} · {p.duration} · {p.stipend}
                </p>
                <p className="small mb-2">{p.description}</p>
                <div className="mb-2">
                  {p.skills.map((s) => (
                    <span className="badge skill-chip me-1" key={s}>
                      {s}
                    </span>
                  ))}
                </div>
                {applicants[p.id] === "loading" ? (
                  <p className="text-muted small mb-0">Loading applicants...</p>
                ) : (
                  Array.isArray(applicants[p.id]) && (
                    applicants[p.id].length === 0 ? (
                      <p className="text-muted small mb-0">No applicants yet.</p>
                    ) : (
                      <ul className="list-group">
                        {applicants[p.id].map((a) => (
                          <li className="list-group-item" key={a.id}>
                            <div className="d-flex justify-content-between align-items-center">
                              <div>
                                <strong>{a.student_name}</strong> ({a.email})
                                <div className="text-muted small">{a.cover_note || "No cover note"}</div>
                              </div>
                              <select
                                className="form-select form-select-sm w-auto"
                                defaultValue={a.status}
                                disabled={updatingId !== null}
                                onChange={(e) => updateStatus(p.id, a.id, e.target.value)}
                              >
                                <option value="applied">Applied</option>
                                <option value="shortlisted">Shortlisted</option>
                                <option value="interview">Interview</option>
                                <option value="selected">Selected</option>
                                <option value="rejected">Rejected</option>
                              </select>
                              {updatingId === a.id && (
                                <span className="text-muted small ms-2">Updating…</span>
                              )}
                            </div>
                          </li>
                        ))}
                      </ul>
                    )
                  )
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      <TrustedCompanies />
    </div>
  );
}
